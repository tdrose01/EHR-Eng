# EHR System Master Management Script
param (
    [Parameter(Mandatory=$false)]
    [ValidateSet('start', 'stop', 'restart', 'status', 'check', 'fix')]
    [string]$Command = 'start',
    
    [switch]$Debug = $false
)

$ErrorActionPreference = "Stop"
$SCRIPT_VERSION = "1.0.0"

# Configuration
$CONFIG = @{
    Services = @(
        @{
            Name = "Login API"
            Port = 8001
            StartCommand = "python -m api.login_api"
            WorkingDir = "backend"
            Endpoint = "http://localhost:8001/api/health"
            Required = $true
        },
        @{
            Name = "Patient API"
            Port = 8002
            StartCommand = "python start_apis.py" 
            WorkingDir = "backend"
            Endpoint = "http://localhost:8002/api/patients?limit=1"
            Required = $true
        },
        @{
            Name = "Records API"
            Port = 8003
            StartCommand = "python -c `"import os; os.environ['PORT'] = '8003'; from api.records_api import app; app.run(host='0.0.0.0', port=8003)`""
            WorkingDir = "backend"
            Endpoint = "http://localhost:8003/api/records"
            Required = $false  # Optional until we fix it
            FixCommand = "powershell -Command `"(Get-Content api/records_api.py) -replace '            # Convert query result to dictionary', '        # Convert query result to dictionary' -replace '            column_names = \[desc\[0\] for desc in cursor.description\]', '        column_names = [desc[0] for desc in cursor.description]' -replace '            record = dict\(zip\(column_names, cursor.fetchone\(\)\)\)', '        record = dict(zip(column_names, cursor.fetchone()))' | Set-Content api/records_api.py`""
            FixWorkingDir = "backend"
        },
        @{
            Name = "Vaccine API"
            Port = 8004
            StartCommand = "python start_vaccine_server.py"
            WorkingDir = "backend"
            Endpoint = "http://localhost:8004/api/vaccines"
            Required = $false  # Not critical because of 404s
        },
        @{
            Name = "Frontend"
            Port = 8081
            StartCommand = "cmd.exe /c npm run dev -- --port 8081 --force"
            WorkingDir = "ehr-vue-app"
            Endpoint = "http://localhost:8081/"
            Required = $true
        }
    )
    EnvConfig = @{
        'Frontend' = @{
            Path = "ehr-vue-app/.env"
            Settings = @{
                'VITE_API_BASE_URL' = "http://localhost:8081/api"
                'VITE_PATIENT_API_URL' = "http://localhost:8002/api"
                'VITE_AUTH_API_URL' = "http://localhost:8001/api"
                'VITE_RECORDS_API_URL' = "http://localhost:8003/api"
                'VITE_VACCINE_API_URL' = "http://localhost:8004/api"
                'VITE_ENABLE_MOCK_DATA' = "false"
                'VITE_ENABLE_TEST_LOGIN' = "true"
            }
        }
    }
    ViteConfig = @{
        Path = "ehr-vue-app/vite.config.js"
        RequiredSettings = @{
            'port' = 8081
            'strictPort' = $true
        }
    }
}

$Global:Processes = @()

# Helper Functions
function Write-Title {
    param (
        [string]$Message
    )
    
    Write-Host "`n$('=' * 50)" -ForegroundColor Blue
    Write-Host "  $Message" -ForegroundColor Blue
    Write-Host "$('=' * 50)" -ForegroundColor Blue
}

function Write-Step {
    param (
        [string]$Message
    )
    
    Write-Host "`n• $Message" -ForegroundColor Cyan
}

