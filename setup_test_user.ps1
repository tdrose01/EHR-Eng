# PowerShell script to create a test user for EHR automation
param (
    [string]$PgHost = "localhost",
    [string]$PgPort = "5432",
    [string]$PgUser = "postgres",
    [string]$PgPassword = "postgres",
    [string]$TestUsername,
    [string]$TestPassword
)

$ErrorActionPreference = "Stop"

function Write-Section {
    param([string]$Message)
    Write-Host "`n========== $Message ==========`n" -ForegroundColor Cyan
}

# Prompt for test username if not provided
if (-not $TestUsername) {
    $TestUsername = Read-Host "Enter test username (default: ehr_test_user)"
    if (-not $TestUsername) {
        $TestUsername = "ehr_test_user"
    }
}

# Prompt for test password if not provided
if (-not $TestPassword) {
    $securePassword = Read-Host "Enter test password (default: ehr_test_password)" -AsSecureString
    if ($securePassword.Length -eq 0) {
        $TestPassword = "ehr_test_password"
    } else {
        $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
        $TestPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
        [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)
    }
}

# Create a temporary SQL file with the user-provided credentials
$tempSqlFile = "temp_create_user.sql"
$sqlContent = Get-Content -Path "create_test_user.sql" -Raw
$sqlContent = $sqlContent -replace "ehr_test_user", $TestUsername
$sqlContent = $sqlContent -replace "ehr_test_password", $TestPassword
Set-Content -Path $tempSqlFile -Value $sqlContent

# Set environment variable for password
$env:PGPASSWORD = $PgPassword

Write-Section "Creating Test User for EHR Automation"
Write-Host "Test username: $TestUsername"

try {
    # Check if psql command is available
    $psqlVersion = & psql --version
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: 'psql' command not found. Please ensure PostgreSQL is installed and added to your PATH." -ForegroundColor Red
        exit 1
    }
    
    Write-Host "PostgreSQL CLI found: $psqlVersion"
    Write-Host "Creating test user and database..."
    
    # Run the SQL script to create the test user and database
    $result = & psql -h $PgHost -p $PgPort -U $PgUser -f $tempSqlFile
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`nTest user created successfully!" -ForegroundColor Green
        Write-Host "Connection string: postgresql://${TestUsername}:${TestPassword}@localhost:5432/ehr_test" -ForegroundColor Green
        
        # Test the connection with the new user
        Write-Host "`nTesting connection with the new user..." -ForegroundColor Yellow
        $env:PGPASSWORD = $TestPassword
        $testResult = & psql -h $PgHost -p $PgPort -U $TestUsername -d ehr_test -c "SELECT 'Connection successful!' AS result;"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Connection test successful!" -ForegroundColor Green
        } else {
            Write-Host "Warning: Could not connect with the new user. You may need to adjust PostgreSQL's pg_hba.conf to allow connections." -ForegroundColor Yellow
        }
    } else {
        Write-Host "Error creating test user. Check the output above for more details." -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
} finally {
    # Clean up temporary file
    if (Test-Path $tempSqlFile) {
        Remove-Item -Path $tempSqlFile -Force
    }
    
    # Clear password from environment
    $env:PGPASSWORD = ""
}

Write-Section "Next Steps"
Write-Host "1. The test user and database are now created."
Write-Host "2. You should update your test scripts to use this connection string:"
Write-Host "   postgresql://${TestUsername}:${TestPassword}@localhost:5432/ehr_test" -ForegroundColor Yellow
Write-Host "3. Or run update_test_connection.ps1 with the proper parameters to update all test files."
Write-Host ""
Write-Host "To update all test files with the new connection info:" -ForegroundColor Cyan
Write-Host ".\update_test_connection.ps1 -Username '$TestUsername' -Password '$TestPassword'" -ForegroundColor Yellow 