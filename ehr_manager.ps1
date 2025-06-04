# EHR System Manager Script
param (
    [ValidateSet('start', 'stop', 'restart', 'status', 'fix')]
    [string]$Command = 'start',
    
    [switch]$ElevateIfNeeded
)

$ErrorActionPreference = "Stop"

# Check if running as administrator
function Test-Administrator {
    $user = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($user)
    $adminRole = [Security.Principal.WindowsBuiltInRole]::Administrator
    return $principal.IsInRole($adminRole)
}

# If not running as admin and ElevateIfNeeded is specified, restart script with elevation
if (-not (Test-Administrator) -and $ElevateIfNeeded) {
    Write-Host "Restarting script with administrative privileges..." -ForegroundColor Yellow
    $arguments = "-File `"$($MyInvocation.MyCommand.Path)`" $Command"
    Start-Process powershell -ArgumentList $arguments -Verb RunAs
    exit
}

# Warn if not running as admin
if (-not (Test-Administrator)) {
    Write-Host "`nWARNING: This script is not running with administrative privileges." -ForegroundColor Yellow
    Write-Host "Some operations like killing processes may fail. Run with -ElevateIfNeeded to auto-elevate.`n" -ForegroundColor Yellow
}

# Constants
$SCRIPT_VERSION = "1.0.0"
$PORTS = @(8000, 8004, 8081)  # Updated to use correct ports
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$BACKEND_DIR = Join-Path -Path $SCRIPT_DIR -ChildPath "backend"
$API_DIR = Join-Path -Path $BACKEND_DIR -ChildPath "api"

$SERVICES = @(
    @{
        Name = "Main API"; 
        Port = 8000; 
        Command = "python start_apis.py"; 
        WorkDir = $BACKEND_DIR;
        TestUrl = "http://localhost:8000/api/health";
        RequiredForNext = $true;  # This service must be running before starting next
        StartupTimeout = 30;  # Seconds to wait for startup
    },
    @{
        Name = "Vaccine API"; 
        Port = 8004; 
        Command = "python start_vaccine_server.py";
        WorkDir = $BACKEND_DIR;
        TestUrl = "http://localhost:8004/api/health";
        RequiredForNext = $true;
        StartupTimeout = 30;
    },
    @{
        Name = "Frontend"; 
        Port = 8081; 
        Command = "cmd.exe /c npm run dev -- --port 8081 --force";
        WorkDir = Join-Path -Path $SCRIPT_DIR -ChildPath "ehr-vue-app";
        TestUrl = "http://localhost:8081/";
        RequiredForNext = $false;
        StartupTimeout = 60;
    }
)

# Helper Functions
function Write-Header {
    param([string]$Message)
    Write-Host "`n==== $Message ====`n" -ForegroundColor Cyan
}

function KillProcessOnPort {
    param([int]$Port)
    
    try {
        $maxAttempts = 5  # Increased from 3
        for ($attempt = 1; $attempt -le $maxAttempts; $attempt++) {
            $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
            $processes = $connections | Where-Object State -eq 'Listen' | Select-Object -ExpandProperty OwningProcess -Unique
            
            if (-not $processes) {
                Write-Host "  Port $Port is free" -ForegroundColor Green
                return $true
            }
            
            # More aggressive with each attempt
            foreach ($process in $processes) {
                $processInfo = Get-Process -Id $process -ErrorAction SilentlyContinue
                if ($processInfo) {
                    if ($attempt -lt 3) {
                        # First try politely
                        Write-Host "  Killing process on port $Port (PID: $process, $($processInfo.ProcessName)) - Attempt $attempt/$maxAttempts" -ForegroundColor Yellow
                        Stop-Process -Id $process -Force -ErrorAction SilentlyContinue
                    } else {
                        # Then get aggressive
                        Write-Host "  Force killing process on port $Port (PID: $process, $($processInfo.ProcessName)) with taskkill - Attempt $attempt/$maxAttempts" -ForegroundColor Red
                        try {
                            & taskkill /F /PID $process /T | Out-Null
                        } catch {
                            # Ignore errors, we'll check if it worked afterward
                        }
                    }
                    Start-Sleep -Seconds 2
                }
            }
            
            # Check if port is really free
            Start-Sleep -Seconds 2  # Increased wait time
            $stillInUse = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
            if (-not $stillInUse) {
                Write-Host "  Port $Port is now free" -ForegroundColor Green
                return $true
            }
            
            if ($attempt -lt $maxAttempts) {
                Write-Host "  Port $Port is still in use, retrying..." -ForegroundColor Yellow
                Start-Sleep -Seconds 3
            }
        }
        
        # Last resort - try to find any Python process and kill it
        if ($Port -eq 8000 -or $Port -eq 8004) {
            Write-Host "  Attempting to kill all Python processes as last resort..." -ForegroundColor Red
            Get-Process -Name python -ErrorAction SilentlyContinue | ForEach-Object {
                Write-Host "  Force killing Python process: $($_.Id)" -ForegroundColor Red
                Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
            }
            
            Start-Sleep -Seconds 5
            $stillInUse = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
            if (-not $stillInUse) {
                Write-Host "  Port $Port is now free after last resort" -ForegroundColor Green
                return $true
            }
        }
        
        Write-Host "  Failed to free port $Port after all attempts" -ForegroundColor Red
        return $false
    } catch {
        $errorMessage = $_.Exception.Message -replace ':', ''  # Remove colons from error message
        Write-Host "  Error killing process on port $Port - $errorMessage" -ForegroundColor Red
        return $false
    }
}

