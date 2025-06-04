# PowerShell script to clean up test processes that might be causing file locks
Write-Host "Cleaning up test processes..." -ForegroundColor Cyan

# Kill any playwright browsers
Write-Host "Killing any remaining Playwright browsers..." -ForegroundColor Yellow
$playwrightProcesses = Get-Process | Where-Object { $_.Name -like "*playwright*" -or $_.Name -like "*chrome*" -or $_.Name -like "*chromium*" -or $_.Name -like "*msedge*" -or $_.Name -like "*firefox*" } -ErrorAction SilentlyContinue
if ($playwrightProcesses) {
    $playwrightProcesses | ForEach-Object {
        Write-Host "Killing process $($_.Name) (PID: $($_.Id))" -ForegroundColor Yellow
        try {
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        } catch {
            Write-Host "Failed to kill process $($_.Name) (PID: $($_.Id)): $_" -ForegroundColor Red
        }
    }
} else {
    Write-Host "No Playwright browser processes found" -ForegroundColor Green
}

# Clean up the test-results directory
Write-Host "Cleaning up test-results directory..." -ForegroundColor Yellow
if (Test-Path ".\test-results") {
    try {
        # Try to delete the .last-run.json file specifically
        if (Test-Path ".\test-results\.last-run.json") {
            Remove-Item -Path ".\test-results\.last-run.json" -Force -ErrorAction SilentlyContinue
            if (Test-Path ".\test-results\.last-run.json") {
                Write-Host "Warning: Could not delete .last-run.json - file may be locked" -ForegroundColor Red
            } else {
                Write-Host "Successfully deleted .last-run.json" -ForegroundColor Green
            }
        }
        
        # Then try to clean up the whole directory
        Get-ChildItem -Path ".\test-results" -Recurse | ForEach-Object {
            try {
                Remove-Item -Path $_.FullName -Force -ErrorAction SilentlyContinue
            } catch {
                Write-Host "Failed to delete $($_.FullName): $_" -ForegroundColor Red
            }
        }
    } catch {
        Write-Host "Failed to clean test-results directory: $_" -ForegroundColor Red
    }
} else {
    Write-Host "test-results directory not found" -ForegroundColor Green
}

# Try deleting the problematic file using different methods
Write-Host "Attempting alternative methods to delete the problematic file..." -ForegroundColor Yellow

# Method 1: Use .NET File class directly
if (Test-Path ".\test-results\.last-run.json") {
    try {
        [System.IO.File]::Delete("$((Get-Location).Path)\test-results\.last-run.json")
        Write-Host "Successfully deleted file using .NET File.Delete" -ForegroundColor Green
    } catch {
        Write-Host "Failed to delete using .NET File.Delete: $_" -ForegroundColor Red
    }
}

# Method 2: Try renaming first then deleting
if (Test-Path ".\test-results\.last-run.json") {
    try {
        Rename-Item -Path ".\test-results\.last-run.json" -NewName "old-last-run.json" -Force -ErrorAction SilentlyContinue
        if (Test-Path ".\test-results\old-last-run.json") {
            Remove-Item -Path ".\test-results\old-last-run.json" -Force
            Write-Host "Successfully used rename-then-delete method" -ForegroundColor Green
        }
    } catch {
        Write-Host "Failed to use rename-then-delete method: $_" -ForegroundColor Red
    }
}

Write-Host "Clean-up process complete" -ForegroundColor Cyan
Write-Host "If the issue persists, you may need to restart your computer" -ForegroundColor Yellow 