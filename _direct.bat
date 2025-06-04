@echo off
echo Running ...
npx playwright test "" --headed
if %ERRORLEVEL% NEQ 0 (
    echo First attempt failed, trying with explicit config...
    npx playwright test --config=playwright.config.js "" --headed
)
start "" "playwright-report\index.html"
