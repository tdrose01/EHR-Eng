# PowerShell script to set up test data
$ErrorActionPreference = "Stop"

Write-Host "Setting up test data..." -ForegroundColor Cyan

# Function to wait for API server
function Wait-ApiServer {
    param (
        [int]$maxRetries = 10,
        [int]$port = 8004
    )
    
    for ($i = 1; $i -le $maxRetries; $i++) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:$port/api/health" -Method GET -TimeoutSec 2
            if ($response.StatusCode -eq 200) {
                Write-Host "API server is ready" -ForegroundColor Green
                return $true
            }
        } catch {
            Write-Host "Waiting for API server (attempt $i of $maxRetries)..." -ForegroundColor Yellow
            Start-Sleep -Seconds 2
        }
    }
    
    Write-Host "API server not responding" -ForegroundColor Red
    return $false
}

# Start API server if not running
Write-Host "Starting API server..." -ForegroundColor Yellow
$apiProcess = Start-Process -FilePath "powershell" -ArgumentList "-Command cd backend && python -m api.vaccine_api" -WindowStyle Hidden -PassThru
Start-Sleep -Seconds 5

# Wait for API server
if (-not (Wait-ApiServer)) {
    Write-Host "Could not connect to API server" -ForegroundColor Red
    exit 1
}

# Create test patient
$patient = @{
    firstName = "Test"
    lastName = "Patient"
    dateOfBirth = "1990-01-01"
    gender = "F"
    address = "123 Test St"
    phone = "555-0123"
    email = "test@example.com"
}

Write-Host "Creating test patient..." -ForegroundColor Yellow
try {
    # First check if the patient already exists
    $existingPatients = Invoke-RestMethod -Uri "http://localhost:8004/api/patients" -Method GET
    $existingPatient = $existingPatients | Where-Object { $_.firstName -eq $patient.firstName -and $_.lastName -eq $patient.lastName }
    
    if ($existingPatient) {
        Write-Host "Test patient already exists" -ForegroundColor Green
    } else {
        $response = Invoke-RestMethod -Uri "http://localhost:8004/api/patients" -Method POST -Body ($patient | ConvertTo-Json) -ContentType "application/json"
        Write-Host "Test patient created successfully" -ForegroundColor Green
    }
} catch {
    Write-Host "Failed to create test patient: $_" -ForegroundColor Red
    exit 1
}

Write-Host "Test data setup complete" -ForegroundColor Green

# Keep the API server running for the test
Write-Host "Keeping API server running for tests..." -ForegroundColor Yellow

# Stop API server if we started it
if ($apiProcess -and !$apiProcess.HasExited) {
    Stop-Process -Id $apiProcess.Id -Force -ErrorAction SilentlyContinue
} 