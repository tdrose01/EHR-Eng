#Requires -RunAsAdministrator
# EHR Application Starter - Launches both backend and frontend with proper permissions

Write-Host "=======================================`nEHR Application Launcher`n=======================================" -ForegroundColor Cyan

# Step 1: Kill any existing Node.js or Python processes
Write-Host "`nStep 1: Checking for existing processes..." -ForegroundColor Green
$nodeProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue
if ($nodeProcesses) {
    Write-Host "Stopping running Node.js processes..." -ForegroundColor Yellow
    Stop-Process -Name "node" -Force -ErrorAction SilentlyContinue
    Write-Host "All Node.js processes terminated." -ForegroundColor Green
}

$pythonProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    Write-Host "Stopping running Python processes..." -ForegroundColor Yellow
    Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue
    Write-Host "All Python processes terminated." -ForegroundColor Green
}

# Step 2: Start backend servers
Write-Host "`nStep 2: Starting backend servers..." -ForegroundColor Green
$backendStarted = $false

# First, try to use the existing batch file
$backendBatPath = Join-Path $PSScriptRoot "start_backend_admin.bat"
if (Test-Path $backendBatPath) {
    Write-Host "Starting backend using start_backend_admin.bat..." -ForegroundColor Yellow
    Start-Process -FilePath $backendBatPath -NoNewWindow
    $backendStarted = $true
    Start-Sleep -Seconds 5  # Give backend time to start
} else {
    # Fallback to direct command
    Write-Host "start_backend_admin.bat not found. Trying direct startup..." -ForegroundColor Yellow
    
    # Check if backend directory exists
    $backendDir = Join-Path $PSScriptRoot "backend"
    if (Test-Path $backendDir) {
        # Start main API
        $mainApiCmd = "cd /d `"$backendDir`" && python -m start_apis 8000"
        Start-Process -FilePath "cmd.exe" -ArgumentList "/c $mainApiCmd" -Verb RunAs
        
        # Start vaccine API
        $vaccineApiCmd = "cd /d `"$backendDir`" && python -m start_apis 8004 --vaccine-api"
        Start-Process -FilePath "cmd.exe" -ArgumentList "/c $vaccineApiCmd" -Verb RunAs
        
        $backendStarted = $true
        Write-Host "Backend servers started directly." -ForegroundColor Green
        Start-Sleep -Seconds 5  # Give backend time to start
    } else {
        Write-Host "Backend directory not found at $backendDir. Cannot start backend." -ForegroundColor Red
    }
}

# Step 3: Start frontend
Write-Host "`nStep 3: Starting frontend..." -ForegroundColor Green
$frontendStarted = $false

# First, try to start with admin batch file
$frontendBatPath = Join-Path $PSScriptRoot "start_frontend_admin.bat"
if (Test-Path $frontendBatPath) {
    Write-Host "Starting frontend using start_frontend_admin.bat..." -ForegroundColor Yellow
    Start-Process -FilePath $frontendBatPath -NoNewWindow
    $frontendStarted = $true
} else {
    # Try regular start_frontend.bat
    $frontendRegularBatPath = Join-Path $PSScriptRoot "start_frontend.bat"
    if (Test-Path $frontendRegularBatPath) {
        Write-Host "Starting frontend using start_frontend.bat..." -ForegroundColor Yellow
        Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$frontendRegularBatPath`"" -Verb RunAs
        $frontendStarted = $true
    } else {
        # Fallback to direct start
        $frontendDir = Join-Path $PSScriptRoot "ehr-vue-app"
        if (Test-Path $frontendDir) {
            Write-Host "Starting frontend directly..." -ForegroundColor Yellow
            $frontendCmd = "cd /d `"$frontendDir`" && npm run dev -- --port 8081 --force"
            Start-Process -FilePath "cmd.exe" -ArgumentList "/c $frontendCmd" -Verb RunAs
            $frontendStarted = $true
        } else {
            Write-Host "Frontend directory not found at $frontendDir. Cannot start frontend." -ForegroundColor Red
        }
    }
}

# Step 4: Report status
Write-Host "`nStep 4: Application startup status" -ForegroundColor Green
if ($backendStarted) {
    Write-Host "✅ Backend services started successfully." -ForegroundColor Green
    Write-Host "   - Main API running on: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "   - Vaccine API running on: http://localhost:8004" -ForegroundColor Cyan
} else {
    Write-Host "❌ Failed to start backend services." -ForegroundColor Red
}

if ($frontendStarted) {
    Write-Host "✅ Frontend started successfully." -ForegroundColor Green
    Write-Host "   - Frontend available at: http://localhost:8081" -ForegroundColor Cyan
} else {
    Write-Host "❌ Failed to start frontend." -ForegroundColor Red
}

# Step 5: Open browser
if ($backendStarted -and $frontendStarted) {
    Write-Host "`nStep 5: Opening application in browser..." -ForegroundColor Green
    Start-Process "http://localhost:8081"
    
    Write-Host "`n=======================================`nApplication started successfully!" -ForegroundColor Cyan
    Write-Host "You can now use the EHR application at: http://localhost:8081" -ForegroundColor Green
    Write-Host "=======================================`n"
} else {
    Write-Host "`n=======================================`nWarning: Application may not be fully operational." -ForegroundColor Yellow
    Write-Host "Please check the console output for errors and try again.`n=======================================`n"
}

Write-Host "Press any key to close this window (services will continue running)..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 