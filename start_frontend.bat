@echo off
echo Starting frontend...
cd /d %~dp0ehr-vue-app
npm run dev -- --port 8081 --force 