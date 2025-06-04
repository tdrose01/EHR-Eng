# EHR End-to-End Test with Permission Issue Handling
Write-Host "EHR Application End-to-End Test Suite" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Step 1: Create test-results directory
Write-Host "Step 1: Creating test-results directory if it doesn't exist" -ForegroundColor Yellow
if (-not (Test-Path "test-results")) {
    New-Item -ItemType Directory -Path "test-results" | Out-Null
}

# Step 2: Kill any running EHR processes
Write-Host "Step 2: Killing any running EHR processes" -ForegroundColor Yellow
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like "*start_apis*" -or $_.MainWindowTitle -like "*start_vaccine*" } | Stop-Process -Force

# Check if port 8000 is in use and release it if necessary
Write-Host "Step 3: Checking for occupied ports" -ForegroundColor Yellow
$port8000InUse = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($port8000InUse) {
    Write-Host "Port 8000 is in use. Attempting to free it..." -ForegroundColor Yellow
    foreach ($process in $port8000InUse) {
        $processId = $process.OwningProcess
        $processName = (Get-Process -Id $processId -ErrorAction SilentlyContinue).Name
        Write-Host "Stopping process $processName (PID: $processId) using port 8000" -ForegroundColor Red
        Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    }
}

# Check if port 8081 is in use and release it if necessary
$port8081InUse = Get-NetTCPConnection -LocalPort 8081 -ErrorAction SilentlyContinue
if ($port8081InUse) {
    Write-Host "Port 8081 is in use. Attempting to free it..." -ForegroundColor Yellow
    foreach ($process in $port8081InUse) {
        $processId = $process.OwningProcess
        $processName = (Get-Process -Id $processId -ErrorAction SilentlyContinue).Name
        Write-Host "Stopping process $processName (PID: $processId) using port 8081" -ForegroundColor Red
        Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    }
}

# Step 4: Clear Vite cache to prevent permission issues
Write-Host "Step 4: Clearing Vite cache to prevent permission issues" -ForegroundColor Yellow
$viteCachePath = "$PWD\ehr-vue-app\node_modules\.vite"
if (Test-Path $viteCachePath) {
    Write-Host "Found Vite cache at: $viteCachePath" -ForegroundColor Yellow
    
    try {
        # Use attrib to clear read-only attributes
        Start-Process -FilePath "cmd.exe" -ArgumentList "/c attrib -R $viteCachePath\*.* /S" -Wait -NoNewWindow
        Write-Host "Cleared read-only attributes from Vite cache files" -ForegroundColor Green

        # Remove Vite cache
        Remove-Item -Path $viteCachePath -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "Successfully removed Vite cache" -ForegroundColor Green
    }
    catch {
        Write-Host "Warning: Could not fully clear Vite cache: $_" -ForegroundColor Yellow
        Write-Host "Will continue anyway..." -ForegroundColor Yellow
    }
}

# Step 5: Starting backend services
Write-Host "Step 5: Starting backend services (Main API and Vaccine API)" -ForegroundColor Yellow
Write-Host "Starting Main API on port 8000..." -ForegroundColor Yellow
$mainApiProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/k cd /d $PWD\backend && python start_apis.py" -PassThru -WindowStyle Normal
Write-Host "Main API started with PID: $($mainApiProcess.Id)"
Start-Sleep -Seconds 5

Write-Host "Starting Vaccine API on port 8004..." -ForegroundColor Yellow
$vaccineApiProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/k cd /d $PWD\backend && python start_vaccine_server.py" -PassThru -WindowStyle Normal
Write-Host "Vaccine API started with PID: $($vaccineApiProcess.Id)"
Start-Sleep -Seconds 5

# Step 6: Check if backend services are running properly
Write-Host "Step 6: Verifying backend services" -ForegroundColor Yellow
$mainApiRunning = $false
$vaccineApiRunning = $false

try {
    $mainApiRequest = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -Method GET -TimeoutSec 5 -ErrorAction SilentlyContinue
    if ($mainApiRequest.StatusCode -eq 200) {
        Write-Host "Main API is running properly" -ForegroundColor Green
        $mainApiRunning = $true
    }
} catch {
    Write-Host "Warning: Could not verify Main API is running. Continuing anyway..." -ForegroundColor Yellow
}

try {
    $vaccineApiRequest = Invoke-WebRequest -Uri "http://localhost:8004/api/vaccines/health" -Method GET -TimeoutSec 5 -ErrorAction SilentlyContinue
    if ($vaccineApiRequest.StatusCode -eq 200) {
        Write-Host "Vaccine API is running properly" -ForegroundColor Green
        $vaccineApiRunning = $true
    }
} catch {
    Write-Host "Warning: Could not verify Vaccine API is running. Continuing anyway..." -ForegroundColor Yellow
}

