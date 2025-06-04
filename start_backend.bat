@echo off
echo Starting backend servers...

:: Start Main API
echo Starting Main API on port 8000...
start cmd /c "cd /d %~dp0backend && python start_apis.py"

:: Wait a bit for the first server to initialize
timeout /t 5 /nobreak

:: Start Vaccine API
echo Starting Vaccine API on port 8004...
start cmd /c "cd /d %~dp0backend && python start_vaccine_server.py"

echo Servers should be starting up. Check the console windows for details.
echo.
echo You can now run start_frontend.bat to start the frontend. 