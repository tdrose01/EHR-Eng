# EHR System Test Automation Script
param (
    [string]$TestType = "all",  # Options: all, patients, records, vaccine, e2e
    [switch]$SkipStartup = $false,
    [switch]$KeepRunning = $false,
    [string]$DbUsername = "tdrose01",
    [string]$DbPassword = "password",
    [string]$DbName = "ehr_test"
)

$ErrorActionPreference = "Stop"
$EHR_MANAGER = ".\ehr_manager_fixed.ps1"

function Write-Section {
    param([string]$Message)
    Write-Host "`n========== $Message ==========`n" -ForegroundColor Cyan
}

function Verify-PostgreSQL {
    Write-Section "Verifying PostgreSQL"
    
    try {
        # First check if PostgreSQL is actually running
        try {
            $pgisready = & pg_isready -h localhost -p 5432
            if ($LASTEXITCODE -ne 0) {
                Write-Host "PostgreSQL server is not running or not accepting connections." -ForegroundColor Red
                Write-Host "Please make sure the PostgreSQL server is running before proceeding." -ForegroundColor Yellow
                return $false
            }
        } catch {
            Write-Host "Unable to check if PostgreSQL is running: $_" -ForegroundColor Red
            Write-Host "Make sure pg_isready is available in your PATH." -ForegroundColor Yellow
        }
        
        # Now attempt to connect with our credentials
        $env:PGPASSWORD = $DbPassword
        
        # Use a fully qualified connection string to verify database access
        $connectionString = "host=localhost port=5432 dbname=$DbName user=$DbUsername password=$DbPassword"
        
        # Just attempt a simple query to verify connectivity
        $result = & psql -c "SELECT 1 AS connection_test;" "$connectionString"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "PostgreSQL is running and test user has access to the database" -ForegroundColor Green
            Write-Host "Connection successful using: $DbUsername@localhost:5432/$DbName" -ForegroundColor Green
            return $true
        } else {
            Write-Host "PostgreSQL connection failed with credentials: $DbUsername@localhost:5432/$DbName" -ForegroundColor Red
            Write-Host "Make sure:" -ForegroundColor Yellow
            Write-Host "1. The database '$DbName' exists" -ForegroundColor Yellow
            Write-Host "2. The user '$DbUsername' exists and has the correct password" -ForegroundColor Yellow
            Write-Host "3. The user has proper permissions to access the database" -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host "Error checking PostgreSQL: $_" -ForegroundColor Red
        Write-Host "Make sure PostgreSQL is installed and available in PATH." -ForegroundColor Yellow
        return $false
    } finally {
        # Clear password from environment
        $env:PGPASSWORD = ""
    }
}

function Start-EHRSystem {
    Write-Section "Starting EHR System"
    try {
        & $EHR_MANAGER start
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to start EHR System"
        }
        
        # Give some time for all services to initialize
        Write-Host "Waiting for services to fully initialize..." -ForegroundColor Yellow
        Start-Sleep -Seconds 15
        
        # Verify services
        $result = & $EHR_MANAGER status
        return $true
    } catch {
        Write-Host "Error starting EHR System: $_" -ForegroundColor Red
        return $false
    }
}

function Stop-EHRSystem {
    Write-Section "Stopping EHR System"
    try {
        & $EHR_MANAGER stop
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to stop EHR System"
        }
        return $true
    } catch {
        Write-Host "Error stopping EHR System: $_" -ForegroundColor Red
        return $false
    }
}

function Run-PlaywrightTests {
    param([string]$TestType)
    
    Write-Section "Running Playwright Tests: $TestType"
    
    $testCommand = ""
    switch ($TestType) {
        "patients" { $testCommand = "npm run test:patients" }
        "records" { $testCommand = "npm run test:records" }
        "vaccine" { $testCommand = "npm run test:vaccine" }
        "e2e" { $testCommand = "npm run test:e2e" }
        default { $testCommand = "npm run test" }
    }
    
    try {
        Write-Host "Running test command: $testCommand" -ForegroundColor Yellow
        Invoke-Expression $testCommand
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Tests completed successfully!" -ForegroundColor Green
            return $true
        } else {
            Write-Host "Tests failed with exit code $LASTEXITCODE" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "Error running tests: $_" -ForegroundColor Red
        return $false
    }
}

function Open-TestReport {
    # Open the Playwright HTML report
    Write-Section "Opening Test Report"
    try {
        Start-Process "playwright-report\index.html"
    } catch {
        Write-Host "Error opening test report: $_" -ForegroundColor Red
    }
}

# Main script execution
try {
    $startTime = Get-Date
    
    # Verify PostgreSQL is running
    $postgresRunning = Verify-PostgreSQL
    if (-not $postgresRunning) {
        Write-Host "Cannot proceed without PostgreSQL. Exiting." -ForegroundColor Red
        exit 1
    }
    
    # Start EHR System if not skipped
    if (-not $SkipStartup) {
        $startSuccess = Start-EHRSystem
        if (-not $startSuccess) {
            Write-Host "Failed to start EHR System. Cannot proceed with tests." -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "Skipping EHR System startup as requested." -ForegroundColor Yellow
    }
    
    # Run the tests
    $testSuccess = Run-PlaywrightTests -TestType $TestType
    
    # Open the report
    Open-TestReport
    
    # Stop EHR System unless requested to keep running
    if (-not $KeepRunning -and -not $SkipStartup) {
        $stopSuccess = Stop-EHRSystem
    } elseif ($KeepRunning) {
        Write-Host "Keeping EHR System running as requested." -ForegroundColor Yellow
    }
    
    $endTime = Get-Date
    $duration = $endTime - $startTime
    
    Write-Section "Test Automation Summary"
    Write-Host "Duration: $($duration.Minutes) min $($duration.Seconds) sec"
    Write-Host "Test Result: $(if ($testSuccess) { 'PASSED' } else { 'FAILED' })"
    Write-Host "Test Report: $(Resolve-Path 'playwright-report\index.html')"
    
    # Return the appropriate exit code
    if ($testSuccess) { 
        exit 0 
    } else { 
        exit 1 
    }
    
} catch {
    Write-Host "Unhandled error in test automation script: $_" -ForegroundColor Red
    
    # Try to stop the EHR System in case of unhandled errors
    if (-not $KeepRunning -and -not $SkipStartup) {
        Stop-EHRSystem
    }
    
    exit 1
} 