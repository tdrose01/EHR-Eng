# Browser Automation Testing Guide

This document provides instructions for setting up and running browser automation tests for the EHR system using Playwright.

## Overview

The browser automation tests validate the end-to-end functionality of the EHR application, ensuring that:

1. The frontend properly loads and renders
2. Authentication works correctly
3. Navigation between pages functions as expected
4. Patient data is correctly displayed
5. The application gracefully handles logout

## Prerequisites

Before running the browser tests, ensure you have:

1. Node.js installed (v16+)
2. The backend servers running
3. The frontend development server running
4. Properly configured environment variables

## Setup

1. Install dependencies:

```bash
cd ehr-vue-app
npm install
```

2. Install Playwright browsers:

```bash
npx playwright install chromium
```

## Running the Tests

1. Ensure the backend servers are running:

```bash
cd backend
python scripts/run_server.py
```

2. In a separate terminal, start the frontend server:

```bash
cd ehr-vue-app
npm run dev
```

3. Run the browser tests:

```bash
cd ehr-vue-app
npm run test:browser
```

## Test Details

The test script (`scripts/test_connection.js`) performs the following checks:

### Test 1: Frontend Loading
- Verifies that the frontend application loads correctly
- Checks that the page title is correctly displayed

### Test 2: Login Functionality
- Navigates to the login page if not already there
- Submits login credentials (testuser/password)
- Verifies successful login by checking for dashboard or patient list

### Test 3: Patient List
- Navigates to the patient list page
- Verifies the patient table is displayed
- Counts the number of patients displayed

### Test 4: Patient Details
- Clicks on the first patient in the list
- Verifies the patient details page loads correctly
- Checks that patient information is displayed

### Test 5: Navigation
- Tests navigation back to the patient list page
- Verifies correct page rendering after navigation

### Test 6: Logout
- Tests the logout functionality
- Verifies redirection to login page after logout

## Troubleshooting

### Common Issues

1. **Tests can't connect to the frontend**
   - Verify the frontend server is running
   - Check the port configuration in the test script (default: 8081)
   - Ensure there are no network restrictions

2. **Authentication failures**
   - Verify the backend authentication server is running
   - Check the test user credentials in the database
   - Inspect network requests for API errors

3. **Element not found errors**
   - The application structure may have changed
   - Update the selectors in the test script
   - Increase timeouts for slow connections

### Debugging

For visual debugging:

1. Set `headless: false` in the test script (already configured)
2. Use `slowMo` parameter to slow down operations (already set to 100ms)
3. Add `await page.pause()` at specific points in the test to pause execution

For failure analysis:

- The test automatically captures a screenshot on failure named `test-failure.png`
- Check the console output for detailed error messages

## Extending the Tests

To add new tests:

1. Follow the pattern in the existing test script
2. Add clear console logging for each test step
3. Use try/catch blocks for proper error handling
4. Verify each step with appropriate assertions

## Continuous Integration

These tests can be integrated into a CI pipeline by:

1. Setting `headless: true` in the test configuration
2. Ensuring proper environment variables are set in the CI environment
3. Adding the test command to your CI configuration file 