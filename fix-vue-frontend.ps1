#Requires -RunAsAdministrator
# EHR Vue Frontend Repair Tool - PowerShell Version

Write-Host "=======================================`nEHR Vue Frontend Repair Tool (PowerShell)`n=======================================" -ForegroundColor Cyan

# Step 1: Check if frontend is running
Write-Host "`nStep 1: Checking if frontend is running..." -ForegroundColor Green
$nodeProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue
if ($nodeProcesses) {
    Write-Host "Stopping running Node.js processes..." -ForegroundColor Yellow
    Stop-Process -Name "node" -Force -ErrorAction SilentlyContinue
    Write-Host "All Node.js processes terminated." -ForegroundColor Green
} else {
    Write-Host "No Node.js processes found running." -ForegroundColor Green
}

# Step 2: Clean Vite cache
Write-Host "`nStep 2: Clearing Vite cache..." -ForegroundColor Green
$appDir = Join-Path $PSScriptRoot "ehr-vue-app"
Set-Location $appDir
Write-Host "Current directory: $PWD"

$viteCachePath = Join-Path $appDir "node_modules\.vite"
if (Test-Path $viteCachePath) {
    Write-Host "Vite cache found, removing..." -ForegroundColor Yellow
    try {
        # First try with PowerShell's Remove-Item
        Remove-Item -Path $viteCachePath -Recurse -Force -ErrorAction Stop
        Write-Host "Vite cache removed successfully." -ForegroundColor Green
    } catch {
        Write-Host "Standard removal failed, trying alternative method..." -ForegroundColor Red
        # Try with cmd rd command
        cmd /c "rd /s /q `"$viteCachePath`""
        if (Test-Path $viteCachePath) {
            Write-Host "Still having issues. Will try to take ownership..." -ForegroundColor Red
            # Take ownership and grant full permissions
            Start-Process "takeown" -ArgumentList "/f `"$viteCachePath`" /r /d y" -NoNewWindow -Wait
            Start-Process "icacls" -ArgumentList "`"$viteCachePath`" /grant:r administrators:F /t" -NoNewWindow -Wait
            # Try removing one more time
            Remove-Item -Path $viteCachePath -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
} else {
    Write-Host "No Vite cache found." -ForegroundColor Green
}

# Step 3: Clear npm cache
Write-Host "`nStep 3: Cleaning npm cache..." -ForegroundColor Green
npm cache clean --force
Write-Host "npm cache cleaned." -ForegroundColor Green

# Step 4: Fix dependencies - Address the package.json to avoid conflicts
Write-Host "`nStep 4: Fixing package.json dependencies..." -ForegroundColor Green
$packageJsonPath = Join-Path $appDir "package.json"
if (Test-Path $packageJsonPath) {
    $packageJson = Get-Content $packageJsonPath -Raw | ConvertFrom-Json
    
    # Check for Jest version conflicts
    $jestVersion = $packageJson.devDependencies.jest
    $vue3JestPath = Join-Path $appDir "node_modules\@vue\vue3-jest"
    
    if (Test-Path $vue3JestPath) {
        Write-Host "Found potential conflict with @vue/vue3-jest, removing..." -ForegroundColor Yellow
        Remove-Item -Path $vue3JestPath -Recurse -Force -ErrorAction SilentlyContinue
    }
    
    # Check for any vue3-jest in devDependencies and remove it temporarily
    if ($packageJson.devDependencies.'@vue/vue3-jest') {
        Write-Host "Temporarily commenting out @vue/vue3-jest in package.json" -ForegroundColor Yellow
        $packageJsonContent = Get-Content $packageJsonPath -Raw
        $packageJsonContent = $packageJsonContent -replace '"@vue/vue3-jest": ".*?"', '"//@vue/vue3-jest": "27.0.0" // temporarily disabled'
        $packageJsonContent | Set-Content $packageJsonPath
    }
    
    Write-Host "Dependencies fixed in package.json." -ForegroundColor Green
} else {
    Write-Host "package.json not found!" -ForegroundColor Red
}

# Step 5: Clean node_modules and reinstall
Write-Host "`nStep 5: Removing node_modules..." -ForegroundColor Green
$nodeModulesPath = Join-Path $appDir "node_modules"
if (Test-Path $nodeModulesPath) {
    try {
        Remove-Item -Path $nodeModulesPath -Recurse -Force -ErrorAction Stop
        Write-Host "node_modules removed successfully." -ForegroundColor Green
    } catch {
        Write-Host "Standard removal failed, trying alternative method..." -ForegroundColor Red
        # Try with cmd rd command
        cmd /c "rd /s /q `"$nodeModulesPath`""
    }
}

# Step 6: Install dependencies
Write-Host "`nStep 6: Installing dependencies..." -ForegroundColor Green
npm install
Write-Host "Dependencies reinstalled." -ForegroundColor Green

# Step 7: Apply configuration fixes
Write-Host "`nStep 7: Applying configuration fixes..." -ForegroundColor Green

$viteConfigPath = Join-Path $appDir "vite.config.js"
if (Test-Path $viteConfigPath) {
    Write-Host "Checking and fixing vite.config.js..." -ForegroundColor Yellow
    $viteConfig = Get-Content $viteConfigPath -Raw
    $viteConfig = $viteConfig -replace 'localhost:8002(.+)dashboard', 'localhost:8000$1dashboard'
    $viteConfig | Set-Content $viteConfigPath
    Write-Host "- Fixed dashboard API target in vite.config.js" -ForegroundColor Green
} else {
    Write-Host "vite.config.js not found!" -ForegroundColor Red
}

$apiJsPath = Join-Path $appDir "src\services\api.js"
if (Test-Path $apiJsPath) {
    Write-Host "Checking and fixing API endpoint in api.js..." -ForegroundColor Yellow
    $apiJs = Get-Content $apiJsPath -Raw
    $apiJs = $apiJs -replace '`\${API_BASE_URL}/api/dashboard/stats`', '/api/dashboard/stats'
    $apiJs | Set-Content $apiJsPath
    Write-Host "- Fixed dashboard API endpoint in api.js" -ForegroundColor Green
} else {
    Write-Host "src\services\api.js not found!" -ForegroundColor Red
}

$dashboardVuePath = Join-Path $appDir "src\views\Dashboard.vue"
if (Test-Path $dashboardVuePath) {
    Write-Host "Checking and fixing StatCard component in Dashboard.vue..." -ForegroundColor Yellow
    $dashboardVue = Get-Content $dashboardVuePath -Raw
    $dashboardVue = $dashboardVue -replace '(:value="stats\.totalPatients"\s+label="Total Patients")(?!\s+icon=)', '$1 icon="fas fa-users"'
    $dashboardVue = $dashboardVue -replace '(:value="stats\.activePatients"\s+label="Active Patients")(?!\s+icon=)', '$1 icon="fas fa-user-check"'
    $dashboardVue = $dashboardVue -replace '(:value="stats\.appointmentsToday"\s+label="Today''s Appointments")(?!\s+icon=)', '$1 icon="fas fa-calendar-check"'
    $dashboardVue = $dashboardVue -replace '(:value="stats\.pendingRecords"\s+label="Pending Records")(?!\s+icon=)', '$1 icon="fas fa-clipboard-list"'
    $dashboardVue | Set-Content $dashboardVuePath
    Write-Host "- Fixed missing icon props in Dashboard.vue" -ForegroundColor Green
} else {
    Write-Host "src\views\Dashboard.vue not found!" -ForegroundColor Red
}

# Step 8: Return to root directory and start frontend
Write-Host "`nStep 8: Starting frontend with clean configuration..." -ForegroundColor Green
Set-Location $PSScriptRoot
Write-Host "Starting frontend with administrative privileges..." -ForegroundColor Yellow

# Start the frontend in a new process window
$startBatPath = Join-Path $PSScriptRoot "start_frontend_admin.bat"
if (Test-Path $startBatPath) {
    Start-Process -FilePath $startBatPath -NoNewWindow
} else {
    # Fallback if the batch file doesn't exist
    $ehrAppPath = Join-Path $PSScriptRoot "ehr-vue-app"
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c cd /d $ehrAppPath && npm run dev -- --port 8081 --force" -Verb RunAs
}

Write-Host "`n=======================================`nFrontend repair process completed!" -ForegroundColor Cyan
Write-Host "`nIf you still have issues:"
Write-Host "1. Check your network connectivity to ensure API servers are reachable"
Write-Host "2. Make sure all backend services are running correctly"
Write-Host "3. Try clearing your browser cache or using incognito mode"
Write-Host "=======================================`n"

Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 