# EHR System Manager Script
param (
    [ValidateSet('start', 'stop', 'restart', 'status', 'fix')]
    [string]$Command = 'start'
)

$ErrorActionPreference = "Stop"

# Get the current directory, handling both script and direct execution
function Get-ScriptDirectory {
    if ($PSScriptRoot) {
        # Normal execution from a file
        return $PSScriptRoot
    } elseif ($MyInvocation.MyCommand.Path) {
        # If script path is available
        return Split-Path -Parent $MyInvocation.MyCommand.Path
    } else {
        # Fallback to current working directory
        return (Get-Location).Path
    }
}

# Get absolute path for the project
$PROJECT_ROOT = Get-ScriptDirectory
Write-Host "Project root directory: $PROJECT_ROOT" -ForegroundColor DarkGray

# Constants
$SCRIPT_VERSION = "1.0.0"
$PORTS = @(8001, 8002, 8003, 8004, 8081)
$SERVICES = @(
    @{
        Name = "Login API"; 
        Port = 8001; 
        Command = "python -m api.login_api"; 
        WorkDir = "backend";
        TestUrl = "http://localhost:8001/api/health";
    },
    @{
        Name = "Patient API"; 
        Port = 8002; 
        Command = "python start_apis.py"; 
        WorkDir = "backend";
        TestUrl = "http://localhost:8002/api/patients?limit=1";
    },
    @{
        Name = "Records API"; 
        Port = 8003; 
        Command = "python -c `"import os; os.environ['PORT'] = '8003'; from api.records_api import app; app.run(host='0.0.0.0', port=8003, debug=False)`"";
        WorkDir = "backend";
        TestUrl = "http://localhost:8003/api/records";
        FixCommand = "powershell -Command `"(Get-Content api/records_api.py) -replace '            # Convert query result to dictionary', '        # Convert query result to dictionary' -replace '            column_names = \[desc\[0\] for desc in cursor.description\]', '        column_names = [desc[0] for desc in cursor.description]' -replace '            record = dict\(zip\(column_names, cursor.fetchone\(\)\)\)', '        record = dict(zip(column_names, cursor.fetchone()))' | Set-Content api/records_api.py`"";
    },
    @{
        Name = "Vaccine API"; 
        Port = 8004; 
        Command = "python start_vaccine_server.py";
        WorkDir = "backend";
        TestUrl = "http://localhost:8004/api/vaccines/simple";
    },
    @{
        Name = "Frontend"; 
        Port = 8081; 
        Command = "cmd.exe /c npm run dev -- --port 8081 --force";
        WorkDir = "ehr-vue-app";
        TestUrl = "http://localhost:8081/";
    }
)

# Helper Functions
function Write-Header {
    param([string]$Message)
    Write-Host "`n==== $Message ====`n" -ForegroundColor Cyan
}

function KillProcessOnPort {
    param([int]$Port)
    
    $process = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | 
               Select-Object -ExpandProperty OwningProcess -ErrorAction SilentlyContinue
    
    if ($process) {
        $processInfo = Get-Process -Id $process -ErrorAction SilentlyContinue
        if ($processInfo) {
            Write-Host "  Killing process on port $Port (PID: $process, $($processInfo.ProcessName))" -ForegroundColor Yellow
            Stop-Process -Id $process -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 1
        }
    } else {
        Write-Host "  No process found on port $Port" -ForegroundColor Gray
    }
}

function TestEndpoint {
    param(
        [string]$Url,
        [int]$TimeoutSec = 5,
        [int]$Retries = 1
    )
    
    for ($i = 0; $i -lt $Retries; $i++) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec $TimeoutSec -ErrorAction Stop
            return $true
        } catch {
            if ($i -lt $Retries - 1) {
                Start-Sleep -Seconds 1
            }
        }
    }
    
    return $false
}

function FixRecordsApiIndentation {
    Write-Host "Fixing indentation in Records API..."
    
    try {
        $backendDir = Join-Path $PROJECT_ROOT "backend"
        $recordsApiPath = Join-Path $backendDir "api/records_api.py"
        
        if (-not (Test-Path $recordsApiPath)) {
            Write-Host "  Error: Records API file not found at: $recordsApiPath" -ForegroundColor Red
            return $false
        }
        
        Push-Location $backendDir
        (Get-Content $recordsApiPath) -replace '            # Convert query result to dictionary', '        # Convert query result to dictionary' -replace '            column_names = \[desc\[0\] for desc in cursor.description\]', '        column_names = [desc[0] for desc in cursor.description]' -replace '            record = dict\(zip\(column_names, cursor.fetchone\(\)\)\)', '        record = dict(zip(column_names, cursor.fetchone()))' | Set-Content $recordsApiPath
        Write-Host "  Fixed indentation issue in Records API" -ForegroundColor Green
        Pop-Location
        return $true
    } catch {
        Write-Host "  Failed to fix Records API: $($_.Exception.Message)" -ForegroundColor Red
        if ((Get-Location).Path -ne $PROJECT_ROOT) {
            Pop-Location
        }
        return $false
    }
}

