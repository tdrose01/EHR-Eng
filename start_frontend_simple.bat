@echo off
echo Starting frontend service (simpler version)...

cd /d %~dp0ehr-vue-app
echo Current directory: %CD%

echo Running: npm run dev -- --port 8081 --force
start cmd /k npm run dev -- --port 8081 --force

echo Frontend started. Please check browser at http://localhost:8081
echo If you encounter any errors, try running start_frontend_admin.bat instead. 