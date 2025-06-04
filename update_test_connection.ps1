# PowerShell script to update PostgreSQL connection strings in all test files
param (
    [string]$Username,
    [string]$Password,
    [string]$DbHost = "localhost",
    [string]$Port = "5432",
    [string]$Database = "ehr_test"
)

$ErrorActionPreference = "Stop"

function Write-Section {
    param([string]$Message)
    Write-Host "`n========== $Message ==========`n" -ForegroundColor Cyan
}

# Prompt for username if not provided
if (-not $Username) {
    $Username = Read-Host "Enter database username (default: ehr_test_user)"
    if (-not $Username) {
        $Username = "ehr_test_user"
    }
}

# Prompt for password if not provided
if (-not $Password) {
    $securePassword = Read-Host "Enter database password (default: ehr_test_password)" -AsSecureString
    if ($securePassword.Length -eq 0) {
        $Password = "ehr_test_password"
    } else {
        $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
        $Password = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
        [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)
    }
}

Write-Section "Updating PostgreSQL Connection Strings in Test Files"

# Build the connection string
$connectionString = "postgresql://${Username}:${Password}@${DbHost}:${Port}/${Database}"
Write-Host "New connection string: $connectionString"

# Find all JavaScript test files
$testFiles = Get-ChildItem -Path "tests" -Filter "*.js" -Recurse | 
             Where-Object { $_.FullName -notlike "*node_modules*" }

$updateCount = 0

foreach ($file in $testFiles) {
    $content = Get-Content -Path $file.FullName -Raw
    
    # Look for existing connection string patterns
    $pattern = "const connectionString = ['`"]postgresql:\/\/[^'`"]+['`"]"
    
    if ($content -match $pattern) {
        # Replace the connection string
        $newContent = $content -replace $pattern, "const connectionString = '$connectionString'"
        Set-Content -Path $file.FullName -Value $newContent
        
        Write-Host "Updated connection string in: $($file.FullName)" -ForegroundColor Green
        $updateCount++
    }
}

Write-Section "Summary"
if ($updateCount -gt 0) {
    Write-Host "Updated connection string in $updateCount file(s)" -ForegroundColor Green
} else {
    Write-Host "No files were updated. Connection string pattern might not match." -ForegroundColor Yellow
}

Write-Host "`nTo verify the changes, you can run: Get-ChildItem -Path tests -Filter *.js -Recurse | Select-String -Pattern 'connectionString'" 