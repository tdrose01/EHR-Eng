@echo off
echo.
echo ========================================
echo        EHR SYSTEM QUICK STARTER
echo ========================================
echo.
echo Starting EHR system on fixed ports...
echo.
echo This will start:
echo  - Frontend:   http://localhost:8081
echo  - Login API:  http://localhost:8001
echo  - Patient API: http://localhost:8002
echo  - Records API: http://localhost:8003
echo  - Vaccine API: http://localhost:8004
echo.
echo Please wait while services initialize...
echo.

echo Initializing database...
cd backend
python setup_database.py
cd ..
echo.

echo Stopping any existing services...
powershell -ExecutionPolicy Bypass -File "%~dp0ehr_manager.ps1" stop
echo.

echo Starting backend services first...
powershell -ExecutionPolicy Bypass -File "%~dp0ehr_manager.ps1" start
echo.

echo Waiting 15 seconds for backend services to fully initialize...
timeout /t 15 > nul
echo.

echo Verifying backend services are running...
powershell -ExecutionPolicy Bypass -File "%~dp0ehr_manager.ps1" status
echo.

echo All services have been started.
echo Access the EHR system at: http://localhost:8081/
echo.
pause 