# Step 7: Starting frontend service with elevated permissions
Write-Host "Step 7: Starting frontend service with elevated permissions" -ForegroundColor Yellow
Write-Host "Using Start-Process with 'RunAs' to avoid permission issues..." -ForegroundColor Yellow

try {
    # Try to use admin privileges first - this will trigger UAC
    $frontendProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/k cd /d $PWD\ehr-vue-app && npm run dev -- --port 8081 --force" -Verb RunAs -PassThru -WindowStyle Normal -ErrorAction SilentlyContinue
    Write-Host "Frontend started with PID: $($frontendProcess.Id)"
    Write-Host "Waiting for frontend to initialize (20 seconds)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 20
}
catch {
    Write-Host "Could not start frontend with elevated permissions: $_" -ForegroundColor Red
    Write-Host "Trying alternative method..." -ForegroundColor Yellow
    
    # If admin privileges fail, try regular method
    $frontendProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/k cd /d $PWD\ehr-vue-app && npm run dev -- --port 8081 --force" -PassThru -WindowStyle Normal
    Write-Host "Frontend started with PID: $($frontendProcess.Id) (without elevation)"
    Write-Host "Waiting for frontend to initialize (20 seconds)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 20
}

# Step 8: Verify frontend is running
Write-Host "Step 8: Verifying frontend is running" -ForegroundColor Yellow
$frontendRunning = $false

try {
    $frontendRequest = Invoke-WebRequest -Uri "http://localhost:8081" -Method GET -TimeoutSec 5 -ErrorAction SilentlyContinue
    if ($frontendRequest.StatusCode -eq 200) {
        Write-Host "Frontend is running properly" -ForegroundColor Green
        $frontendRunning = $true
    }
} catch {
    Write-Host "Warning: Could not verify frontend is running: $_" -ForegroundColor Red
    Write-Host "Checking if there are any error messages in the frontend console..." -ForegroundColor Yellow
    
    # Check if EPERM error is occurring
    $nodeProcs = Get-Process -Name "node" -ErrorAction SilentlyContinue
    if ($nodeProcs) {
        Write-Host "Found node processes running. Frontend might still be starting..." -ForegroundColor Yellow
    } else {
        Write-Host "No node processes found. Frontend might have failed to start." -ForegroundColor Red
    }
}

# Step 9: Installing Playwright
Write-Host "Step 9: Installing Playwright if needed" -ForegroundColor Yellow
npm install -D @playwright/test | Out-Null
npx playwright install chromium | Out-Null

# Step 10: Running tests - only if frontend is running
if ($frontendRunning) {
    Write-Host "Step 10: Running browser tests" -ForegroundColor Green
    Write-Host "----------------------------" -ForegroundColor Gray
    Write-Host "The browser window will open automatically." -ForegroundColor Cyan
    Write-Host "Screenshots will be saved to the test-results directory." -ForegroundColor Cyan
    Write-Host "----------------------------" -ForegroundColor Gray
    
    npx playwright test ehr-test-automation.js --config=ehr-playwright.config.js --headed
} else {
    Write-Host "Step 10: SKIPPED - Frontend does not appear to be running" -ForegroundColor Red
    Write-Host "Will attempt manual navigation with Playwright anyway..." -ForegroundColor Yellow
    
    npx playwright test ehr-test-automation.js --config=ehr-playwright.config.js --headed
}

# Step 11: Completion
Write-Host "Step 11: Test completed!" -ForegroundColor Green
Write-Host "Check the test-results directory for screenshots" -ForegroundColor Cyan
Write-Host "and review the console output for details." -ForegroundColor Cyan
Write-Host "----------------------------" -ForegroundColor Gray

# Ask to close services
$response = Read-Host "Press Enter to close all EHR services and exit (or type 'keep' to keep them running)"
if ($response -ne "keep") {
    Write-Host "Cleaning up - stopping all EHR services" -ForegroundColor Yellow
    
    # Stop the started processes by PID
    if ($mainApiProcess) { Stop-Process -Id $mainApiProcess.Id -Force -ErrorAction SilentlyContinue }
    if ($vaccineApiProcess) { Stop-Process -Id $vaccineApiProcess.Id -Force -ErrorAction SilentlyContinue }
    if ($frontendProcess) { Stop-Process -Id $frontendProcess.Id -Force -ErrorAction SilentlyContinue }
    
    # Additional cleanup
    Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
    Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like "*start_apis*" -or $_.MainWindowTitle -like "*start_vaccine*" } | Stop-Process -Force
    
    Write-Host "All EHR services have been stopped." -ForegroundColor Green
} 