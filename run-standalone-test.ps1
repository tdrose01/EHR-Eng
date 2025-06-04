# PowerShell script to run the standalone CVX test
$ErrorActionPreference = "Stop"

Write-Host @"

=====================================================
CVX CODE BROWSER AUTOMATION TEST
=====================================================

This test will validate that the CVX code auto-population 
feature is working correctly in the browser interface.

The test will:
1. Start the backend API and frontend servers
2. Open a browser window and navigate to the login page
3. Log in as the admin user
4. Navigate to the patients page
5. Select a patient
6. Create a vaccination record
7. Verify that the CVX code is auto-populated
8. Save the record

Screenshots will be captured at each step for documentation.

=====================================================

"@ -ForegroundColor Cyan

# Function to verify frontend is running
function Test-Frontend {
    param (
        [int[]]$ports = @(4173, 8081),
        [int]$maxRetries = 5
    )
    
    foreach ($port in $ports) {
        Write-Host "Verifying frontend server on port $($port)..." -ForegroundColor Yellow
        
        for ($i = 1; $i -le $maxRetries; $i++) {
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:$($port)" -Method HEAD -TimeoutSec 2 -ErrorAction SilentlyContinue
                if ($response.StatusCode -eq 200) {
                    Write-Host "Frontend server verified on port $($port)" -ForegroundColor Green
                    return $true
                }
            } catch {
                Write-Host "Attempt $($i) of $($maxRetries) on port $($port) - Frontend not responding yet" -ForegroundColor Yellow
                Start-Sleep -Seconds 2
            }
        }
        
        Write-Host "Could not verify frontend server on port $($port)" -ForegroundColor Yellow
    }
    
    Write-Host "Could not verify frontend server on any port" -ForegroundColor Red
    return $false
}

# Create a temporary directory for the test
$testDir = ".\cvx-standalone-test"
if (Test-Path $testDir) {
    Write-Host "Cleaning up previous test directory..." -ForegroundColor Yellow
    Remove-Item -Path "$testDir" -Recurse -Force -ErrorAction SilentlyContinue
}

# Create test directory
New-Item -Path $testDir -ItemType Directory -Force | Out-Null

# Create package.json
$packageJson = @"
{
  "name": "cvx-standalone-test",
  "version": "1.0.0",
  "dependencies": {
    "puppeteer": "^21.0.0"
  }
}
"@
$packageJson | Out-File -FilePath "$testDir/package.json" -Encoding utf8

# Copy the test file
Copy-Item "standalone-cvx-test.js" -Destination "$testDir/standalone-cvx-test.js"

# Change to the test directory
Set-Location $testDir

# Install dependencies
Write-Host "Installing puppeteer..." -ForegroundColor Yellow
& npm install --no-fund --loglevel=error

# Make sure backend API is running
Write-Host "Starting backend API..." -ForegroundColor Yellow
$apiProcess = Start-Process -FilePath "powershell" -ArgumentList "-Command cd ../backend && python -m api.vaccine_api" -WindowStyle Hidden -PassThru
Start-Sleep -Seconds 5

# Make sure frontend is running
Write-Host "Starting frontend..." -ForegroundColor Yellow
$frontendProcess = Start-Process -FilePath "powershell" -ArgumentList "-Command cd ../ehr-vue-app && npm run preview" -WindowStyle Hidden -PassThru

# Verify frontend is running
$frontendReady = Test-Frontend -maxRetries 10
if (-not $frontendReady) {
    Write-Host "Frontend server failed to start properly. Please check the server logs." -ForegroundColor Red
    exit 1
}

try {
    # Run the test
    Write-Host "Running CVX code test..." -ForegroundColor Cyan
    & node standalone-cvx-test.js
    $testResult = $LASTEXITCODE
    
    if ($testResult -ne 0) {
        Write-Host "Test failed. Checking server status..." -ForegroundColor Yellow
        Test-Frontend -maxRetries 1
    }
} catch {
    Write-Host "Error running test: $_" -ForegroundColor Red
    $testResult = 1
} finally {
    # Always go back to original directory
    Set-Location ".."
    
    # Stop the processes we started
    if ($apiProcess -and !$apiProcess.HasExited) {
        Write-Host "Stopping API server..." -ForegroundColor Yellow
        Stop-Process -Id $apiProcess.Id -Force -ErrorAction SilentlyContinue
    }
    
    if ($frontendProcess -and !$frontendProcess.HasExited) {
        Write-Host "Stopping frontend server..." -ForegroundColor Yellow
        Stop-Process -Id $frontendProcess.Id -Force -ErrorAction SilentlyContinue
    }
}

# Display test result
if ($testResult -eq 0) {
    Write-Host "✅ Test completed successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Test failed with exit code $testResult" -ForegroundColor Red
}

# Show the screenshots
Write-Host "Screenshots are available in $testDir" -ForegroundColor Cyan
Get-ChildItem -Path "$testDir" -Filter "*.png" | ForEach-Object {
    Write-Host "  $_" -ForegroundColor Gray
} 