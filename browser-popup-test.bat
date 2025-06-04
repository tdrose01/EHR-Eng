@echo off
echo Browser Launch Test
echo =================

echo Creating test directory...
if not exist "browser-test" mkdir browser-test

echo Killing any existing Chrome processes...
taskkill /F /IM chrome.exe >nul 2>&1

echo Installing Playwright with verbose logging...
call npm install -D @playwright/test > browser-test\install.log 2>&1
call npx playwright install chromium --verbose > browser-test\install-chromium.log 2>&1

echo Creating simple browser script...
echo // Simple browser test > browser-test.js
echo const { chromium } = require('@playwright/test'); >> browser-test.js
echo (async () => { >> browser-test.js
echo   console.log('Starting browser test...'); >> browser-test.js
echo   try { >> browser-test.js
echo     console.log('Launching browser...'); >> browser-test.js
echo     const browser = await chromium.launch({ headless: false, args: ['--start-maximized'] }); >> browser-test.js
echo     console.log('Browser launched successfully'); >> browser-test.js
echo     const context = await browser.newContext({ viewport: { width: 1280, height: 720 } }); >> browser-test.js
echo     const page = await context.newPage(); >> browser-test.js
echo     console.log('Navigating to localhost...'); >> browser-test.js
echo     await page.goto('http://localhost:8081'); >> browser-test.js
echo     console.log('Page loaded'); >> browser-test.js
echo     await page.screenshot({ path: './browser-test/screenshot.png' }); >> browser-test.js
echo     console.log('Screenshot taken'); >> browser-test.js
echo     await new Promise(r => setTimeout(r, 10000)); // Wait 10 seconds to see the browser >> browser-test.js
echo     console.log('Test completed successfully'); >> browser-test.js
echo     await browser.close(); >> browser-test.js
echo   } catch (error) { >> browser-test.js
echo     console.error('Error during browser test:'); >> browser-test.js
echo     console.error(error); >> browser-test.js
echo   } >> browser-test.js
echo })(); >> browser-test.js

echo Running browser test with NODE_DEBUG for detailed logging...
set NODE_DEBUG=pw:api,pw:browser
call node browser-test.js > browser-test\execution.log 2>&1

echo Test execution completed.
echo Check browser-test\execution.log for details.
echo.
echo Press any key to exit...
pause > nul 