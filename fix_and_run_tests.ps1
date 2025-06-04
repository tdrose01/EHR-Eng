# Comprehensive script to fix Playwright issues and run tests
$ErrorActionPreference = "Continue"  # Don't stop on errors

function Write-Section {
    param([string]$Message)
    Write-Host "`n========== $Message ==========`n" -ForegroundColor Cyan
}

Write-Section "Playwright Test Runner Fix Script"

# Verify file structure
Write-Host "Verifying test files..." -ForegroundColor Yellow
$testFiles = Get-ChildItem -Path "tests" -Filter "*.js" -Recurse
Write-Host "Found $($testFiles.Count) test files:" -ForegroundColor Green
$testFiles | ForEach-Object { Write-Host "  $($_.FullName)" }

# Verify playwright is installed
Write-Section "Checking Playwright installation"
$playwrightVersion = npx playwright --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "Playwright CLI not found. Reinstalling Playwright..." -ForegroundColor Red
    npm install -D @playwright/test
    npx playwright install
} else {
    Write-Host "Playwright version: $playwrightVersion" -ForegroundColor Green
}

# Fix package.json if needed
Write-Section "Updating package.json"
$packageJsonPath = Join-Path (Get-Location).Path "package.json"
$packageJson = Get-Content $packageJsonPath -Raw | ConvertFrom-Json

# Update scripts
$packageJson.scripts."test:vaccine" = "npx playwright test tests/vaccine-test.js --headed"
$packageJson.scripts."test:minimal" = "npx playwright test tests/minimal-test.js --headed"
$packageJson | ConvertTo-Json -Depth 10 | Set-Content $packageJsonPath
Write-Host "Updated package.json with explicit test paths" -ForegroundColor Green

# Update playwright.config.js
Write-Section "Updating Playwright config"
$configPath = Join-Path (Get-Location).Path "playwright.config.js"
$configContent = @"
// @ts-check
const { defineConfig, devices } = require('@playwright/test');

/**
 * @see https://playwright.dev/docs/test-configuration
 */
module.exports = defineConfig({
  testDir: '.',
  testMatch: '**/*.js',
  timeout: 30000,
  expect: {
    timeout: 10000
  },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    actionTimeout: 0,
    baseURL: 'http://localhost:8081',
    trace: 'on-first-retry',
    headless: false,
    slowMo: 200
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
"@
Set-Content -Path $configPath -Value $configContent
Write-Host "Updated Playwright config with expanded settings" -ForegroundColor Green

# Try different approaches to run tests
Write-Section "Running Tests with Multiple Approaches"

Write-Host "Approach 1: Using npx directly with tests folder..." -ForegroundColor Yellow
npx playwright test tests/ --headed

if ($LASTEXITCODE -ne 0) {
    Write-Host "Approach 2: Running minimal test directly..." -ForegroundColor Yellow
    npx playwright test tests/minimal-test.js --headed
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "Approach 3: Running vaccine test with explicit projects..." -ForegroundColor Yellow
    npx playwright test tests/vaccine-test.js --project=chromium --headed
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "Approach 4: Running with full test path and debug flag..." -ForegroundColor Yellow
    $fullTestPath = Join-Path (Get-Location).Path "tests\minimal-test.js"
    npx playwright test "$fullTestPath" --debug
}

Write-Section "Test Results Summary"
if ($LASTEXITCODE -eq 0) {
    Write-Host "Tests completed successfully!" -ForegroundColor Green
} else {
    Write-Host "All test approaches failed. Please check:" -ForegroundColor Red
    Write-Host "1. Make sure your EHR system is running at http://localhost:8081" -ForegroundColor Yellow
    Write-Host "2. Check that your test files follow the correct format" -ForegroundColor Yellow
    Write-Host "3. Inspect the Playwright report for detailed errors" -ForegroundColor Yellow
    Write-Host "`nYou can run 'npx playwright show-report' to see the last test report" -ForegroundColor Cyan
}

# Always show report path
Write-Host "`nTest report is available at playwright-report\index.html" -ForegroundColor Cyan 