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

# Update package.json scripts
Write-Section "Updating package.json Scripts"

if (Test-Path "package.json") {
    $packageJson = Get-Content -Path "package.json" -Raw | ConvertFrom-Json
    
    # Update or add the test scripts
    if (-not $packageJson.scripts) {
        $packageJson | Add-Member -NotePropertyName "scripts" -NotePropertyValue @{}
    }
    
    $packageJson.scripts."test:minimal" = "npx playwright test tests/minimal-test.js"
    $packageJson.scripts."test:standalone" = "npx playwright test tests/standalone-test.js"
    $packageJson.scripts."test:vaccine" = "npx playwright test tests/vaccine-test.js"
    $packageJson.scripts."test:patients" = "npx playwright test tests/patients-test.js"
    $packageJson.scripts."test:e2e" = "npx playwright test tests/e2e-flow.js"
    $packageJson.scripts."test:all" = "npx playwright test tests/"
    
    $packageJson | ConvertTo-Json -Depth 10 | Set-Content -Path "package.json"
    Write-Host "Updated package.json test scripts successfully" -ForegroundColor Green
} else {
    Write-Host "package.json not found. Skipping script updates." -ForegroundColor Yellow
}

# Install or update Playwright if needed
Write-Section "Checking Playwright Installation"

try {
    $playwrightVersion = npm list @playwright/test --depth=0 2>$null
    if ($playwrightVersion -match "@playwright/test@") {
        Write-Host "Playwright is installed. Version: $($Matches[0])" -ForegroundColor Green
    } else {
        Write-Host "Installing Playwright..." -ForegroundColor Yellow
        npm install --save-dev @playwright/test
        npx playwright install chromium
    }
} catch {
    Write-Host "Error checking Playwright installation. Please run 'npm install --save-dev @playwright/test' manually." -ForegroundColor Red
}

# Test installation
Write-Section "Testing Playwright Installation"
npx playwright --version

# Give instructions to run tests
Write-Section "Instructions"
Write-Host "Configuration complete! Run tests with one of these commands:" -ForegroundColor Green
Write-Host "  - Run all tests:           npm run test:all" -ForegroundColor White
Write-Host "  - Run standalone test:     npm run test:standalone" -ForegroundColor White
Write-Host "  - Run minimal test:        npm run test:minimal" -ForegroundColor White
Write-Host "  - Run specific test:       npm run test:vaccine" -ForegroundColor White
Write-Host "  - Run with all DB tests:   .\run_db_tests.ps1 -TestType standalone" -ForegroundColor White
Write-Host ""
Write-Host "If tests are still not found, try running directly with:" -ForegroundColor Yellow
Write-Host "  npx playwright test tests/standalone-test.js --headed" -ForegroundColor White 