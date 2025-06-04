# Run the  test
Write-Host "Running ..." -ForegroundColor Cyan
Write-Host "Test File: C:\tom\"
Write-Host "Config: C:\tom\playwright.config.js"

# Attempt to run test in different ways
try {
    # Method 1: Direct run with explicit path
    Write-Host "Running test with explicit path..." -ForegroundColor Yellow
    npx playwright test "" --headed
    
    if ($LASTEXITCODE -ne 0) {
        # Method 2: Run with npm script
        Write-Host "First method failed, trying npm script..." -ForegroundColor Yellow
        npm run test:
        
        if ($LASTEXITCODE -ne 0) {
            # Method 3: Run with config parameter
            Write-Host "Second method failed, trying with config parameter..." -ForegroundColor Yellow
            npx playwright test --config=playwright.config.js "" --headed
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
