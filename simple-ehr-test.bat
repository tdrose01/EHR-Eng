@echo off
echo EHR Simple End-to-End Test
echo =========================

REM Kill any existing node processes
echo Terminating existing Node.js processes...
taskkill /F /IM node.exe >nul 2>&1

REM Clear the test-results directory
echo Clearing test-results directory...
if exist "test-results" rmdir /s /q test-results
mkdir test-results

REM Start the backend API in a new window
echo Starting backend API...
start "Backend API" cmd /c "cd backend && python start_apis.py > ..\test-results\backend-log.txt 2>&1"
timeout /t 5 /nobreak

REM Start the frontend in a new window using the command that skips Vite's cache
echo Starting frontend (with no-cache option)...
start "Frontend" cmd /c "cd ehr-vue-app && npm run dev -- --port 8081 --force --no-cache > ..\test-results\frontend-log.txt 2>&1"
timeout /t 15 /nobreak

REM Install Playwright if needed
echo Installing Playwright...
call npm install -D @playwright/test > test-results\playwright-install.log 2>&1
call npx playwright install chromium > test-results\playwright-install-chromium.log 2>&1

REM Create a minimal test script
echo Creating minimal test script...
echo // Simple EHR test > simple-test.js
echo const { test } = require('@playwright/test'); >> simple-test.js
echo test('Simple EHR test', async ({ page }) => { >> simple-test.js
echo   console.log('Starting test...'); >> simple-test.js
echo   await page.goto('http://localhost:8081'); >> simple-test.js
echo   await page.screenshot({ path: './test-results/homepage.png' }); >> simple-test.js
echo   const dashboardLink = await page.locator('a[href="/dashboard"], text=Dashboard').first(); >> simple-test.js
echo   if (await dashboardLink.isVisible()) { >> simple-test.js
echo     await dashboardLink.click(); >> simple-test.js
echo     await page.screenshot({ path: './test-results/dashboard.png' }); >> simple-test.js
echo   } >> simple-test.js
echo   console.log('Test completed'); >> simple-test.js
echo }); >> simple-test.js

REM Create a minimal config
echo Creating minimal config...
echo module.exports = { > simple-playwright.config.js
echo   timeout: 30000, >> simple-playwright.config.js
echo   use: { headless: false }, >> simple-playwright.config.js
echo   projects: [{ name: 'chromium' }], >> simple-playwright.config.js
echo   reporter: 'list', >> simple-playwright.config.js
echo   outputDir: 'test-results/', >> simple-playwright.config.js
echo }; >> simple-playwright.config.js

REM Run the test
echo Running browser test...
call npx playwright test simple-test.js --config=simple-playwright.config.js --headed

echo Test completed. Check test-results folder for screenshots and logs.
echo Press any key to close all services...
pause > nul

REM Clean up
taskkill /F /IM node.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1 