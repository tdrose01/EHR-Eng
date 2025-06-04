# EHR System Diagnostic and Repair Tool
Write-Host "EHR System Diagnostic and Repair" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan

function Test-ServiceRunning {
    param ([string]$HostName, [int]$Port)
    try {
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $connectionResult = $tcpClient.BeginConnect($HostName, $Port, $null, $null)
        $wait = $connectionResult.AsyncWaitHandle.WaitOne(1000, $false)
        if ($wait -and $tcpClient.Connected) {
            $tcpClient.EndConnect($connectionResult); $tcpClient.Close(); return $true
        }
        if ($tcpClient.Connected) { $tcpClient.Close() }
        return $false
    } catch { return $false }
}

function Test-API {
    param ([string]$Uri, [string]$Name)
    Write-Host "Testing $Name API... " -NoNewline
    try {
        $response = Invoke-WebRequest -Uri $Uri -Method GET -TimeoutSec 5
        Write-Host "OK ($($response.StatusCode))" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "FAILED: $_" -ForegroundColor Red
        return $false
    }
}

function Fix-Permissions {
    param ([string]$Path)
    if (Test-Path $Path) {
        Write-Host "Setting permissions for $Path"
        $acl = Get-Acl -Path $Path
        $accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule("Everyone", "FullControl", "Allow")
        $acl.SetAccessRule($accessRule)
        Set-Acl -Path $Path -AclObject $acl
        return $true
    }
    return $false
}

# Check system status
Write-Host "`n[1] Checking system status..." -ForegroundColor Yellow
$backendRunning = Test-ServiceRunning -HostName "localhost" -Port 8000
$frontendRunning = Test-ServiceRunning -HostName "localhost" -Port 8081
$vaccineApiRunning = Test-ServiceRunning -HostName "localhost" -Port 8004

Write-Host "Backend API: $(if($backendRunning){"Running [OK]"}else{"Not Running [FAIL]"})" -ForegroundColor $(if($backendRunning){[System.ConsoleColor]::Green}else{[System.ConsoleColor]::Red})
Write-Host "Frontend: $(if($frontendRunning){"Running [OK]"}else{"Not Running [FAIL]"})" -ForegroundColor $(if($frontendRunning){[System.ConsoleColor]::Green}else{[System.ConsoleColor]::Red})
Write-Host "Vaccine API: $(if($vaccineApiRunning){"Running [OK]"}else{"Not Running [FAIL]"})" -ForegroundColor $(if($vaccineApiRunning){[System.ConsoleColor]::Green}else{[System.ConsoleColor]::Red})

# Test APIs if running
if ($backendRunning) {
    Write-Host "`n[2] Testing API endpoints..." -ForegroundColor Yellow
    $healthOk = Test-API -Uri "http://localhost:8000/api/health" -Name "Health"
    $dashboardOk = Test-API -Uri "http://localhost:8000/api/dashboard/stats" -Name "Dashboard"
    $patientsOk = Test-API -Uri "http://localhost:8000/api/patients" -Name "Patients"
} else {
    $healthOk = $dashboardOk = $patientsOk = $false
}

# Check file system
Write-Host "`n[3] Checking file system..." -ForegroundColor Yellow
$basePath = $PSScriptRoot
$backendPath = Join-Path -Path $basePath -ChildPath "backend"
$frontendPath = Join-Path -Path $basePath -ChildPath "ehr-vue-app"
$dbPath = Join-Path -Path $backendPath -ChildPath "instance/clinic.db"

Write-Host "Backend directory: $(if(Test-Path $backendPath){"Exists [OK]"}else{"Missing [FAIL]"})" -ForegroundColor $(if(Test-Path $backendPath){[System.ConsoleColor]::Green}else{[System.ConsoleColor]::Red})
Write-Host "Frontend directory: $(if(Test-Path $frontendPath){"Exists [OK]"}else{"Missing [FAIL]"})" -ForegroundColor $(if(Test-Path $frontendPath){[System.ConsoleColor]::Green}else{[System.ConsoleColor]::Red})
Write-Host "Database file: $(if(Test-Path $dbPath){"Exists [OK]"}else{"Missing [FAIL]"})" -ForegroundColor $(if(Test-Path $dbPath){[System.ConsoleColor]::Green}else{[System.ConsoleColor]::Red})

