# Browser Launch Test with Elevated Privileges
Write-Host "Browser Launch Test" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan

# Create test directory
Write-Host "Creating test directory..." -ForegroundColor Yellow
if (-not (Test-Path "browser-test")) {
    New-Item -ItemType Directory -Path "browser-test" | Out-Null
}

# Kill any existing Chrome processes
Write-Host "Killing any existing Chrome processes..." -ForegroundColor Yellow
Get-Process -Name "chrome" -ErrorAction SilentlyContinue | Stop-Process -Force

# Check if services are running
Write-Host "Checking if services are running..." -ForegroundColor Yellow
$frontend = Test-NetConnection -ComputerName localhost -Port 8081 -InformationLevel Quiet -ErrorAction SilentlyContinue
$backend = Test-NetConnection -ComputerName localhost -Port 8000 -InformationLevel Quiet -ErrorAction SilentlyContinue

if (-not $frontend) {
    Write-Host "Frontend is not running on port 8081!" -ForegroundColor Red
    Write-Host "Starting frontend with no-cache option..." -ForegroundColor Yellow
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c cd /d $PWD\ehr-vue-app && npm run dev -- --port 8081 --force --no-cache" -PassThru -WindowStyle Normal
    Start-Sleep -Seconds 15
}

if (-not $backend) {
    Write-Host "Backend is not running on port 8000!" -ForegroundColor Red
    Write-Host "Starting backend service..." -ForegroundColor Yellow
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c cd /d $PWD\backend && python start_apis.py" -PassThru -WindowStyle Normal
    Start-Sleep -Seconds 5
}

# Install Playwright with detailed logging
Write-Host "Installing Playwright with verbose logging..." -ForegroundColor Yellow
npm install -D @playwright/test | Out-File -FilePath "browser-test\install.log"
npx playwright install chromium --verbose | Out-File -FilePath "browser-test\install-chromium.log"

# Create test script
Write-Host "Creating browser test script..." -ForegroundColor Yellow
$testScript = @"
// Simple browser test
const { chromium } = require('@playwright/test');

(async () => {
  console.log('Starting browser test...');
  try {
    console.log('Launching browser...');
    const browser = await chromium.launch({ 
      headless: false,
      args: ['--start-maximized'],
      executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH || undefined
    });
    console.log('Browser launched successfully');
    
    const context = await browser.newContext({ 
      viewport: { width: 1280, height: 720 } 
    });
    const page = await context.newPage();
    
    console.log('Navigating to localhost...');
    await page.goto('http://localhost:8081', { timeout: 30000 });
    console.log('Page loaded');
    
    await page.screenshot({ path: './browser-test/screenshot.png' });
    console.log('Screenshot taken');
    
    // Try to navigate to dashboard
    console.log('Attempting to navigate to dashboard');
    try {
      const dashboardLink = await page.locator('a[href="/dashboard"], a:has-text("Dashboard")').first();
      if (await dashboardLink.isVisible()) {
        await dashboardLink.click();
        await page.waitForLoadState('networkidle', { timeout: 30000 });
        await page.screenshot({ path: './browser-test/dashboard.png' });
        console.log('Dashboard screenshot taken');
      } else {
        console.log('Dashboard link not found, trying direct navigation');
        await page.goto('http://localhost:8081/dashboard', { timeout: 30000 });
        await page.waitForLoadState('networkidle', { timeout: 30000 });
        await page.screenshot({ path: './browser-test/dashboard-direct.png' });
      }
    } catch (navError) {
      console.error('Error navigating to dashboard:', navError);
    }
    
    // Wait to see the browser
    console.log('Waiting 20 seconds to observe the browser...');
    await new Promise(r => setTimeout(r, 20000)); 
    
    console.log('Test completed successfully');
    await browser.close();
  } catch (error) {
    console.error('Error during browser test:');
    console.error(error);
  }
})();
"@

$testScript | Out-File -FilePath "browser-test.js" -Encoding utf8

# Set environment variables for better debugging
Write-Host "Running browser test with detailed logging..." -ForegroundColor Green
$env:PLAYWRIGHT_BROWSERS_PATH = "$PWD\node_modules\playwright"
$env:NODE_DEBUG = "pw:api,pw:browser"

# Try to find Chrome path
$chromePath = ""
$possiblePaths = @(
    "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
    "${env:LOCALAPPDATA}\Google\Chrome\Application\chrome.exe"
)

foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $chromePath = $path
        break
    }
}

if ($chromePath) {
    Write-Host "Found Chrome at: $chromePath" -ForegroundColor Green
    $env:PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH = $chromePath
} else {
    Write-Host "Could not find Chrome, will use bundled browser" -ForegroundColor Yellow
}

# Run the test
Write-Host "Executing browser test..." -ForegroundColor Green
$process = Start-Process -FilePath "node" -ArgumentList "browser-test.js" -PassThru -NoNewWindow -RedirectStandardOutput "browser-test\execution.log" -RedirectStandardError "browser-test\error.log"

Write-Host "Browser test process started with PID: $($process.Id)" -ForegroundColor Cyan
Write-Host "Waiting for test to complete (30 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

if (-not $process.HasExited) {
    Write-Host "Browser test is still running. Check if browser window opened." -ForegroundColor Green
    Write-Host "Press any key when ready to stop the test..." -ForegroundColor Cyan
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    
    if (-not $process.HasExited) {
        Stop-Process -Id $process.Id -Force
    }
} else {
    Write-Host "Browser test completed with exit code: $($process.ExitCode)" -ForegroundColor $(if ($process.ExitCode -eq 0) { "Green" } else { "Red" })
}

# Check for errors
if (Test-Path "browser-test\error.log") {
    $errorContent = Get-Content "browser-test\error.log"
    if ($errorContent -and $errorContent.Length -gt 0) {
        Write-Host "Errors detected during test execution:" -ForegroundColor Red
        $errorContent | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
    }
}

Write-Host "Test execution completed." -ForegroundColor Green
Write-Host "Check browser-test\execution.log and browser-test\error.log for details." -ForegroundColor Cyan
Write-Host "Screenshots should be in the browser-test directory." -ForegroundColor Cyan 