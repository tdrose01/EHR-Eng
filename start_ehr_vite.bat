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

echo Starting backend servers...
echo.
rem First, stop any running services
powershell -ExecutionPolicy Bypass -Command "& '%~dp0ehr_manager.ps1' stop"

rem Now start the backend services normally (not minimized for troubleshooting)
powershell -ExecutionPolicy Bypass -Command "& '%~dp0ehr_manager.ps1' start_backend"

rem Wait longer for backends to initialize
echo.
echo Waiting for backend services to initialize (15 seconds)...
echo.
timeout /t 15 > nul

echo.
echo Checking if backend services are running...
powershell -ExecutionPolicy Bypass -Command "& '%~dp0ehr_manager.ps1' status"
echo.

echo.
echo Starting frontend Vite server...
echo.

rem Start the Vite server in a visible window
cd ehr-vue-app
npm run dev

echo.
echo All services have been started.
echo. 