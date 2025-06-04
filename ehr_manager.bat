@echo off
echo.
echo ========================================
echo       EHR SYSTEM MANAGER UTILITY
echo ========================================
echo.

if "%1"=="" (
    echo Starting EHR System with fixed ports...
    echo - Frontend:   http://localhost:8081
    echo - Login API:  http://localhost:8001
    echo - Patient API: http://localhost:8002
    echo - Records API: http://localhost:8003
    echo - Vaccine API: http://localhost:8004
    echo.
    powershell -ExecutionPolicy Bypass -File "%~dp0ehr_manager.ps1" start
) else (
    powershell -ExecutionPolicy Bypass -File "%~dp0ehr_manager.ps1" %*
)

echo.
pause 