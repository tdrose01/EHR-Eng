# Run database tests with correct credentials
param (
    [string]$TestType = "all",  # Options: all, patients, records, vaccine, e2e, standalone, minimal
    [switch]$SkipSetup = $false
)

function Write-Section {
    param([string]$Message)
    Write-Host "`n========== $Message ==========`n" -ForegroundColor Cyan
}

# First make sure the EHR system is running
if (-not $SkipSetup) {
    # Stop any existing EHR system
    Write-Section "Stopping any existing EHR instances"
    .\ehr_manager_fixed.ps1 stop
    
    # Start a fresh instance
    Write-Section "Starting EHR system"
    .\ehr_manager_fixed.ps1 start
}

# Verify PostgreSQL connection
Write-Section "Verifying PostgreSQL"
$env:PGPASSWORD = "password"
$connectionString = "host=localhost port=5432 dbname=ehr_test user=tdrose01"
$result = & psql -c "SELECT 'PostgreSQL connection successful' AS result;" "$connectionString"

if ($LASTEXITCODE -eq 0) {
    Write-Host "PostgreSQL is running and test user has access to the database" -ForegroundColor Green
    Write-Host "Connection successful using: tdrose01@localhost:5432/ehr_test" -ForegroundColor Green
} else {
    Write-Host "PostgreSQL connection failed. Cannot proceed with tests." -ForegroundColor Red
    exit 1
}

# Clear the password environment variable
$env:PGPASSWORD = ""

# Run the appropriate test directly with npx
Write-Section "Running Playwright Tests: $TestType"

switch ($TestType) {
    "minimal" { 
        Write-Host "Running minimal test..." -ForegroundColor Yellow
        npx playwright test tests/minimal-test.js --headed
    }
    "standalone" { 
        Write-Host "Running standalone test..." -ForegroundColor Yellow
        npx playwright test tests/standalone-test.js --headed 
    }
    "patients" { 
        Write-Host "Running patients test..." -ForegroundColor Yellow
        npx playwright test tests/patients-test.js --headed 
    }
    "vaccine" { 
        Write-Host "Running vaccine test..." -ForegroundColor Yellow
        npx playwright test tests/vaccine-test.js --headed 
    }
    "e2e" { 
        Write-Host "Running e2e test..." -ForegroundColor Yellow
        npx playwright test tests/e2e-flow.js --headed 
    }
    "all" { 
        Write-Host "Running all tests..." -ForegroundColor Yellow
        npx playwright test tests/ --headed 
    }
    default { 
        Write-Host "Invalid test type. Using standalone test..." -ForegroundColor Yellow
        npx playwright test tests/standalone-test.js --headed 
    }
}

# Show results
Write-Section "Test Results"
if ($LASTEXITCODE -eq 0) {
    Write-Host "Tests completed successfully!" -ForegroundColor Green
} else {
    Write-Host "Tests failed with exit code $LASTEXITCODE" -ForegroundColor Red
}

# Open the HTML report
Write-Host "`nOpening test report..." -ForegroundColor Cyan
Start-Process "playwright-report\index.html" 