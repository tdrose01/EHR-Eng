@echo off
echo EHR System Master Management
echo ===========================
echo.

rem Check if command is provided
if "%~1"=="" (
    echo Starting EHR System...
    powershell -ExecutionPolicy Bypass -File "%~dp0master_ehr.ps1" -Command start
) else (
    echo Running command: %1
    powershell -ExecutionPolicy Bypass -File "%~dp0master_ehr.ps1" -Command %1
)

echo.
echo Press any key to exit...
pause > nul 