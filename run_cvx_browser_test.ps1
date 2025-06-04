# PowerShell script to run browser automation tests for CVX codes
param (
    [Parameter()]
    [string]$TestFile = "test_cvx_browser_automation.js"
)

$ErrorActionPreference = "Stop"

# Function to check if Node.js is installed
function Check-NodeInstallation {
    try {
        $nodeVersion = & node --version
        Write-Host "Found Node.js version: $nodeVersion" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "Node.js is not installed or not in PATH" -ForegroundColor Red
        return $false
    }
}

# Function to check if Playwright is installed
function Check-PlaywrightInstallation {
    try {
        $result = & npx playwright --version
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Found Playwright: $result" -ForegroundColor Green
            return $true
        } else {
            Write-Host "Playwright CLI not found" -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host "Could not check Playwright installation" -ForegroundColor Yellow
        return $false
    }
}

# Function to install Playwright if needed
function Install-Playwright {
    Write-Host "Installing Playwright..." -ForegroundColor Yellow
    & npm init -y
    & npm install -D @playwright/test
    & npx playwright install chromium
}

# Main script execution
Write-Host "Starting CVX Code Browser Automation Test" -ForegroundColor Cyan

# Verify Node.js installation
if (-not (Check-NodeInstallation)) {
    Write-Host "Please install Node.js and try again" -ForegroundColor Red
    exit 1
}

# Check if the backend API server is running
Write-Host "Checking if backend API server is running..." -ForegroundColor Cyan
try {
    $result = Invoke-RestMethod -Uri "http://localhost:5000/api/vaccines/test" -Method GET -ErrorAction SilentlyContinue
    Write-Host "Backend API server is running" -ForegroundColor Green
} catch {
    Write-Host "Backend API server does not appear to be running" -ForegroundColor Yellow
    $startServer = Read-Host "Do you want to start the API server? (y/n)"
    if ($startServer -eq "y") {
        Write-Host "Starting backend API server..." -ForegroundColor Yellow
        Start-Process -FilePath "powershell" -ArgumentList "-Command cd backend && python -m api.vaccine_api" -WindowStyle Hidden
        # Give the server a moment to start
        Start-Sleep -Seconds 5
    }
}

# Check if frontend is running
Write-Host "Checking if frontend is running..." -ForegroundColor Cyan
$frontendRunning = $false
$ports = @(5173, 8080, 8081, 3000)
foreach ($port in $ports) {
    try {
        $result = Invoke-WebRequest -Uri "http://localhost:$port" -Method HEAD -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($result.StatusCode -eq 200) {
            Write-Host "Frontend is running on port $port" -ForegroundColor Green
            $frontendRunning = $true
            break
        }
    } catch {
        # Continue to next port
    }
}

if (-not $frontendRunning) {
    Write-Host "Frontend does not appear to be running" -ForegroundColor Yellow
    $startFrontend = Read-Host "Do you want to try to start the frontend? (y/n)"
    if ($startFrontend -eq "y") {
        Write-Host "Starting frontend..." -ForegroundColor Yellow
        Start-Process -FilePath "powershell" -ArgumentList "-Command cd ehr-vue-app && npm run dev" -WindowStyle Hidden
        # Give the frontend a moment to start
        Start-Sleep -Seconds 10
    }
}

# Verify Playwright installation
if (-not (Check-PlaywrightInstallation)) {
    Write-Host "Playwright not found, installing..." -ForegroundColor Yellow
    Install-Playwright
}

# Check and clean test results directory
$testResultsDir = ".\cvx-test-results"
Write-Host "Cleaning up test results directory..." -ForegroundColor Cyan
if (Test-Path $testResultsDir) {
    try {
        Remove-Item -Path "$testResultsDir\*" -Recurse -Force -ErrorAction SilentlyContinue
    } catch {
        Write-Host "Warning: Could not clean test results directory completely. Some files may be locked." -ForegroundColor Yellow
    }
} else {
    New-Item -Path $testResultsDir -ItemType Directory | Out-Null
}

# Run the test with custom results directory
Write-Host "Running browser automation test for CVX codes..." -ForegroundColor Cyan
& npx playwright test $TestFile --config playwright.cvx.config.js --output $testResultsDir

$testResult = $LASTEXITCODE

# Open the test report
if (Test-Path "$testResultsDir\playwright-report\index.html") {
    Write-Host "Opening test report..." -ForegroundColor Cyan
    Start-Process "$testResultsDir\playwright-report\index.html"
} else {
    Write-Host "Test report not found at expected location" -ForegroundColor Yellow
}

if ($testResult -eq 0) {
    Write-Host "Browser automation test completed successfully!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "Browser automation test failed with exit code $testResult" -ForegroundColor Red
    exit $testResult
} 