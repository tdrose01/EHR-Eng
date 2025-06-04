@echo off
echo Starting backend servers with administrative privileges...

:: Start Main API
echo Starting Main API on port 8000...
set "COMMAND=cd /d %~dp0backend && python start_apis.py"
powershell -Command "Start-Process cmd -ArgumentList '/c %COMMAND%' -Verb RunAs"

:: Wait a bit for the first server to initialize
timeout /t 5 /nobreak

:: Start Vaccine API
echo Starting Vaccine API on port 8004...
set "COMMAND=cd /d %~dp0backend && python start_vaccine_server.py"
powershell -Command "Start-Process cmd -ArgumentList '/c %COMMAND%' -Verb RunAs"

echo Servers should be starting up. Check the console windows for details.
echo.
echo You can now run start_frontend_admin.bat to start the frontend. 