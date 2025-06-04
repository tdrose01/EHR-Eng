# Check-Servers.ps1 - Script to verify if backend servers are running properly
Write-Host "Checking server status..." -ForegroundColor Cyan

# Function to test connection to a port
function Test-ServerConnection {
    param (
        [string]$HostName,
        [int]$Port,
        [string]$ServiceName
    )
    
    Write-Host "Testing connection to $ServiceName ($HostName`:$Port)..." -NoNewline
    
    try {
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $connectionResult = $tcpClient.BeginConnect($HostName, $Port, $null, $null)
        $wait = $connectionResult.AsyncWaitHandle.WaitOne(1000, $false)
        
        if ($wait) {
            if ($tcpClient.Connected) {
                Write-Host "SUCCESS" -ForegroundColor Green
                $tcpClient.EndConnect($connectionResult)
                $tcpClient.Close()
                return $true
            }
        }
        
        if ($tcpClient.Connected) {
            $tcpClient.Close()
        }
        
        Write-Host "FAILED" -ForegroundColor Red
        return $false
    }
    catch {
        Write-Host "ERROR: $_" -ForegroundColor Red
        return $false
    }
}

# Check for running Python processes
$pythonProcesses = Get-Process -Name python -ErrorAction SilentlyContinue
$nodejsProcesses = Get-Process -Name node -ErrorAction SilentlyContinue

Write-Host "`nRunning Processes:" -ForegroundColor Yellow
if ($pythonProcesses) {
    Write-Host "Python processes found: $($pythonProcesses.Count)"
    $pythonProcesses | ForEach-Object {
        Write-Host "  PID: $($_.Id), CPU: $($_.CPU), Memory: $([math]::Round($_.WorkingSet64/1MB, 2)) MB"
    }
} else {
    Write-Host "No Python processes found. Backend servers might not be running." -ForegroundColor Red
}

if ($nodejsProcesses) {
    Write-Host "Node.js processes found: $($nodejsProcesses.Count)"
    $nodejsProcesses | ForEach-Object {
        Write-Host "  PID: $($_.Id), CPU: $($_.CPU), Memory: $([math]::Round($_.WorkingSet64/1MB, 2)) MB"
    }
} else {
    Write-Host "No Node.js processes found. Frontend server might not be running." -ForegroundColor Red
}

# Test connections to the servers
Write-Host "`nServer Connection Tests:" -ForegroundColor Yellow
$mainApiRunning = Test-ServerConnection -HostName "localhost" -Port 8000 -ServiceName "Main API"
$frontendRunning = Test-ServerConnection -HostName "localhost" -Port 8081 -ServiceName "Frontend"
$vaccineApiRunning = Test-ServerConnection -HostName "localhost" -Port 8004 -ServiceName "Vaccine API"

# Test HTTP requests to the servers if they're running
if ($mainApiRunning) {
    Write-Host "`nTesting HTTP request to Main API health endpoint..." -ForegroundColor Yellow
    try {
        $result = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -Method GET -TimeoutSec 5
        Write-Host "Main API health check status: $($result.StatusCode)" -ForegroundColor Green
        Write-Host "Response: $($result.Content)"
    } catch {
        Write-Host "Failed to get health status from Main API: $_" -ForegroundColor Red
    }
    
    Write-Host "`nTesting HTTP request to Dashboard API..." -ForegroundColor Yellow
    try {
        $result = Invoke-WebRequest -Uri "http://localhost:8000/api/dashboard/stats" -Method GET -TimeoutSec 5
        Write-Host "Dashboard API status: $($result.StatusCode)" -ForegroundColor Green
        Write-Host "Response: $($result.Content)"
    } catch {
        Write-Host "Failed to get stats from Dashboard API: $_" -ForegroundColor Red
    }
}

Write-Host "`nServer checks completed." -ForegroundColor Cyan
Write-Host "Main API running: $mainApiRunning"
Write-Host "Frontend running: $frontendRunning"
Write-Host "Vaccine API running: $vaccineApiRunning"

# Provide next steps based on the results
Write-Host "`nRecommended Actions:" -ForegroundColor Yellow
if (-not $mainApiRunning -or -not $vaccineApiRunning) {
    Write-Host "- Start backend servers by running: .\start_backend_admin.bat" -ForegroundColor Magenta
}
if (-not $frontendRunning) {
    Write-Host "- Start frontend server by running: .\start_frontend_admin.bat" -ForegroundColor Magenta
}
if ($mainApiRunning -and $frontendRunning) {
    Write-Host "- All essential services appear to be running. Try accessing the application at http://localhost:8081" -ForegroundColor Green
}

Write-Host "`nPress any key to exit..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 