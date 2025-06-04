# CVX Code Browser Automation Test

This directory contains a browser automation test for verifying the CVX code auto-population functionality in the EHR system. The test uses Playwright to simulate user interactions with the system and verify that CVX codes are correctly populated when creating vaccine records.

## Test Overview

The test performs the following steps:

1. Logs into the EHR system
2. Navigates to the patients page
3. Selects a patient
4. Creates a new vaccination record
5. Verifies that the CVX code is automatically populated based on the selected vaccine

## Files

- `test_cvx_browser_automation.js` - The Playwright test that simulates user interaction with the EHR system
- `playwright.cvx.config.js` - Playwright configuration file specific to these tests
- `run_cvx_browser_test.ps1` - PowerShell script to run the test and manage required services
- `cvx-test-package.json` - NPM package file with required dependencies

## Prerequisites

- Node.js (v14 or later)
- npm 
- Python 3.6+
- PowerShell 5+

## Running the Tests

You can run the tests using the PowerShell script:

```powershell
.\run_cvx_browser_test.ps1
```

The script will:
1. Check if the backend API server is running and offer to start it if not
2. Check if the frontend is running and offer to start it if not
3. Install Playwright if it's not already installed
4. Run the tests
5. Open the report when complete

## Running Tests Manually

If you prefer to run the tests manually:

1. Start the backend API server:
   ```
   cd backend && python -m api.vaccine_api
   ```

2. Start the frontend:
   ```
   cd ehr-vue-app && npm run dev
   ```

3. Install dependencies:
   ```
   npm install
   ```

4. Run the test:
   ```
   npx playwright test test_cvx_browser_automation.js --config playwright.cvx.config.js
   ```

5. View the report:
   ```
   npx playwright show-report
   ```

## Headed Mode

To see the browser while tests are running:

```
npx playwright test test_cvx_browser_automation.js --config playwright.cvx.config.js --headed
```

## Test Results

Test results are stored in the `playwright-report` directory. You can view them by opening `playwright-report/index.html` in your browser.

## Troubleshooting

- **Test cannot connect to the frontend**: Make sure the frontend is running on one of the expected ports (5173, 8080, 8081, 3000)
- **Test cannot connect to the API**: Make sure the API server is running on port 5000
- **Login fails**: Check that the correct credentials are configured in the test file
- **CVX code is not populated**: Verify that the database has been set up correctly with CVX codes 