function StartService {
    param(
        [hashtable]$Service
    )
    
    Write-Host "Starting $($Service.Name) on port $($Service.Port)..." -NoNewline
    
    try {
        # Resolve absolute paths
        $workDir = Join-Path $PROJECT_ROOT $Service.WorkDir
        
        if (-not (Test-Path $workDir -PathType Container)) {
            Write-Host "FAILED" -ForegroundColor Red
            Write-Host "  Error: Directory not found: $workDir" -ForegroundColor Red
            return $null
        }
        
        # Special handling for Records API
        if ($Service.Name -eq "Records API") {
            # Create a startup script with absolute paths
            $scriptPath = Join-Path $PROJECT_ROOT "start_records_api.ps1"
            @"
# Use absolute path for the backend directory
`$backendDir = "$workDir"

# Change to the backend directory
Set-Location `$backendDir

# Run the command
$($Service.Command)
"@ | Set-Content -Path $scriptPath
            
            $processStartInfo = New-Object System.Diagnostics.ProcessStartInfo
            $processStartInfo.FileName = "powershell"
            $processStartInfo.Arguments = "-NoExit -File `"$scriptPath`""
            $processStartInfo.UseShellExecute = $true
        } else {
            $processStartInfo = New-Object System.Diagnostics.ProcessStartInfo
            $processStartInfo.FileName = "powershell"
            $processStartInfo.Arguments = "-Command Set-Location '$workDir'; $($Service.Command)"
            $processStartInfo.UseShellExecute = $true
        }
        
        $process = [System.Diagnostics.Process]::Start($processStartInfo)
        Write-Host "STARTED (PID: $($process.Id))" -ForegroundColor Green
        return $process.Id
    } catch {
        Write-Host "FAILED" -ForegroundColor Red
        Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
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
            
            # Use more retries for Records API
            $retries = if ($service.Name -eq "Records API") { 3 } else { 1 }
            $isResponding = TestEndpoint -Url $service.TestUrl -Retries $retries
            
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
    
    # Kill any existing processes
    Write-Host "Stopping any existing processes..."
    foreach ($port in $PORTS) {
        KillProcessOnPort -Port $port
    }
    
    # Initialize database
    Write-Host "Checking database status..." -ForegroundColor Cyan
    try {
        $backendDir = Join-Path $PROJECT_ROOT "backend"
        
        if (-not (Test-Path $backendDir -PathType Container)) {
            Write-Host "  Error: Backend directory not found: $backendDir" -ForegroundColor Red
            Write-Host "  Database initialization skipped. Some features may not work correctly." -ForegroundColor Yellow
        } else {
            Push-Location $backendDir
            python -c "from setup_database import initialize_database; initialize_database()"
            $dbInitResult = $?
            Pop-Location
            
            if ($dbInitResult) {
                Write-Host "  Database initialization successful!" -ForegroundColor Green
            } else {
                Write-Host "  Database initialization failed or skipped. Some features may not work correctly." -ForegroundColor Yellow
            }
        }
    } catch {
        Write-Host "  Database initialization failed: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "  Continuing startup anyway, but some features may not work correctly." -ForegroundColor Yellow
        if ((Get-Location).Path -ne $PROJECT_ROOT) {
            Pop-Location
        }
    }
    
    # Fix Records API first before starting anything
    FixRecordsApiIndentation
    
    # Start each service
    foreach ($service in $SERVICES) {
        $processId = StartService -Service $service
        Start-Sleep -Seconds 1
    }
    
    # Wait for initialization
    Write-Host "`nWaiting for services to initialize..." -ForegroundColor Cyan
    Start-Sleep -Seconds 10  # Increased from 5 to 10 seconds
    
    # Show status
    $status = CheckStatus
    Write-Host "`nCurrent Service Status:" -ForegroundColor Cyan
    $status | Format-Table -Property Name, Port, Status, Process, PID
    
    # Check for any services that are not responding and attempt to fix them
    foreach ($svc in $status) {
        if ($svc.Status -eq "Running but not responding" -and $svc.Name -eq "Records API") {
            Write-Host "Attempting to fix Records API..." -ForegroundColor Yellow
            FixRecordsApiIndentation
            # Restart the Records API
            foreach ($service in $SERVICES) {
                if ($service.Name -eq "Records API") {
                    KillProcessOnPort -Port $service.Port
                    Start-Sleep -Seconds 2
                    $processId = StartService -Service $service
                    break
                }
            }
        }
    }
    
    Write-Host "`nEHR System started. Access the application at: http://localhost:8081/" -ForegroundColor Green
}

function StopSystem {
    Write-Header "Stopping EHR System"
    
    foreach ($port in $PORTS) {
        KillProcessOnPort -Port $port
    }
    
    Write-Host "All services stopped." -ForegroundColor Green
}

function CheckSystemStatus {
    Write-Header "EHR System Status"
    
    $status = CheckStatus
    $status | Format-Table -Property Name, Port, Status, Process, PID
}

function FixSystem {
    Write-Header "Applying Fixes to EHR System"
    
    # Fix Records API indentation issue
    FixRecordsApiIndentation
    
    Write-Host "`nFixes applied. You should now restart the system with: .\ehr_manager_fixed.ps1 restart" -ForegroundColor Green
}

# Main execution
try {
    switch ($Command.ToLower()) {
        "start" {
            StartSystem
        }
        "stop" {
            StopSystem
        }
        "restart" {
            StopSystem
            Start-Sleep -Seconds 2
            StartSystem
        }
        "status" {
            CheckSystemStatus
        }
        "fix" {
            FixSystem
        }
        default {
            Write-Host "Unknown command: $Command" -ForegroundColor Red
            Write-Host "Available commands: start, stop, restart, status, fix" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
} 