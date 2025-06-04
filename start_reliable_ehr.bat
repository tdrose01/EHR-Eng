@echo off
echo.
echo ========================================
echo        EHR SYSTEM RELIABLE STARTER
echo ========================================
echo.
echo Starting EHR system with guaranteed fixed ports...
echo.
echo This will start:
echo  - Login API:  http://localhost:8001 (fixed)
echo  - Patient API: http://localhost:8002 (fixed)
echo  - Records API: http://localhost:8003 (fixed)
echo  - Vaccine API: http://localhost:8004 (fixed)
echo  - Frontend:   http://localhost:8081 (fixed)
echo.
echo Please wait while services initialize...
echo.

REM Kill any existing processes on these ports
echo Stopping any existing services...
powershell -ExecutionPolicy Bypass -Command "& '%~dp0ehr_manager.ps1' stop"
echo.

REM Initialize database
echo Initializing database...
cd backend
python setup_database.py
cd ..
echo.

REM Start the backend services one by one with increased timeouts
echo Starting Login API on port 8001...
start "Login API" /min powershell -Command "cd backend; python -m api.login_api"
timeout /t 5 > nul

echo Starting Patient API on port 8002...
echo IMPORTANT: This API contains the dashboard endpoints
start "Patient API" /min powershell -Command "cd backend; python start_apis.py"
timeout /t 8 > nul

REM Verify Patient API is running since it's critical for the dashboard
echo Checking if Patient API is responding...
powershell -Command "$result = $null; try { $result = Invoke-WebRequest -Uri 'http://localhost:8002/api/status' -UseBasicParsing -TimeoutSec 5 } catch {}; if ($result -and $result.StatusCode -eq 200) { Write-Host 'Patient API is responding correctly' -ForegroundColor Green } else { Write-Host 'WARNING: Patient API is not responding. Dashboard may fail to load.' -ForegroundColor Red }"
echo.

echo Starting Records API on port 8003...
start "Records API" /min powershell -Command "cd backend; python -c """import os; from api.records_api import app, asgi_app; import uvicorn; port=8003; print('Starting Records API on port ' + str(port)); uvicorn.run(asgi_app, host='0.0.0.0', port=port)"""" 
timeout /t 5 > nul

echo Starting Vaccine API on port 8004...
start "Vaccine API" /min powershell -Command "cd backend; python start_vaccine_server.py"
timeout /t 5 > nul

REM Verify all backend services are running
echo.
echo Verifying backend services are running...
powershell -ExecutionPolicy Bypass -Command "& '%~dp0ehr_manager.ps1' status"
echo.

REM Check specifically for Patient API (dashboard) status
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8002/api/dashboard/stats' -UseBasicParsing -TimeoutSec 5; Write-Host 'Dashboard API is responding correctly' -ForegroundColor Green } catch { Write-Host 'WARNING: Dashboard API is not responding. Dashboard may fail to load.' -ForegroundColor Red }"
echo.

REM Now start the frontend
echo Starting Vue.js Frontend on port 8081...
cd ehr-vue-app
start "Frontend" /min cmd /c npm run dev -- --port 8081
cd ..

echo.
echo All services have been started with fixed ports.
echo Access the EHR system at: http://localhost:8081/
echo.
echo IMPORTANT: If you see connection errors in the dashboard,
echo please wait 30 seconds and then refresh the page after all services are fully initialized.
echo.
pause 