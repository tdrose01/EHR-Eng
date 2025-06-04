@echo off
echo EHR Application Full Test Suite
echo ==================================

echo Step 1: Creating test-results directory if it doesn't exist
if not exist "test-results" mkdir test-results

echo Step 2: Killing any running EHR processes
taskkill /F /IM node.exe /FI "WINDOWTITLE eq ehr-vue-app" > nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq EHR API" > nul 2>&1

echo Step 3: Starting backend services (Main API and Vaccine API)
start "EHR Main API" cmd /k "cd /d %~dp0backend && python start_apis.py"
timeout /t 5 /nobreak
start "EHR Vaccine API" cmd /k "cd /d %~dp0backend && python start_vaccine_server.py"
timeout /t 5 /nobreak

echo Step 4: Starting frontend service
start "EHR Frontend" cmd /k "cd /d %~dp0ehr-vue-app && npm run dev -- --port 8081 --force"
timeout /t 15 /nobreak

echo Step 5: Installing Playwright if needed
call npm install -D @playwright/test > nul 2>&1
call npx playwright install chromium > nul 2>&1

echo Step 6: Running browser tests
echo ----------------------------
echo The browser window will open automatically.
echo Screenshots will be saved to the test-results directory.
echo ----------------------------
call npx playwright test ehr-test-automation.js --config=ehr-playwright.config.js --headed

echo Step 7: Test completed!
echo Check the test-results directory for screenshots
echo and review the console output for details.
echo ----------------------------
echo Press any key to close all EHR services and exit...
pause > nul

echo Cleaning up - stopping all EHR services
taskkill /F /IM node.exe /FI "WINDOWTITLE eq ehr-vue-app" > nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq EHR API" > nul 2>&1 