function Write-Success {
    param (
        [string]$Message
    )
    
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Warning {
    param (
        [string]$Message
    )
    
    Write-Host "! $Message" -ForegroundColor Yellow
}

function Write-Error {
    param (
        [string]$Message
    )
    
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Debug {
    param (
        [string]$Message
    )
    
    if ($Debug) {
        Write-Host "[DEBUG] $Message" -ForegroundColor Magenta
    }
}

function Test-Endpoint {
    param (
        [string]$Name,
        [string]$Url,
        [int]$TimeoutSec = 5
    )
    
    Write-Debug "Testing $Name API at $Url..."
    
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec $TimeoutSec -ErrorAction Stop
        
        if ($response.StatusCode -eq 200) {
            Write-Debug "  Endpoint is responsive"
            return $true
        } else {
            Write-Debug "  Endpoint responded with status: $($response.StatusCode)"
            return $false
        }
    } 
    catch [System.Net.WebException] {
        if ($_.Exception.Response -ne $null) {
            $statusCode = [int]$_.Exception.Response.StatusCode
            Write-Debug "  Endpoint responded with error: $statusCode"
            if ($statusCode -eq 404) {
                # For this application, consider 404 as "service running but endpoint not found"
                Write-Debug "  Service is running but endpoint not found (404)"
                return $false
            }
        }
        else {
            Write-Debug "  Endpoint not reachable: $($_.Exception.Message)"
        }
        return $false
    }
    catch {
        Write-Debug "  Unexpected error: $($_.Exception.Message)"
        return $false
    }
}

function Get-ProcessOnPort {
    param (
        [int]$Port
    )
    
    try {
        $process = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | 
            Select-Object -ExpandProperty OwningProcess -ErrorAction SilentlyContinue
            
        if ($process) {
            return $process
        }
    }
    catch {
        Write-Debug "Error checking process on port $Port : $($_.Exception.Message)"
    }
    
    return $null
}

function Stop-ProcessOnPort {
    param (
        [int]$Port,
        [string]$ServiceName
    )
    
    $process = Get-ProcessOnPort -Port $Port
    
    if ($process) {
        $processInfo = Get-Process -Id $process -ErrorAction SilentlyContinue
        if ($processInfo) {
            Write-Host "  Stopping $ServiceName on port $Port (PID: $process, $($processInfo.ProcessName))" -ForegroundColor Yellow
            
            try {
                Stop-Process -Id $process -Force -ErrorAction Stop
                Start-Sleep -Seconds 1  # Give it a moment to terminate
                
                # Verify it's really stopped
                $stillRunning = Get-Process -Id $process -ErrorAction SilentlyContinue
                if ($stillRunning) {
                    Write-Warning "  Process did not terminate immediately, retrying..."
                    Stop-Process -Id $process -Force -ErrorAction SilentlyContinue
                    Start-Sleep -Seconds 2
                }
                
                return $true
            }
            catch {
                Write-Error "  Failed to stop process: $($_.Exception.Message)"
                return $false
            }
        }
    }
    else {
        Write-Host "  No process found on port $Port" -ForegroundColor Gray
    }
    
    return $true  # Consider it "stopped" if no process was found
}

function Start-EhrService {
    param (
        [hashtable]$Service
    )
    
    Write-Host "  Starting $($Service.Name) on port $($Service.Port)..." -NoNewline
    
    # Ensure the port is free
    $existingProcess = Get-ProcessOnPort -Port $Service.Port
    if ($existingProcess) {
        Write-Host "CONFLICT" -ForegroundColor Red
        Write-Warning "  Port $($Service.Port) is already in use by process ID $existingProcess!"
        if (-not (Stop-ProcessOnPort -Port $Service.Port -ServiceName $Service.Name)) {
            Write-Error "  Failed to free up port $($Service.Port). Cannot start $($Service.Name)."
            return $null
        }
    }
    
    try {
        # Start the service
        $process = Start-Process -FilePath "powershell" -ArgumentList "-Command", "cd $($Service.WorkingDir); $($Service.StartCommand)" -PassThru -WindowStyle Normal
        
        if ($process -eq $null) {
            Write-Host "FAILED" -ForegroundColor Red
            Write-Error "  Failed to start process for $($Service.Name)"
            return $null
        }
        
        # Add to global processes list
        $Global:Processes += [PSCustomObject]@{
            Name = $Service.Name
            ProcessId = $process.Id
            Port = $Service.Port
            Endpoint = $Service.Endpoint
            StartTime = Get-Date
        }
        
        Write-Host "STARTED (PID: $($process.Id))" -ForegroundColor Green
        
        return $process.Id
    }
    catch {
        Write-Host "ERROR" -ForegroundColor Red
        Write-Error "  Failed to start $($Service.Name): $($_.Exception.Message)"
        return $null
    }
}

function Wait-ForEndpoints {
    param (
        [int]$TimeoutSeconds = 20,
        [int]$Interval = 2
    )
    
    Write-Step "Waiting for services to initialize..."
    
    $timer = [System.Diagnostics.Stopwatch]::StartNew()
    $allReady = $false
    $retries = 0
    
    while ($timer.Elapsed.TotalSeconds -lt $TimeoutSeconds) {
        $retries++
        $readyCount = 0
        $requiredCount = 0
        
        foreach ($service in $CONFIG.Services) {
            if ($service.Required) {
                $requiredCount++
                if (Test-Endpoint -Name $service.Name -Url $service.Endpoint) {
                    $readyCount++
                }
            }
        }
        
        if ($readyCount -eq $requiredCount) {
            $allReady = $true
            break
        }
        
        Write-Host "  Waiting for services ($readyCount/$requiredCount ready)... Retry $retries" -ForegroundColor Yellow
        Start-Sleep -Seconds $Interval
    }
    
    $timer.Stop()
    
    if ($allReady) {
        Write-Success "All required services are ready! (Took $($timer.Elapsed.TotalSeconds.ToString("0.0")) seconds)"
        return $true
    }
    else {
        Write-Warning "Timed out waiting for services to become ready!"
        return $false
    }
}

function Get-ServiceStatus {
    Write-Step "Checking service status..."
    
    $results = @()
    
    foreach ($service in $CONFIG.Services) {
        $processId = Get-ProcessOnPort -Port $service.Port
        
        if ($processId) {
            $processInfo = Get-Process -Id $processId -ErrorAction SilentlyContinue
            $processName = if ($processInfo) { $processInfo.ProcessName } else { "Unknown" }
            $endpointOnline = Test-Endpoint -Name $service.Name -Url $service.Endpoint
            
            $status = if ($endpointOnline) { "Online" } else { "Running but endpoint not responding" }
            
            $results += [PSCustomObject]@{
                Name = $service.Name
                Port = $service.Port
                Status = $status
                ProcessId = $processId
                ProcessName = $processName
                Endpoint = $service.Endpoint
                Required = $service.Required
            }
        }
        else {
            $results += [PSCustomObject]@{
                Name = $service.Name
                Port = $service.Port
                Status = "Offline"
                ProcessId = $null
                ProcessName = ""
                Endpoint = $service.Endpoint
                Required = $service.Required
            }
        }
    }
    
    return $results
}

function Show-ServiceStatus {
    $status = Get-ServiceStatus
    
    Write-Host ""
    Write-Host "Current Service Status:" -ForegroundColor Cyan
    $status | Format-Table -Property Name, Port, Status, ProcessId, ProcessName
    
    # Check if critical services are running
    $criticalOffline = $status | Where-Object { $_.Required -and $_.Status -eq "Offline" }
    
    if ($criticalOffline.Count -gt 0) {
        Write-Warning "Critical services are offline: $($criticalOffline.Name -join ', ')"
        return $false
    }
    
    return $true
}

function Stop-AllServices {
    Write-Step "Stopping all EHR services..."
    
    foreach ($service in $CONFIG.Services) {
        Stop-ProcessOnPort -Port $service.Port -ServiceName $service.Name
    }
    
    Write-Success "All services stopped"
}

function Fix-Service {
    param (
        [hashtable]$Service
    )
    
    if (-not $Service.ContainsKey('FixCommand')) {
        Write-Warning "No fix command specified for $($Service.Name)"
        return $false
    }
    
    Write-Host "  Applying fix for $($Service.Name)..." -NoNewline
    
    try {
        # Execute the fix command
        $workingDir = if ($Service.ContainsKey('FixWorkingDir')) { $Service.FixWorkingDir } else { $Service.WorkingDir }
        $result = Start-Process -FilePath "powershell" -ArgumentList "-Command", "cd $workingDir; $($Service.FixCommand)" -PassThru -Wait -NoNewWindow
        
        if ($result.ExitCode -eq 0) {
            Write-Host "SUCCESS" -ForegroundColor Green
            return $true
        }
        else {
            Write-Host "FAILED (Exit code: $($result.ExitCode))" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "ERROR" -ForegroundColor Red
        Write-Error "  Error applying fix: $($_.Exception.Message)"
        return $false
    }
}

function Fix-AllServices {
    Write-Step "Applying fixes to services with known issues..."
    
    $fixedCount = 0
    
    foreach ($service in $CONFIG.Services) {
        if ($service.ContainsKey('FixCommand')) {
            if (Fix-Service -Service $service) {
                $fixedCount++
            }
        }
    }
    
    if ($fixedCount -gt 0) {
        Write-Success "Applied fixes to $fixedCount services"
    }
    else {
        Write-Host "  No fixes were applied" -ForegroundColor Gray
    }
}

function Start-EhrSystem {
    Write-Title "Starting EHR System v$SCRIPT_VERSION"
    
    # Stop any existing services first
    Stop-AllServices
    
    # Start each service in the proper order
    Write-Step "Starting services..."
    
    foreach ($service in $CONFIG.Services) {
        Start-EhrService -Service $service
    }
    
    # Wait for all services to be available
    $success = Wait-ForEndpoints -TimeoutSeconds 30
    
    # Show final status
    Show-ServiceStatus
    
    if ($success) {
        Write-Success "EHR System started successfully!"
        Write-Host "System is available at: http://localhost:8081/" -ForegroundColor Green
    }
    else {
        Write-Warning "Some services failed to start or are not responding."
        Write-Host "Check the status output above and consider running 'master_ehr.ps1 fix' then 'master_ehr.ps1 restart'" -ForegroundColor Yellow
    }
}

function Restart-EhrSystem {
    Write-Title "Restarting EHR System v$SCRIPT_VERSION"
    
    # Stop all services
    Stop-AllServices
    
    # Apply any fixes
    Fix-AllServices
    
    # Start the system again
    Start-EhrSystem
}

function Check-EhrSystem {
    Write-Title "Checking EHR System Health v$SCRIPT_VERSION"
    
    # Check service status
    Show-ServiceStatus
    
    # Additional checks can be added here
}

# Main Execution
try {
    # Set the working directory to the script location
    Push-Location $PSScriptRoot
    
    switch ($Command.ToLower()) {
        'start' {
            Start-EhrSystem
        }
        'stop' {
            Write-Title "Stopping EHR System v$SCRIPT_VERSION"
            Stop-AllServices
        }
        'restart' {
            Restart-EhrSystem
        }
        'status' {
            Check-EhrSystem
        }
        'check' {
            Check-EhrSystem
        }
        'fix' {
            Write-Title "Fixing EHR System v$SCRIPT_VERSION"
            Fix-AllServices
        }
        default {
            Write-Error "Unknown command: $Command"
            Write-Host "Available commands: start, stop, restart, status, check, fix" -ForegroundColor Yellow
        }
    }
}
finally {
    # Restore the original working directory
    Pop-Location
} 