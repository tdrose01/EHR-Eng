@echo off
echo Starting EHR application fix with administrator privileges...
powershell -ExecutionPolicy Bypass -Command "Start-Process powershell -ArgumentList '-ExecutionPolicy Bypass -File \"C:\tom\fix-and-start-ehr.ps1\"' -Verb RunAs"
echo Script launched. If you see a UAC prompt, please click "Yes" to allow admin access. 