# PowerShell script for fully automated CVX browser test
$ErrorActionPreference = "Stop"

# Configuration
$testDir = "./cvx-auto-test"
$testFile = "test_cvx_auto.js"
$apiPort = 5000
$frontendPort = 8080

Write-Host "Starting Automated CVX Browser Test" -ForegroundColor Cyan

# Clean up previous test results
if (Test-Path $testDir) {
    Write-Host "Cleaning up previous test results..." -ForegroundColor Yellow
    Remove-Item -Path "$testDir" -Recurse -Force -ErrorAction SilentlyContinue
}

# Create test directory
New-Item -Path $testDir -ItemType Directory -Force | Out-Null
New-Item -Path "$testDir/screenshots" -ItemType Directory -Force | Out-Null
New-Item -Path "$testDir/results" -ItemType Directory -Force | Out-Null

# Kill any existing processes
Write-Host "Killing any existing browser processes..." -ForegroundColor Yellow
Get-Process | Where-Object { $_.Name -like "*chrome*" -or $_.Name -like "*chromium*" } | Stop-Process -Force -ErrorAction SilentlyContinue

# Start backend API server
Write-Host "Starting backend API server..." -ForegroundColor Yellow
$apiProcess = Start-Process -FilePath "powershell" -ArgumentList "-Command cd backend && python -m api.vaccine_api" -WindowStyle Hidden -PassThru

# Give the server time to start
Write-Host "Waiting for API server to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start frontend server
Write-Host "Starting frontend server..." -ForegroundColor Yellow
$frontendProcess = Start-Process -FilePath "powershell" -ArgumentList "-Command cd ehr-vue-app && npm run dev" -WindowStyle Hidden -PassThru

# Give the frontend time to start
Write-Host "Waiting for frontend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Run the test
Write-Host "Running browser automation test..." -ForegroundColor Cyan
try {
    # Create a minimal package.json for this test
    $packageJson = @"
{
  "name": "cvx-auto-test",
  "version": "1.0.0",
  "type": "module",
  "dependencies": {
    "@playwright/test": "^1.40.0"
  }
}
"@
    $packageJson | Out-File -FilePath "$testDir/package.json" -Encoding utf8

    # Create a minimal playwright.config.js
    $playwrightConfig = @"
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './',
  timeout: 60000,
  expect: { timeout: 10000 },
  fullyParallel: false,
  reporter: 'html',
  outputDir: './results',
  use: {
    actionTimeout: 0,
    baseURL: 'http://localhost:$frontendPort',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
"@
    $playwrightConfig | Out-File -FilePath "$testDir/playwright.config.js" -Encoding utf8

    # Copy the test file
    Copy-Item $testFile -Destination "$testDir/$testFile"

    # Change to the test directory
    Set-Location $testDir

    # Install dependencies
    & npm install --no-fund --loglevel=error
    & npx playwright install chromium --with-deps

    # Run the test
    & npx playwright test $testFile --config playwright.config.js
    $testResult = $LASTEXITCODE

    # Display the report
    if (Test-Path "./playwright-report/index.html") {
        Write-Host "Test report available at: $((Get-Location).Path)/playwright-report/index.html" -ForegroundColor Cyan
        Start-Process "./playwright-report/index.html"
    }
} catch {
    Write-Host "Error running test: $_" -ForegroundColor Red
    $testResult = 1
} finally {
    # Return to the original directory
    Set-Location ".."
    
    # Stop the API and frontend processes
    if ($apiProcess -and !$apiProcess.HasExited) {
        Write-Host "Stopping API server..." -ForegroundColor Yellow
        Stop-Process -Id $apiProcess.Id -Force -ErrorAction SilentlyContinue
    }
    
    if ($frontendProcess -and !$frontendProcess.HasExited) {
        Write-Host "Stopping frontend server..." -ForegroundColor Yellow
        Stop-Process -Id $frontendProcess.Id -Force -ErrorAction SilentlyContinue
    }
}

if ($testResult -eq 0) {
    Write-Host "Test completed successfully!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "Test failed with exit code $testResult" -ForegroundColor Red
    exit $testResult
} 