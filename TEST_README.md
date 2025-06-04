# EHR System Test Framework

This document explains the test setup and scripts created to run Playwright tests reliably in the EHR system.

## Test Configuration

The main test configuration is in `playwright.config.js` which has been updated to:
- Set the test directory to `./tests`
- Configure timeouts, reporters, and browser settings
- Include proper screenshot and video capture settings

## Test Scripts

We've created multiple scripts to facilitate test execution:

### PowerShell Setup Scripts

- `fix-playwright.ps1`: Comprehensive script that:
  - Updates the Playwright configuration
  - Creates package.json with test scripts
  - Generates test runner scripts
  - Installs Playwright dependencies
  - Creates batch files for direct execution

- `fix_vaccine_test.ps1`: Script that:
  - Creates a backup of the vaccine test
  - Updates the file with proper structure
  - Creates a simplified version of the test

### Test Runner Scripts

#### PowerShell Runners

- `run_vaccine_test.ps1`: Runs the vaccine test using multiple approaches:
  - Direct execution with explicit path
  - Using npm script
  - With config parameter
  - From within the tests directory

- `run_standalone_test.ps1`: Similar runner for the standalone test
- `run_minimal_test.ps1`: Runner for the minimal test

#### Batch Runners

- `vaccine_test_direct.bat`: Direct execution of the vaccine test
- `standalone_test_direct.bat`: Direct execution of the standalone test
- `minimal_test_direct.bat`: Direct execution of the minimal test
- `test.bat`: Quick runner that tries multiple tests

### Database Test Runner

- `run_db_tests.ps1`: Updated script that:
  - Stops and starts the EHR system
  - Verifies PostgreSQL connection
  - Runs tests directly with npx
  - Shows test results and opens the report

## Test Files

Several test files are available:

- `tests/vaccine-test.js`: Main vaccine test file
- `tests/simple-vaccine-test.js`: Simplified version of the vaccine test
- `tests/standalone-test.js`: Basic navigation test
- `tests/minimal-test.js`: Minimal test example
- `tests/patients-test.js`: Tests for patient functionality
- `tests/e2e-flow.js`: End-to-end flow tests
- `tests/records-test.cjs`: Medical records tests

## How to Run Tests

1. **Run the setup script first**:
   ```
   .\fix-playwright.ps1
   ```

2. **Run tests using one of these methods**:

   - Quick test (try multiple tests):
     ```
     .\test.bat
     ```

   - Run a specific test with PowerShell script:
     ```
     .\run_vaccine_test.ps1
     .\run_standalone_test.ps1
     .\run_minimal_test.ps1
     ```

   - Run directly with batch files:
     ```
     .\vaccine_test_direct.bat
     .\standalone_test_direct.bat
     .\minimal_test_direct.bat
     ```

   - Run with npm scripts:
     ```
     npm run test:vaccine
     npm run test:standalone
     npm run test:minimal
     npm run test:all
     ```

   - Run with database setup:
     ```
     .\run_db_tests.ps1 -TestType standalone
     .\run_db_tests.ps1 -TestType vaccine
     .\run_db_tests.ps1 -TestType minimal
     .\run_db_tests.ps1 -TestType all
     ```

3. **Troubleshooting**:

   If tests are still not found, try:
   
   - Checking the test directory structure:
     ```
     Get-ChildItem -Path tests -Recurse
     ```
     
   - Verifying Playwright installation:
     ```
     npx playwright --version
     ```
     
   - Reinstalling Playwright:
     ```
     npm install --save-dev @playwright/test
     npx playwright install chromium
     ```

## Viewing Test Results

Test reports are generated in the `playwright-report` directory. The test scripts will automatically open the HTML report after test completion.

If you want to open the report manually:
```
Start-Process "playwright-report\index.html"
``` 