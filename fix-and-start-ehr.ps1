# Check if running as administrator and restart with elevation if needed
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "This script requires administrator privileges. Attempting to restart with elevation..."
    Start-Process powershell.exe -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    Exit
}

Write-Host "Running with administrator privileges" -ForegroundColor Green
Write-Host "Fixing EHR Vue application..." -ForegroundColor Cyan

# Kill any existing Node.js processes
Write-Host "Stopping any running Node.js processes..." -ForegroundColor Yellow
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
# Allow time for process termination
Start-Sleep -Seconds 2

# Navigate to the app directory
Set-Location "C:\tom\ehr-vue-app"

# Clean Vite cache - with extra robust cleanup
Write-Host "Removing Vite cache (with admin privileges)..." -ForegroundColor Yellow
if (Test-Path "node_modules\.vite") {
    # First try to change permissions to ensure we can delete
    $viteDir = Resolve-Path "node_modules\.vite"
    attrib -R "$viteDir\*.*" /S /D
    
    # Then force remove
    Remove-Item -Recurse -Force -Path $viteDir -ErrorAction SilentlyContinue
}

# Also clean the specific problematic file with extra steps
$problemFile = "node_modules\.vite\deps\chunk-VT7FWPCL.js"
if (Test-Path $problemFile) {
    # Try to unlock the file if it's locked
    Write-Host "Attempting to unlock and remove problematic file..." -ForegroundColor Yellow
    attrib -R $problemFile
    
    try {
        Remove-Item -Force -Path $problemFile -ErrorAction Stop
        Write-Host "Successfully removed problematic file." -ForegroundColor Green
    }
    catch {
        Write-Host "Failed to remove file directly. Trying alternate methods..." -ForegroundColor Red
        
        # Try with cmd.exe del command
        cmd.exe /c "del /F /Q $problemFile"
    }
}

# Reinstall dependencies to rebuild cache
Write-Host "Reinstalling dependencies..." -ForegroundColor Yellow
& npm install --force

# Return to the main directory
Set-Location "C:\tom"

# Start the backend server
Write-Host "Starting backend server..." -ForegroundColor Yellow
$backendProcess = Start-Process powershell.exe -ArgumentList "-File C:\tom\ehr_manager.ps1" -WindowStyle Normal -PassThru

# Start the frontend in a new window
Write-Host "Starting frontend server..." -ForegroundColor Yellow
Set-Location "C:\tom\ehr-vue-app"
$frontendProcess = Start-Process cmd.exe -ArgumentList "/c npm run dev -- --port 8081 --force" -WindowStyle Normal -PassThru

Write-Host "Application should be starting now!" -ForegroundColor Green
Write-Host "Access the application at http://localhost:8081" -ForegroundColor Cyan
Write-Host "Login with: admin / password" -ForegroundColor Cyan 