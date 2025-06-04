@echo off
echo ========================================
echo EHR System Startup
echo ========================================
echo.

echo Step 1: Running diagnostic check...
powershell -ExecutionPolicy Bypass -File .\ehr-diagnostic.ps1
echo.

echo Step 2: Starting backend services...
start cmd /c ".\start_backend_admin.bat"
echo Waiting for backend to initialize...
timeout /t 10 /nobreak > nul
echo.

echo Step 3: Starting frontend service...
start cmd /c ".\start_frontend_simple.bat"
echo Waiting for frontend to initialize...
timeout /t 5 /nobreak > nul
echo.

echo Step 4: Opening application in browser...
start "" "http://localhost:8081"
echo.

echo ========================================
echo EHR System has been started!
echo.
echo You should now have:
echo - Backend services running on ports 8000 and 8004
echo - Frontend running on port 8081
echo - Browser opened to http://localhost:8081
echo.
echo If the application doesn't load correctly:
echo 1. Wait a few more seconds for services to fully initialize
echo 2. Refresh the browser page
echo 3. If issues persist, run: powershell -ExecutionPolicy Bypass -File .\ehr-diagnostic.ps1
echo ========================================

echo Press any key to exit this window...
pause > nul 