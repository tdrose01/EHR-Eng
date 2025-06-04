# Script to run minimal test
Write-Host "Running minimal test to verify Playwright setup..." -ForegroundColor Cyan

# Remove any existing Playwright cache that might be corrupted
if (Test-Path ".playwright") {
    Write-Host "Removing Playwright cache directory..." -ForegroundColor Yellow
    Remove-Item -Path ".playwright" -Recurse -Force -ErrorAction SilentlyContinue
}

# Verify exact file path
$minimalTestFile = Join-Path (Get-Location).Path "tests\minimal-test.js"
Write-Host "Test file path: $minimalTestFile" -ForegroundColor Green

# Try running with an explicit file pattern
Write-Host "`nAttempting to run minimal test with direct path..." -ForegroundColor Cyan
npx playwright test "$minimalTestFile" --headed

# Alternative approach with different command structure
if ($LASTEXITCODE -ne 0) {
    Write-Host "`nFirst attempt failed, trying alternative approach..." -ForegroundColor Yellow
    
    # Try running with node directly
    Write-Host "Running with node directly..." -ForegroundColor Cyan
    npx playwright test --config=playwright.config.js tests/minimal-test.js --headed
}

# One more attempt with maximally explicit options if needed
if ($LASTEXITCODE -ne 0) {
    Write-Host "`nStill failed, trying one more approach..." -ForegroundColor Yellow
    
    # Try with different test runner command and explicit project
    cd tests
    npx playwright test minimal-test.js --headed --project=chromium
}

# Final fallback to just list the test files
if ($LASTEXITCODE -ne 0) {
    Write-Host "`nList all test files for debugging..." -ForegroundColor Yellow
    Get-ChildItem -Path "tests" -Filter "*.js" | ForEach-Object { Write-Host $_.FullName }
} 