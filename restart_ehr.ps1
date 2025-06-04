# EHR System Restart PowerShell Script
Write-Host "EHR System Restart Script" -ForegroundColor Green
Write-Host "-----------------------" -ForegroundColor Green
Write-Host ""

# Function to kill process using a specific port
function Kill-ProcessOnPort {
    param (
        [int]$Port
    )
    
    $process = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -ErrorAction SilentlyContinue
    
    if ($process) {
        $processInfo = Get-Process -Id $process -ErrorAction SilentlyContinue
        if ($processInfo) {
            Write-Host "Killing process $($processInfo.ProcessName) (PID: $process) on port $Port" -ForegroundColor Yellow
            Stop-Process -Id $process -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 1
        }
    } else {
        Write-Host "No process found on port $Port" -ForegroundColor Gray
    }
}

# Kill processes on required ports
Write-Host "Stopping any processes on ports 8001-8004 and 8081..." -ForegroundColor Cyan
Kill-ProcessOnPort -Port 8001
Kill-ProcessOnPort -Port 8002
Kill-ProcessOnPort -Port 8003
Kill-ProcessOnPort -Port 8004
Kill-ProcessOnPort -Port 8081

# Create an array to store process information
$processes = @()

# Start Login API (port 8001)
Write-Host "Starting Login API on port 8001..." -ForegroundColor Cyan
$loginApi = Start-Process -FilePath "python" -ArgumentList "-m api.login_api" -WorkingDirectory "backend" -PassThru -WindowStyle Normal
$processes += [PSCustomObject]@{
    Name = "Login API"
    ProcessId = $loginApi.Id
    Port = 8001
    Endpoint = "http://localhost:8001/api/"
}

# Start Patient API (port 8002)
Write-Host "Starting Patient API on port 8002..." -ForegroundColor Cyan
$patientApi = Start-Process -FilePath "python" -ArgumentList "start_apis.py" -WorkingDirectory "backend" -PassThru -WindowStyle Normal
$processes += [PSCustomObject]@{
    Name = "Patient API"
    ProcessId = $patientApi.Id
    Port = 8002
    Endpoint = "http://localhost:8002/api/"
}

# Start Vaccine API (port 8004)
Write-Host "Starting Vaccine API on port 8004..." -ForegroundColor Cyan
$vaccineApi = Start-Process -FilePath "python" -ArgumentList "start_vaccine_server.py" -WorkingDirectory "backend" -PassThru -WindowStyle Normal
$processes += [PSCustomObject]@{
    Name = "Vaccine API"
    ProcessId = $vaccineApi.Id
    Port = 8004
    Endpoint = "http://localhost:8004/api/"
}

# Wait for APIs to be ready
Write-Host "Waiting for APIs to initialize (5 seconds)..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

# Start Frontend (port 8081)
Write-Host "Starting Frontend on port 8081..." -ForegroundColor Cyan
# Use cmd.exe to start npm to ensure it works properly
$frontend = Start-Process -FilePath "cmd.exe" -ArgumentList "/c cd ehr-vue-app && npm run dev -- --port 8081 --force" -PassThru -WindowStyle Normal
$processes += [PSCustomObject]@{
    Name = "EHR Frontend"
    ProcessId = $frontend.Id
    Port = 8081
    Endpoint = "http://localhost:8081/"
}

Write-Host ""
Write-Host "EHR System started successfully!" -ForegroundColor Green
Write-Host ""

Write-Host "Running Services:" -ForegroundColor Green
$processes | Format-Table -Property Name, ProcessId, Port, Endpoint

Write-Host "Note: Console windows must remain open for services to run" -ForegroundColor Yellow
Write-Host "To stop all services, close this window and run this script again" -ForegroundColor Yellow 