function TestEndpoint {
    param(
        [string]$Url,
        [int]$TimeoutSec = 10,  # Increased default timeout
        [int]$MaxRetries = 3,
        [int]$RetryDelaySec = 5  # Increased retry delay
    )
    
    for ($i = 0; $i -lt $MaxRetries; $i++) {
        try {
            Write-Host "    Attempting to connect to $Url (Attempt $($i + 1)/$MaxRetries)..." -ForegroundColor Gray
            $ProgressPreference = 'SilentlyContinue'  # Suppress progress bar
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec $TimeoutSec -ErrorAction Stop
            $ProgressPreference = 'Continue'
            Write-Host "    Connection successful!" -ForegroundColor Green
            return $true
        } catch {
            Write-Host "    Connection failed: $($_.Exception.Message)" -ForegroundColor Yellow
            if ($i -lt $MaxRetries - 1) {
                Write-Host "    Waiting $RetryDelaySec seconds before retry..." -ForegroundColor Gray
                Start-Sleep -Seconds $RetryDelaySec
            }
        }
    }
    
    Write-Host "    Service failed to respond after $MaxRetries attempts" -ForegroundColor Red
    return $false
}

function StartService {
    param(
        [hashtable]$Service
    )
    
    Write-Host "`nStarting $($Service.Name) on port $($Service.Port)..."
    
    # First ensure the port is free
    $maxPortAttempts = 3
    $portFreed = $false
    
    for ($attempt = 1; $attempt -le $maxPortAttempts; $attempt++) {
        $portFreed = KillProcessOnPort -Port $Service.Port
        if ($portFreed) {
            break
        }
        if ($attempt -lt $maxPortAttempts) {
            Write-Host "  Retrying to free port $($Service.Port) in 5 seconds..." -ForegroundColor Yellow
            Start-Sleep -Seconds 5
        }
    }
    
    if (-not $portFreed) {
        Write-Host "  Failed to free port $($Service.Port) after $maxPortAttempts attempts" -ForegroundColor Red
        return $null
    }
    
    try {
        # Special handling for Frontend
        if ($Service.Name -eq "Frontend") {
            Push-Location $($Service.WorkDir)
            Write-Host "  Installing frontend dependencies..." -ForegroundColor Yellow
            & npm install --legacy-peer-deps
            Pop-Location
        }
        
        $processStartInfo = New-Object System.Diagnostics.ProcessStartInfo
        $processStartInfo.FileName = "powershell"
        $processStartInfo.Arguments = "-Command `"Set-Location '$($Service.WorkDir)'; $($Service.Command)`""
        $processStartInfo.UseShellExecute = $true
        
        $process = [System.Diagnostics.Process]::Start($processStartInfo)
        Write-Host "  Process started (PID: $($process.Id))" -ForegroundColor Green
        
        # Wait for service to be ready
        Write-Host "  Waiting up to $($Service.StartupTimeout) seconds for service to be ready..."
        $startTime = Get-Date
        $timeout = New-TimeSpan -Seconds $Service.StartupTimeout
        $healthCheckInterval = 5  # Check every 5 seconds
        
        while ((Get-Date) - $startTime -lt $timeout) {
            if (TestEndpoint -Url $Service.TestUrl -TimeoutSec 10 -MaxRetries 2) {
                Write-Host "  Service is ready!" -ForegroundColor Green
                return $process.Id
            }
            Start-Sleep -Seconds $healthCheckInterval
        }
        
        if ($Service.RequiredForNext) {
            Write-Host "  Service failed to start in time and is required for other services" -ForegroundColor Red
            throw "Service startup timeout"
        } else {
            Write-Host "  Service not responding yet, but continuing as it's not required for other services" -ForegroundColor Yellow
            return $process.Id
        }
    } catch {
        Write-Host "  Failed to start service: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

function CheckStatus {
    $results = @()
    
    foreach ($service in $SERVICES) {
        $processId = Get-NetTCPConnection -LocalPort $service.Port -State Listen -ErrorAction SilentlyContinue | 
                     Select-Object -ExpandProperty OwningProcess -ErrorAction SilentlyContinue
        
        if ($processId) {
            $processInfo = Get-Process -Id $processId -ErrorAction SilentlyContinue
            $processName = if ($processInfo) { $processInfo.ProcessName } else { "Unknown" }
            $isResponding = TestEndpoint -Url $service.TestUrl -MaxRetries 2
            $status = if ($isResponding) { "Online" } else { "Running but not responding" }
            
            $results += [PSCustomObject]@{
                Name = $service.Name
                Port = $service.Port
                Status = $status
                Process = $processName
                PID = $processId
            }
        } else {
            $results += [PSCustomObject]@{
                Name = $service.Name
                Port = $service.Port
                Status = "Offline"
                Process = ""
                PID = ""
            }
        }
    }
    
    return $results
}

# Commands
function StartSystem {
    Write-Header "Starting EHR System v$SCRIPT_VERSION"
    
    # Kill any existing processes on our ports
    Write-Host "Ensuring ports are free..."
    foreach ($port in $PORTS) {
        KillProcessOnPort -Port $port
    }
    
    # Initialize database
    Write-Host "`nChecking database status..." -ForegroundColor Cyan
    try {
        Push-Location $BACKEND_DIR
        python -c "from setup_database import initialize_database; initialize_database()"
        $dbInitResult = $?
        Pop-Location
        
        if ($dbInitResult) {
            Write-Host "  Database initialization successful!" -ForegroundColor Green
        } else {
            throw "Database initialization returned failure"
        }
    } catch {
        Write-Host "  Database initialization failed: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "  Cannot continue without database. Please check PostgreSQL is running." -ForegroundColor Red
        return
    }
    
    # Start each service
    $startedServices = @()
    foreach ($service in $SERVICES) {
        $processId = StartService -Service $service
        if ($null -eq $processId) {
            if ($service.RequiredForNext) {
                Write-Host "`nCritical service $($service.Name) failed to start. Stopping all services..." -ForegroundColor Red
                foreach ($startedService in $startedServices) {
                    KillProcessOnPort -Port $startedService.Port
                }
                return
            }
        } else {
            $startedServices += $service
        }
    }
    
    # Show final status
    Write-Host "`nFinal Service Status:"
    $status = CheckStatus
    $status | Format-Table -AutoSize
    
    # Verify all required services are running
    $criticalFailure = $false
    foreach ($service in $SERVICES | Where-Object { $_.RequiredForNext }) {
        $serviceStatus = $status | Where-Object { $_.Name -eq $service.Name }
        if ($serviceStatus.Status -ne "Online") {
            Write-Host "Critical service $($service.Name) is not running properly!" -ForegroundColor Red
            $criticalFailure = $true
        }
    }
    
    if ($criticalFailure) {
        Write-Host "`nOne or more critical services failed to start properly. Please check the logs and try again." -ForegroundColor Red
    } else {
        Write-Host "`nEHR System started successfully!" -ForegroundColor Green
        Write-Host "  Main API: http://localhost:8000"
        Write-Host "  Vaccine API: http://localhost:8004"
        Write-Host "  Frontend: http://localhost:8081"
    }
}

# Main execution
switch ($Command) {
    'start' { StartSystem }
    'stop' { 
        Write-Header "Stopping EHR System"
        foreach ($port in $PORTS) {
            KillProcessOnPort -Port $port
        }
    }
    'restart' {
        Write-Header "Restarting EHR System"
        foreach ($port in $PORTS) {
            KillProcessOnPort -Port $port
        }
        Start-Sleep -Seconds 2
        StartSystem
    }
    'status' {
        Write-Header "EHR System Status"
        $status = CheckStatus
        $status | Format-Table -AutoSize
    }
    'fix' {
        Write-Header "Running System Fixes"
        foreach ($port in $PORTS) {
            KillProcessOnPort -Port $port
        }
        StartSystem
    }
} 