# Determine issues to fix
$issuesFound = @()
if (-not $backendRunning) { $issuesFound += "Backend not running" }
if (-not $frontendRunning) { $issuesFound += "Frontend not running" }
if ($backendRunning -and -not $dashboardOk) { $issuesFound += "Dashboard API failing" }
if (-not (Test-Path $dbPath)) { $issuesFound += "Database missing" }

# Report issues
Write-Host "`n[4] Diagnostic Summary:" -ForegroundColor Yellow
if ($issuesFound.Count -eq 0) {
    Write-Host "All systems operational. No issues detected." -ForegroundColor Green
} else {
    Write-Host "Issues detected: $($issuesFound.Count)" -ForegroundColor Red
    foreach ($issue in $issuesFound) {
        Write-Host " - $issue" -ForegroundColor Red
    }

    # Fix issues
    Write-Host "`n[5] Attempting repairs..." -ForegroundColor Yellow
    
    # Fix database if missing
    if (-not (Test-Path $dbPath)) {
        Write-Host "Creating database directory and file..." -ForegroundColor Yellow
        $instanceDir = Join-Path -Path $backendPath -ChildPath "instance"
        if (-not (Test-Path $instanceDir)) {
            New-Item -ItemType Directory -Path $instanceDir -Force | Out-Null
        }
        $null | Set-Content -Path $dbPath
        Fix-Permissions -Path $dbPath
    }
    
    # Fix permissions on key files
    Fix-Permissions -Path $dbPath
    
    # Restart backend if needed
    if (-not $backendRunning -or ($backendRunning -and -not $dashboardOk)) {
        Write-Host "Restarting backend services..." -ForegroundColor Yellow
        $pythonProcesses = Get-Process -Name python -ErrorAction SilentlyContinue
        if ($pythonProcesses) {
            $pythonProcesses | ForEach-Object {
                Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
            }
            Start-Sleep -Seconds 2
        }
        Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "start_backend_admin.bat" -NoNewWindow
        Write-Host "Waiting for backend to start..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10
    }
    
    # Restart frontend if needed
    if (-not $frontendRunning) {
        Write-Host "Starting frontend service..." -ForegroundColor Yellow
        Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "start_frontend_admin.bat" -NoNewWindow
        Write-Host "Waiting for frontend to start..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10
    }
    
    # Verify fixes
    Write-Host "`n[6] Verifying repairs..." -ForegroundColor Yellow
    $backendRunning = Test-ServiceRunning -HostName "localhost" -Port 8000
    $frontendRunning = Test-ServiceRunning -HostName "localhost" -Port 8081
    
    Write-Host "Backend API: $(if($backendRunning){"Running [OK]"}else{"Still not running [FAIL]"})" -ForegroundColor $(if($backendRunning){[System.ConsoleColor]::Green}else{[System.ConsoleColor]::Red})
    Write-Host "Frontend: $(if($frontendRunning){"Running [OK]"}else{"Still not running [FAIL]"})" -ForegroundColor $(if($frontendRunning){[System.ConsoleColor]::Green}else{[System.ConsoleColor]::Red})
    
    if ($backendRunning) {
        $dashboardOk = Test-API -Uri "http://localhost:8000/api/dashboard/stats" -Name "Dashboard"
    }
}

# Final instructions
Write-Host "`n[7] Next Steps:" -ForegroundColor Yellow
Write-Host "1. Open your browser and navigate to: http://localhost:8081" -ForegroundColor White
Write-Host "2. If dashboard statistics still fail to load, try clearing your browser cache" -ForegroundColor White
Write-Host "3. For persistent issues, please check the application logs or contact support" -ForegroundColor White

Write-Host "`nDiagnostic completed. Press any key to exit..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 