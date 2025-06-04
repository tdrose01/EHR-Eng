# Direct script to run vaccine test with debug output
Write-Host "Starting direct vaccine test run with additional debug info" -ForegroundColor Cyan

# Show test file location and verify it exists
$testFile = Join-Path (Get-Location).Path "tests\vaccine-test.js"
if (Test-Path $testFile) {
    Write-Host "Test file found at: $testFile" -ForegroundColor Green
} else {
    Write-Host "ERROR: Test file not found at: $testFile" -ForegroundColor Red
    exit 1
}

# Check playwright config
$configFile = Join-Path (Get-Location).Path "playwright.config.js"
if (Test-Path $configFile) {
    Write-Host "Playwright config found at: $configFile" -ForegroundColor Green
    Write-Host "Config contents:" -ForegroundColor Yellow
    Get-Content $configFile | ForEach-Object { Write-Host "  $_" }
} else {
    Write-Host "WARNING: Playwright config not found at: $configFile" -ForegroundColor Yellow
}

# Run the vaccine-test test
Write-Host "Running vaccine-test..." -ForegroundColor Cyan
Write-Host "Test File: $PWD\tests\vaccine-test.js"
Write-Host "Config: $PWD\playwright.config.js"

# Attempt to run test in different ways
try {
    # Method 1: Direct run with explicit path
    Write-Host "Running test with explicit path..." -ForegroundColor Yellow
    npx playwright test "tests/vaccine-test.js" --headed
    
    if ($LASTEXITCODE -ne 0) {
        # Method 2: Run with npm script
        Write-Host "First method failed, trying npm script..." -ForegroundColor Yellow
        npm run test:vaccine
        
        if ($LASTEXITCODE -ne 0) {
            # Method 3: Run with config parameter
            Write-Host "Second method failed, trying with config parameter..." -ForegroundColor Yellow
            npx playwright test --config=playwright.config.js "tests/vaccine-test.js" --headed
            
            if ($LASTEXITCODE -ne 0) {
                # Method 4: Try changing directory to tests and running directly
                Write-Host "Third method failed, trying direct execution from tests directory..." -ForegroundColor Yellow
                Push-Location tests
                npx playwright test "vaccine-test.js" --headed
                Pop-Location
            }
        }
    }
} catch {
    Write-Host "Error running test: $_" -ForegroundColor Red
}

# Open the HTML report if it exists
if (Test-Path "playwright-report\index.html") {
    Write-Host "Opening test report..." -ForegroundColor Cyan
    Start-Process "playwright-report\index.html"
} 