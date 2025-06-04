@echo off
echo ======================================
echo EHR Vue Frontend Repair Tool
echo ======================================
echo.

echo Step 1: Checking if frontend is running...
tasklist /fi "imagename eq node.exe" | find "node.exe" >nul
if %errorlevel% equ 0 (
    echo Stopping running Node.js processes...
    taskkill /F /IM node.exe
    echo All Node.js processes terminated.
) else (
    echo No Node.js processes found running.
)
echo.

echo Step 2: Clearing Vite cache...
cd /d %~dp0ehr-vue-app
echo Current directory: %CD%

if exist "node_modules\.vite" (
    echo Vite cache found, removing...
    rmdir /S /Q "node_modules\.vite" 2>nul
    if %errorlevel% neq 0 (
        echo Standard deletion failed, trying with admin rights...
        powershell -Command "Start-Process cmd -ArgumentList '/c rmdir /S /Q \"%CD%\node_modules\.vite\"' -Verb RunAs"
        timeout /t 2 /nobreak > nul
    )
) else (
    echo No Vite cache found.
)
echo.

echo Step 3: Cleaning npm cache...
call npm cache clean --force
echo npm cache cleaned.
echo.

echo Step 4: Installing dependencies...
call npm install
echo Dependencies reinstalled.
echo.

echo Step 5: Applying configuration fixes...
echo.

if exist "vite.config.js" (
    echo Checking and fixing vite.config.js...
    powershell -Command "(Get-Content vite.config.js) -replace 'localhost:8002(.+)dashboard', 'localhost:8000$1dashboard' | Set-Content vite.config.js"
    echo - Fixed dashboard API target in vite.config.js
) else (
    echo vite.config.js not found!
)

if exist "src\services\api.js" (
    echo Checking and fixing API endpoint in api.js...
    powershell -Command "(Get-Content 'src\services\api.js') -replace '``\$\{API_BASE_URL\}/api/dashboard/stats``', '/api/dashboard/stats' | Set-Content 'src\services\api.js'"
    echo - Fixed dashboard API endpoint in api.js
) else (
    echo src\services\api.js not found!
)

if exist "src\views\Dashboard.vue" (
    echo Checking and fixing StatCard component in Dashboard.vue...
    powershell -Command "(Get-Content 'src\views\Dashboard.vue') -replace '(:value=\"stats.totalPatients\"\s+label=\"Total Patients\")', '$1\n      icon=\"fas fa-users\"' | Set-Content 'src\views\Dashboard.vue.tmp'"
    powershell -Command "(Get-Content 'src\views\Dashboard.vue.tmp') -replace '(:value=\"stats.activePatients\"\s+label=\"Active Patients\")', '$1\n      icon=\"fas fa-user-check\"' | Set-Content 'src\views\Dashboard.vue'"
    powershell -Command "(Get-Content 'src\views\Dashboard.vue') -replace '(:value=\"stats.appointmentsToday\"\s+label=\"Today''s Appointments\")', '$1\n      icon=\"fas fa-calendar-check\"' | Set-Content 'src\views\Dashboard.vue.tmp'"
    powershell -Command "(Get-Content 'src\views\Dashboard.vue.tmp') -replace '(:value=\"stats.pendingRecords\"\s+label=\"Pending Records\")', '$1\n      icon=\"fas fa-clipboard-list\"' | Set-Content 'src\views\Dashboard.vue'"
    if exist "src\views\Dashboard.vue.tmp" del /f "src\views\Dashboard.vue.tmp"
    echo - Fixed missing icon props in Dashboard.vue
) else (
    echo src\views\Dashboard.vue not found!
)
echo.

echo Step 6: Starting frontend with clean configuration...
cd /d %~dp0
echo Starting frontend with administrative privileges...
call start_frontend_admin.bat
echo.

echo ======================================
echo Frontend repair process completed!
echo.
echo If you still have issues:
echo 1. Check your network connectivity to ensure API servers are reachable
echo 2. Make sure all backend services are running correctly
echo 3. Try clearing your browser cache or using incognito mode
echo ======================================
echo.
echo Press any key to exit...
pause > nul 