@echo off
echo Rebuilding Vite Cache
echo ===================
echo.

echo Step 1: Terminating any Node.js processes...
taskkill /F /IM node.exe >nul 2>&1
echo Node processes terminated.
echo.

echo Step 2: Clearing Vite cache...
cd /d %~dp0ehr-vue-app
echo Current directory: %CD%

if exist "node_modules\.vite" (
    echo Vite cache found, removing with admin rights...
    powershell -Command "Start-Process cmd -ArgumentList '/c rmdir /S /Q \"%CD%\node_modules\.vite\"' -Verb RunAs"
    timeout /t 2 /nobreak > nul
) else (
    echo No Vite cache found.
)

echo Step 3: Clearing npm cache...
echo This may take a moment...
call npm cache clean --force
echo NPM cache cleared.
echo.

echo Step 4: Installing dependencies...
echo This will rebuild all node_modules. Please be patient...
call npm install
echo Dependencies reinstalled.
echo.

echo Step 5: Starting frontend with clean cache...
echo.
cd /d %~dp0
echo Starting frontend with no-cache option...
cd /d %~dp0ehr-vue-app
start cmd /k npm run dev -- --port 8081 --force --no-cache
cd /d %~dp0
echo.

echo ===================
echo Vite cache has been completely rebuilt.
echo The frontend should now be running in a separate window.
echo If you still encounter issues, try:
echo 1. Restarting your computer
echo 2. Running start_frontend_admin.bat
echo 3. Reinstalling Node.js
echo ===================
echo.
echo Press any key to exit...
pause > nul 