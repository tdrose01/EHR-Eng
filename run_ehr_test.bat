@echo off
echo Creating test-results directory if it doesn't exist
if not exist "test-results" mkdir test-results

echo Installing Playwright if needed
npx playwright install chromium

echo Running EHR application browser test
npx playwright test ehr-test-automation.js --config=ehr-playwright.config.js --headed

echo Test completed. Check the test-results directory for screenshots and the console output for details. 