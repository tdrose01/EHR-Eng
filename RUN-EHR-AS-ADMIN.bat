@echo off
echo =======================================
echo = EHR APPLICATION REPAIR AND LAUNCHER =
echo =======================================
echo.
echo This script will:
echo 1. Request administrator privileges (required)
echo 2. Stop any running Node.js processes
echo 3. Fix permission issues with Vite cache
echo 4. Start the EHR application servers
echo.
echo If you see a UAC prompt, please click "Yes" to allow admin access
echo.
echo Press any key to continue...
pause > nul

powershell -ExecutionPolicy Bypass -Command "Start-Process powershell -ArgumentList '-ExecutionPolicy Bypass -File \"C:\tom\fix-and-start-ehr.ps1\"' -Verb RunAs"

echo.
echo Script launched! Wait for the PowerShell window to initialize the servers.
echo Once complete, access the application at: http://localhost:8081
echo Login credentials: admin / password
echo. 