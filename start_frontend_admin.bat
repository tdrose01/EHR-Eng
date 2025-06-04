@echo off
echo Starting frontend with administrative privileges...
set "COMMAND=cd /d %~dp0ehr-vue-app && npm run dev -- --port 8081 --force"
powershell -Command "Start-Process cmd -ArgumentList '/c %COMMAND%' -Verb RunAs" 