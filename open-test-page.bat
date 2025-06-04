@echo off
echo Opening test page in Chrome...

REM Try to find Chrome in common locations
set CHROME_PATH=

REM Check Program Files location
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH="%ProgramFiles%\Google\Chrome\Application\chrome.exe"
    goto :CHROME_FOUND
)

REM Check Program Files (x86) location
if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH="%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
    goto :CHROME_FOUND
)

REM Check Local AppData location
if exist "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH="%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
    goto :CHROME_FOUND
)

echo Chrome not found in common locations. Trying to open with default browser...
start "" "file://%~dp0test-page.html"
goto :END

:CHROME_FOUND
echo Found Chrome at: %CHROME_PATH%
%CHROME_PATH% "file://%~dp0test-page.html" --new-window

:END
echo Test page should be open now. Press any key to continue...
pause > nul 