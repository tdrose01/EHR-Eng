# EHR Full Test Suite in PowerShell
Write-Host "EHR Application Full Test Suite" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

# Step 1: Create test-results directory
Write-Host "Step 1: Creating test-results directory if it doesn't exist" -ForegroundColor Yellow
if (-not (Test-Path "test-results")) {
    New-Item -ItemType Directory -Path "test-results" | Out-Null
}

# Step 2: Kill any running EHR processes
Write-Host "Step 2: Killing any running EHR processes" -ForegroundColor Yellow
Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like "*ehr-vue-app*" } | Stop-Process -Force
Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like "*EHR API*" } | Stop-Process -Force

# Check if port 8000 is in use and release it if necessary
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

# Step 3: Starting backend services
Write-Host "Step 3: Starting backend services (Main API and Vaccine API)" -ForegroundColor Yellow
$mainApiProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/k cd /d $PWD\backend && python start_apis.py" -PassThru -WindowStyle Normal
Write-Host "Main API started with PID: $($mainApiProcess.Id)"
Start-Sleep -Seconds 5

$vaccineApiProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/k cd /d $PWD\backend && python start_vaccine_server.py" -PassThru -WindowStyle Normal
Write-Host "Vaccine API started with PID: $($vaccineApiProcess.Id)"
Start-Sleep -Seconds 5

# Step 4: Starting frontend service
Write-Host "Step 4: Starting frontend service" -ForegroundColor Yellow
$frontendProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/k cd /d $PWD\ehr-vue-app && npm run dev -- --port 8081 --force" -PassThru -WindowStyle Normal
Write-Host "Frontend started with PID: $($frontendProcess.Id)"
Write-Host "Waiting for frontend to initialize (15 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Step 5: Installing Playwright
Write-Host "Step 5: Installing Playwright if needed" -ForegroundColor Yellow
npm install -D @playwright/test | Out-Null
npx playwright install chromium | Out-Null

# Step 6: Running tests
Write-Host "Step 6: Running browser tests" -ForegroundColor Green
Write-Host "----------------------------" -ForegroundColor Gray
Write-Host "The browser window will open automatically." -ForegroundColor Cyan
Write-Host "Screenshots will be saved to the test-results directory." -ForegroundColor Cyan
Write-Host "----------------------------" -ForegroundColor Gray

npx playwright test ehr-test-automation.js --config=ehr-playwright.config.js --headed

# Step 7: Completion
Write-Host "Step 7: Test completed!" -ForegroundColor Green
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
    Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like "*ehr-vue-app*" } | Stop-Process -Force
    Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like "*EHR API*" } | Stop-Process -Force
} 