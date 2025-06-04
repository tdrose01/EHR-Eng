# EHR System Automated Testing Suite

This directory contains automated tests for the EHR System using Playwright for end-to-end testing and PostgreSQL validation.

## Test Structure

The test suite is organized as follows:

- `patients-test.js` - Tests for patient management functionality with PostgreSQL validation
- `vaccine-test.js` - Tests for vaccine management functionality
- `e2e-flow.js` - End-to-end tests for the complete patient-records-vaccine workflow
- `records-test.cjs` - Tests for medical records functionality
- `simple-records-test.js` - Basic tests for the records page

## Prerequisites

1. PostgreSQL server running with the correct EHR database initialized
2. Node.js and npm installed
3. Required npm packages (`npm install` in the root directory)
4. EHR System properly configured

## Running Tests

### Using the Automation Script

The simplest way to run all tests is using the PowerShell automation script:

```powershell
# Run all tests (starts and stops the EHR system automatically)
.\run-tests.ps1

# Run specific test suite
.\run-tests.ps1 -TestType patients
.\run-tests.ps1 -TestType records
.\run-tests.ps1 -TestType vaccine
.\run-tests.ps1 -TestType e2e

# Run tests without starting/stopping the EHR system
.\run-tests.ps1 -SkipStartup

# Keep the EHR system running after tests
.\run-tests.ps1 -KeepRunning
```

### Manual Test Running

You can also run tests manually:

1. Ensure the EHR system is running (`.\ehr_manager.ps1 start`)
2. Run the desired test command:

```bash
# Run all tests
npm run test

# Run specific test suites
npm run test:patients
npm run test:records
npm run test:vaccine
npm run test:e2e

# Run tests with UI mode (interactive)
npm run test:ui
```

## Test Artifacts

- Screenshots will be saved in the project root directory
- The Playwright HTML report will be available in `playwright-report/index.html`
- Test results will be saved in the `test-results` directory

## Database Validation

Several tests validate UI data against the PostgreSQL database. For this to work:

1. PostgreSQL must be running
2. The database connection string in the test files must be correct
3. The `psql` command-line tool must be available in your PATH

The default connection string is:
```
postgresql://postgres:postgres@localhost:5432/ehr_test
```

Edit the test files if your connection details are different.

## Troubleshooting

If tests fail:

1. Check the Playwright report for details on failures
2. Verify all EHR services are running correctly (`.\ehr_manager.ps1 status`)
3. Check the PostgreSQL connection
4. Look for screenshots generated during failed tests
5. Check console output for error messages

## Headless vs. Headed Mode

By default, tests run in headed mode (visible browser). To run in headless mode, modify the `playwright.config.js` file and set `headless: true`. 