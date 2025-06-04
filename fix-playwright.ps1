$ErrorActionPreference = "Continue"

function Write-Section {
    param([string]$Message)
    Write-Host "`n========== $Message ==========`n" -ForegroundColor Cyan
}

Write-Section "Fixing Playwright Configuration"

# Check for the test directory
if (-not (Test-Path "tests")) {
    Write-Host "Tests directory not found. Creating it..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path "tests" -Force
}

# Count test files
$testFiles = Get-ChildItem -Path "tests" -Filter "*.js" -File
$testFilesCjs = Get-ChildItem -Path "tests" -Filter "*.cjs" -File
$totalTestFiles = $testFiles.Count + $testFilesCjs.Count

Write-Host "Found $totalTestFiles test files in tests directory" -ForegroundColor Green
foreach ($file in $testFiles + $testFilesCjs) {
    Write-Host " - $($file.Name)" -ForegroundColor Gray
}

# Update playwright.config.js
Write-Section "Updating Playwright Configuration File"

$playwrightConfig = @'
// @ts-check
const { devices } = require('@playwright/test');

/**
 * @see https://playwright.dev/docs/test-configuration
 * @type {import('@playwright/test').PlaywrightTestConfig}
 */
const config = {
  testDir: './tests',
  timeout: 30 * 1000,
  expect: {
    timeout: 5000
  },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [['html'], ['list']],
  use: {
    actionTimeout: 0,
    baseURL: 'http://localhost:8081',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
      },
    },
  ],
  outputDir: 'test-results/',
};

module.exports = config;
'@

Set-Content -Path "playwright.config.js" -Value $playwrightConfig
Write-Host "Updated playwright.config.js successfully" -ForegroundColor Green

# Create or update package.json
Write-Section "Creating package.json File"

$packageJson = @"
{
  "name": "ehr-system",
  "version": "1.0.0",
  "description": "EHR System",
  "main": "server.js",
  "scripts": {
    "test:minimal": "npx playwright test tests/minimal-test.js",
    "test:standalone": "npx playwright test tests/standalone-test.js",
    "test:vaccine": "npx playwright test tests/vaccine-test.js",
    "test:patients": "npx playwright test tests/patients-test.js",
    "test:e2e": "npx playwright test tests/e2e-flow.js",
    "test:records": "npx playwright test tests/records-test.cjs",
    "test:all": "npx playwright test tests/"
  },
  "devDependencies": {
    "@playwright/test": "^1.51.0"
  }
}
"@

Set-Content -Path "package.json" -Value $packageJson
Write-Host "Created package.json file with test scripts" -ForegroundColor Green

# Create batch/PowerShell runners for each test
Write-Section "Creating Test Runner Scripts"

$testScripts = @(
    @{
        Name = "minimal-test"
        Path = "tests/minimal-test.js"
    },
    @{
        Name = "standalone-test"
        Path = "tests/standalone-test.js"
    },
    @{
        Name = "vaccine-test"
        Path = "tests/vaccine-test.js"
    },
    @{
        Name = "patients-test"
        Path = "tests/patients-test.js"
    },
    @{
        Name = "e2e-flow"
        Path = "tests/e2e-flow.js"
    },
    @{
        Name = "records-test"
        Path = "tests/records-test.cjs"
    }
)

# Create PowerShell runners
foreach ($script in $testScripts) {
    $runnerContent = @"
# Run the ${script.Name} test
Write-Host "Running ${script.Name}..." -ForegroundColor Cyan
Write-Host "Test File: $PWD\${script.Path}"
Write-Host "Config: $PWD\playwright.config.js"

# Attempt to run test in different ways
try {
    # Method 1: Direct run with explicit path
    Write-Host "Running test with explicit path..." -ForegroundColor Yellow
    npx playwright test "${script.Path}" --headed
    
    if (`$LASTEXITCODE -ne 0) {
        # Method 2: Run with npm script
        Write-Host "First method failed, trying npm script..." -ForegroundColor Yellow
        npm run test:${script.Name.Replace(".js", "").Replace(".cjs", "")}
        
        if (`$LASTEXITCODE -ne 0) {
            # Method 3: Run with config parameter
            Write-Host "Second method failed, trying with config parameter..." -ForegroundColor Yellow
            npx playwright test --config=playwright.config.js "${script.Path}" --headed
        }
    }
} catch {
    Write-Host "Error running test: `$_" -ForegroundColor Red
}

# Open the HTML report if it exists
if (Test-Path "playwright-report\index.html") {
    Write-Host "Opening test report..." -ForegroundColor Cyan
    Start-Process "playwright-report\index.html"
}
"@
    
    $psFileName = "run_${script.Name.Replace("-", "_").Replace(".js", "").Replace(".cjs", "")}.ps1"
    Set-Content -Path $psFileName -Value $runnerContent
    Write-Host "Created $psFileName" -ForegroundColor Green
    
    # Create batch runner too
    $batchContent = @"
@echo off
echo Running ${script.Name}...
npx playwright test "${script.Path}" --headed
if %ERRORLEVEL% NEQ 0 (
    echo First attempt failed, trying with explicit config...
    npx playwright test --config=playwright.config.js "${script.Path}" --headed
)
start "" "playwright-report\index.html"
"@
    
    $batchFileName = "${script.Name.Replace(".js", "").Replace(".cjs", "")}_direct.bat"
    Set-Content -Path $batchFileName -Value $batchContent
    Write-Host "Created $batchFileName" -ForegroundColor Green
}

# Install or update Playwright if needed
Write-Section "Installing Playwright"

try {
    Write-Host "Installing Playwright and dependencies..." -ForegroundColor Yellow
    npm install --save-dev @playwright/test
    npx playwright install chromium
} catch {
    Write-Host "Error installing Playwright: $_" -ForegroundColor Red
    Write-Host "Please run these commands manually:" -ForegroundColor Yellow
    Write-Host "  npm install --save-dev @playwright/test" -ForegroundColor White
    Write-Host "  npx playwright install chromium" -ForegroundColor White
}

# Test installation
Write-Section "Testing Playwright Installation"
npx playwright --version

# Create test.bat for quick running
$testBatch = @"
@echo off
echo === Running Standalone Test ===
npx playwright test tests/standalone-test.js --headed
if %ERRORLEVEL% NEQ 0 (
    echo === Running Minimal Test ===
    npx playwright test tests/minimal-test.js --headed
)
"@
Set-Content -Path "test.bat" -Value $testBatch

# Give instructions to run tests
Write-Section "Instructions"
Write-Host "Configuration complete! Run tests with one of these commands:" -ForegroundColor Green
Write-Host "  - Quick test:              .\test.bat" -ForegroundColor White
Write-Host "  - Run all tests:           npm run test:all" -ForegroundColor White
Write-Host "  - Run standalone test:     .\run_standalone_test.ps1" -ForegroundColor White
Write-Host "  - Run minimal test:        .\run_minimal_test.ps1" -ForegroundColor White
Write-Host "  - Run specific test:       .\run_vaccine_test.ps1" -ForegroundColor White
Write-Host "  - Run with DB tests:       .\run_db_tests.ps1 -TestType standalone" -ForegroundColor White
Write-Host ""
Write-Host "Or use batch files for direct execution:" -ForegroundColor Yellow
Write-Host "  standalone_test_direct.bat" -ForegroundColor White
Write-Host "  minimal_test_direct.bat" -ForegroundColor White 