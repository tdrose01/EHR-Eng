@echo off
echo EHR System Restart Script
echo -----------------------

:: Kill processes on required ports
echo Stopping any processes on ports 8001-8004 and 8081...
FOR /F "tokens=5" %%P IN ('netstat -ano ^| findstr ":8001 "') DO (
    echo Killing process on port 8001: %%P
    taskkill /F /PID %%P 2>nul
)

FOR /F "tokens=5" %%P IN ('netstat -ano ^| findstr ":8002 "') DO (
    echo Killing process on port 8002: %%P
    taskkill /F /PID %%P 2>nul
)

FOR /F "tokens=5" %%P IN ('netstat -ano ^| findstr ":8003 "') DO (
    echo Killing process on port 8003: %%P
    taskkill /F /PID %%P 2>nul
)

FOR /F "tokens=5" %%P IN ('netstat -ano ^| findstr ":8004 "') DO (
    echo Killing process on port 8004: %%P
    taskkill /F /PID %%P 2>nul
)

FOR /F "tokens=5" %%P IN ('netstat -ano ^| findstr ":8081 "') DO (
    echo Killing process on port 8081: %%P
    taskkill /F /PID %%P 2>nul
)

echo Starting all EHR system components...

:: Start Login API (port 8001)
echo Starting Login API on port 8001...
start "Login API" cmd /c "cd backend && python -m api.login_api"

:: Start Patient API (port 8002)
echo Starting Patient API on port 8002...
start "Patient API" cmd /c "cd backend && python start_apis.py"

:: Start Records API (port 8003)
echo Starting Records API on port 8003...
start "Records API" cmd /c "cd backend && python -c "import os; os.environ['PORT'] = '8003'; from api.records_api import app; app.run(host='0.0.0.0', port=8003)""

:: Start Vaccine API (port 8004)
echo Starting Vaccine API on port 8004...
start "Vaccine API" cmd /c "cd backend && python start_vaccine_server.py"

:: Wait for APIs to be ready
echo Waiting for APIs to initialize (5 seconds)...
timeout /t 5 /nobreak >nul

:: Start Frontend (port 8081)
echo Starting Frontend on port 8081...
start "EHR Frontend" cmd /c "cd ehr-vue-app && npm run dev -- --port 8081 --force"

echo.
echo EHR System started successfully!
echo.
echo Endpoints:
echo - Frontend: http://localhost:8081/
echo - Login API: http://localhost:8001/api/
echo - Patient API: http://localhost:8002/api/
echo - Records API: http://localhost:8003/api/
echo - Vaccine API: http://localhost:8004/api/
echo.
echo Note: Console windows must remain open for services to run
echo. 