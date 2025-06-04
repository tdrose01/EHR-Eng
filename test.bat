@echo off
echo === Running Standalone Test ===
npx playwright test tests/standalone-test.js --headed
if %ERRORLEVEL% NEQ 0 (
    echo === Running Minimal Test ===
    npx playwright test tests/minimal-test.js --headed
)
