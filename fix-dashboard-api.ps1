# Fix-Dashboard-API.ps1 - Focus on fixing the dashboard API issue
Write-Host "Dashboard API Fix Utility" -ForegroundColor Cyan
Write-Host "=======================`n" -ForegroundColor Cyan

# Check if backend is running
function Test-ServiceRunning {
    param (
        [string]$HostName,
        [int]$Port
    )
    
    try {
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $connectionResult = $tcpClient.BeginConnect($HostName, $Port, $null, $null)
        $wait = $connectionResult.AsyncWaitHandle.WaitOne(1000, $false)
        
        if ($wait -and $tcpClient.Connected) {
            $tcpClient.EndConnect($connectionResult)
            $tcpClient.Close()
            return $true
        }
        
        if ($tcpClient.Connected) {
            $tcpClient.Close()
        }
        
        return $false
    }
    catch {
        return $false
    }
}

# Step 1: Verify backend is running
Write-Host "Step 1: Checking if backend server is running..." -ForegroundColor Yellow
$backendRunning = Test-ServiceRunning -HostName "localhost" -Port 8000
if (-not $backendRunning) {
    Write-Host "Backend server is not running! Starting it now..." -ForegroundColor Red
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "start_backend_admin.bat" -NoNewWindow
    Write-Host "Waiting for backend to start (15 seconds)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 15
    $backendRunning = Test-ServiceRunning -HostName "localhost" -Port 8000
    if (-not $backendRunning) {
        Write-Host "Failed to start backend server. Please start it manually." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Backend server is already running." -ForegroundColor Green
}

# Step 2: Test the dashboard API with diagnostic information
Write-Host "`nStep 2: Testing dashboard API endpoint..." -ForegroundColor Yellow
try {
    $headers = @{
        "Accept" = "application/json"
        "Content-Type" = "application/json"
    }
    
    Write-Host "Sending request to http://localhost:8000/api/dashboard/stats..." -ForegroundColor Gray
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/dashboard/stats" -Method GET -Headers $headers -TimeoutSec 10
    
    Write-Host "Response Status: $($response.StatusCode) $($response.StatusDescription)" -ForegroundColor Green
    Write-Host "Response Headers:" -ForegroundColor Gray
    $response.Headers | Format-Table -AutoSize
    
    Write-Host "Response Content:" -ForegroundColor Gray
    $responseContent = $response.Content | ConvertFrom-Json
    $responseContent | ConvertTo-Json -Depth 5
    
    Write-Host "`nDashboard API is responding correctly!" -ForegroundColor Green
} catch {
    Write-Host "Error testing dashboard API: $_" -ForegroundColor Red
    Write-Host "`nAttempting to fix common issues..." -ForegroundColor Yellow
    
    # Step 3: Checking database connectivity
    Write-Host "`nStep 3: Checking database connectivity..." -ForegroundColor Yellow
    
    # Ensure backend directory exists
    $backendDir = Join-Path -Path $PSScriptRoot -ChildPath "backend"
    if (-not (Test-Path -Path $backendDir)) {
        Write-Host "Backend directory not found at $backendDir" -ForegroundColor Red
        exit 1
    }
    
    # Check database file
    $dbPath = Join-Path -Path $backendDir -ChildPath "instance/clinic.db"
    if (-not (Test-Path -Path $dbPath)) {
        Write-Host "Database file not found at $dbPath" -ForegroundColor Red
        
        # Create directory if it doesn't exist
        $instanceDir = Join-Path -Path $backendDir -ChildPath "instance"
        if (-not (Test-Path -Path $instanceDir)) {
            New-Item -ItemType Directory -Path $instanceDir -Force | Out-Null
            Write-Host "Created instance directory: $instanceDir" -ForegroundColor Yellow
        }
        
        # Create an empty database file
        $null | Set-Content -Path $dbPath
        Write-Host "Created empty database file: $dbPath" -ForegroundColor Yellow
        
        # Set appropriate permissions
        $acl = Get-Acl -Path $dbPath
        $accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule("Everyone", "FullControl", "Allow")
        $acl.SetAccessRule($accessRule)
        Set-Acl -Path $dbPath -AclObject $acl
        Write-Host "Set permissions on database file" -ForegroundColor Yellow
    } else {
        Write-Host "Database file exists at $dbPath" -ForegroundColor Green
        
        # Check file permissions
        $acl = Get-Acl -Path $dbPath
        $permissions = $acl.Access | ForEach-Object { "$($_.IdentityReference) - $($_.FileSystemRights)" }
        Write-Host "Current permissions:" -ForegroundColor Gray
        $permissions
        
        # Ensure everyone has read/write access
        $acl = Get-Acl -Path $dbPath
        $accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule("Everyone", "FullControl", "Allow")
        $acl.SetAccessRule($accessRule)
        Set-Acl -Path $dbPath -AclObject $acl
        Write-Host "Updated permissions on database file" -ForegroundColor Yellow
    }
    
    # Step 4: Restart backend service
    Write-Host "`nStep 4: Restarting backend service..." -ForegroundColor Yellow
    
    # Kill existing Python processes
    $pythonProcesses = Get-Process -Name python -ErrorAction SilentlyContinue
    if ($pythonProcesses) {
        Write-Host "Stopping existing Python processes..." -ForegroundColor Yellow
        $pythonProcesses | ForEach-Object {
            Write-Host "  Stopping PID: $($_.Id)" -ForegroundColor Gray
            Stop-Process -Id $_.Id -Force
        }
        Start-Sleep -Seconds 2
    }
    
    # Start backend with admin privileges
    Write-Host "Starting backend with admin privileges..." -ForegroundColor Yellow
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "start_backend_admin.bat" -Verb RunAs
    
    Write-Host "Waiting for backend to start (15 seconds)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 15
    
    # Test if backend is running
    $backendRunning = Test-ServiceRunning -HostName "localhost" -Port 8000
    if ($backendRunning) {
        Write-Host "Backend server successfully restarted!" -ForegroundColor Green
        
        # Test dashboard API again
        Write-Host "`nTesting dashboard API again..." -ForegroundColor Yellow
        try {
            $headers = @{
                "Accept" = "application/json"
                "Content-Type" = "application/json"
            }
            
            $response = Invoke-WebRequest -Uri "http://localhost:8000/api/dashboard/stats" -Method GET -Headers $headers -TimeoutSec 10
            Write-Host "Response Status: $($response.StatusCode) $($response.StatusDescription)" -ForegroundColor Green
            
            $responseContent = $response.Content | ConvertFrom-Json
            $responseContent | ConvertTo-Json -Depth 5
            
            Write-Host "`nDashboard API is now responding correctly!" -ForegroundColor Green
        } catch {
            Write-Host "Error testing dashboard API after restart: $_" -ForegroundColor Red
        }
    } else {
        Write-Host "Failed to restart backend server." -ForegroundColor Red
    }
}

# Step 5: Verify frontend is running correctly
Write-Host "`nStep 5: Checking if frontend is running..." -ForegroundColor Yellow
$frontendRunning = Test-ServiceRunning -HostName "localhost" -Port 8081
if (-not $frontendRunning) {
    Write-Host "Frontend is not running! Starting it now..." -ForegroundColor Red
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "start_frontend_admin.bat" -NoNewWindow
    Write-Host "Waiting for frontend to start (15 seconds)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 15
} else {
    Write-Host "Frontend is running on port 8081." -ForegroundColor Green
}

# Final instructions
Write-Host "`nDashboard API fix process completed!" -ForegroundColor Cyan
Write-Host "- The application should now be available at: http://localhost:8081" -ForegroundColor Yellow
Write-Host "- The dashboard should load statistics correctly" -ForegroundColor Yellow
Write-Host "- If you still experience issues, try refreshing the page or clearing your browser cache" -ForegroundColor Yellow

Write-Host "`nPress any key to exit..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 