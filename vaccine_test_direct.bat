@echo off
echo Running vaccine-test.js...
echo Using npx playwright test tests/vaccine-test.js --headed

npx playwright test tests/vaccine-test.js --headed
if %ERRORLEVEL% NEQ 0 (
    echo First attempt failed, trying with explicit config...
    npx playwright test --config=playwright.config.js tests/vaccine-test.js --headed
    
    if %ERRORLEVEL% NEQ 0 (
        echo Second attempt failed, trying from tests directory...
        cd tests
        npx playwright test vaccine-test.js --headed
        cd ..
    )
)

if exist "playwright-report\index.html" (
    echo Opening test report...
    start "" "playwright-report\index.html"
) 