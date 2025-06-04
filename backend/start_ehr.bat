@echo off
echo EHR System Starter
echo =====================================
echo.
echo This script will start all EHR system components
echo.
echo Press any key to continue...
pause > nul

python start_ehr_servers.py

echo.
echo Press any key to exit...
pause > nul 