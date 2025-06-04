@echo off
echo Fixing Vite Cache Permission Issues
echo ===================================
echo.

echo Step 1: Terminating any Node.js processes...
taskkill /F /IM node.exe >nul 2>&1
echo Node processes terminated.
echo.

echo Step 2: Clearing Vite cache...
cd /d %~dp0ehr-vue-app
echo Current directory: %CD%

if exist "node_modules\.vite" (
    echo Vite cache found, attempting to remove...
    rmdir /S /Q "node_modules\.vite" 2>nul
    if exist "node_modules\.vite" (
        echo Standard deletion failed, trying with admin rights...
        powershell -Command "Start-Process cmd -ArgumentList '/c rmdir /S /Q \"%CD%\node_modules\.vite\"' -Verb RunAs"
        timeout /t 2 /nobreak > nul
    )
    if not exist "node_modules\.vite" (
        echo Vite cache successfully removed.
    ) else (
        echo WARNING: Could not remove Vite cache completely. Some files may still be locked.
    )
) else (
    echo No Vite cache found.
)
echo.

echo Step 3: Starting frontend with admin rights...
cd /d %~dp0
call start_frontend_admin.bat
echo.

echo ===================================
echo Process completed. The frontend should now start correctly.
echo If you still encounter issues:
echo 1. Try clearing Node.js and NPM cache with: npm cache clean --force
echo 2. Run the application in development mode without cache: npm run dev -- --force --no-cache
echo 3. Restart your computer to release any locked files
echo =================================== 