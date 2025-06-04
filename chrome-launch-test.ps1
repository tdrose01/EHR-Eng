# Chrome Launch Test
Write-Host "Chrome Direct Launch Test" -ForegroundColor Cyan
Write-Host "=======================" -ForegroundColor Cyan

# Find Chrome path
$chromePath = $null
$possiblePaths = @(
    "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
    "${env:LOCALAPPDATA}\Google\Chrome\Application\chrome.exe"
)

foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $chromePath = $path
        Write-Host "Found Chrome at: $chromePath" -ForegroundColor Green
        break
    }
}

if (-not $chromePath) {
    Write-Host "Chrome not found in standard locations. Trying to find it..." -ForegroundColor Yellow
    
    # Try to find Chrome using registry
    try {
        $regPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
        if (Test-Path $regPath) {
            $chromePath = (Get-ItemProperty $regPath)."(default)"
            Write-Host "Found Chrome via registry at: $chromePath" -ForegroundColor Green
        }
    } catch {
        Write-Host "Error checking registry: $_" -ForegroundColor Red
    }
}

if (-not $chromePath) {
    Write-Host "Chrome not found. Please install Chrome or specify the path manually." -ForegroundColor Red
    exit 1
}

# Verify Chrome file exists
if (-not (Test-Path $chromePath)) {
    Write-Host "Chrome executable does not exist at path: $chromePath" -ForegroundColor Red
    exit 1
}

# Try to launch Chrome
Write-Host "Attempting to launch Chrome directly..." -ForegroundColor Yellow
try {
    $process = Start-Process -FilePath $chromePath -ArgumentList "--new-window", "http://localhost:8081" -PassThru
    Write-Host "Chrome launched with PID: $($process.Id)" -ForegroundColor Green
    
    Write-Host "Waiting 10 seconds to verify Chrome is running..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    if (-not $process.HasExited) {
        Write-Host "Chrome is running successfully!" -ForegroundColor Green
    } else {
        Write-Host "Chrome exited prematurely with code: $($process.ExitCode)" -ForegroundColor Red
    }
    
    Write-Host "Press any key to close Chrome and exit..." -ForegroundColor Cyan
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    
    if (-not $process.HasExited) {
        Stop-Process -Id $process.Id -Force
    }
} catch {
    Write-Host "Error launching Chrome: $_" -ForegroundColor Red
    exit 1
}

Write-Host "Test completed." -ForegroundColor Green 