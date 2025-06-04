# EHR System API Test Script
Write-Host "EHR System API Test Script" -ForegroundColor Green
Write-Host "-----------------------" -ForegroundColor Green
Write-Host ""

# Function to test an API endpoint
function Test-ApiEndpoint {
    param (
        [string]$Name,
        [string]$Url,
        [switch]$AllowRedirect
    )
    
    try {
        Write-Host "Testing $Name API... " -NoNewline
        $params = @{
            Uri = $Url
            UseBasicParsing = $true
            TimeoutSec = 5
            ErrorAction = 'Stop'
        }
        
        if ($AllowRedirect) {
            $params.MaximumRedirection = 5
        }
        
        $response = Invoke-WebRequest @params
        
        if ($response.StatusCode -eq 200) {
            Write-Host "SUCCESS" -ForegroundColor Green
            return $true
        } else {
            Write-Host "FAILED (Status: $($response.StatusCode))" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "FAILED (Error: $($_.Exception.Message))" -ForegroundColor Red
        return $false
    }
}

# Define the endpoints to test
$endpoints = @(
    @{
        Name = "Login API"
        Url = "http://localhost:8001/api/health"
        AllowRedirect = $false
    },
    @{
        Name = "Patient API"
        Url = "http://localhost:8002/api/patients?limit=1"
        AllowRedirect = $false
    },
    @{
        Name = "Frontend"
        Url = "http://localhost:8081/"
        AllowRedirect = $true
    }
)

# Test each endpoint
$results = @()
Write-Host "Testing API endpoints..." -ForegroundColor Cyan
foreach ($endpoint in $endpoints) {
    $success = Test-ApiEndpoint -Name $endpoint.Name -Url $endpoint.Url -AllowRedirect:$endpoint.AllowRedirect
    $results += [PSCustomObject]@{
        Name = $endpoint.Name
        Url = $endpoint.Url
        Status = if ($success) { "Online" } else { "Offline" }
    }
}

# Test for process check - verify all expected processes are running
$requiredProcesses = @(
    @{ Name = "Login API"; Port = 8001 },
    @{ Name = "Patient API"; Port = 8002 },
    @{ Name = "Records API"; Port = 8003 },
    @{ Name = "Vaccine API"; Port = 8004 }
)

Write-Host "`nVerifying process status..." -ForegroundColor Cyan
$processResults = @()

foreach ($proc in $requiredProcesses) {
    $processId = $null
    $process = Get-NetTCPConnection -State Listen -LocalPort $proc.Port -ErrorAction SilentlyContinue | 
        Select-Object -ExpandProperty OwningProcess -ErrorAction SilentlyContinue
    
    if ($process) {
        $processInfo = Get-Process -Id $process -ErrorAction SilentlyContinue
        if ($processInfo) {
            Write-Host "Process for $($proc.Name) (Port $($proc.Port)) is running (PID: $process)" -ForegroundColor Green
            $processId = $process
            $status = "Running"
        } else {
            Write-Host "Process for $($proc.Name) (Port $($proc.Port)) is not valid" -ForegroundColor Red
            $status = "Invalid"
        }
    } else {
        Write-Host "No process found for $($proc.Name) (Port $($proc.Port))" -ForegroundColor Red
        $status = "Not Running"
    }
    
    $processResults += [PSCustomObject]@{
        Name = $proc.Name
        Port = $proc.Port
        ProcessId = $processId
        Status = $status
    }
}

# Display the results
Write-Host "`nAPI Endpoint Status:" -ForegroundColor Cyan
$results | Format-Table -Property Name, Url, Status

Write-Host "Process Status:" -ForegroundColor Cyan
$processResults | Format-Table -Property Name, Port, ProcessId, Status

# Check if all APIs and processes are up
$offlineCount = ($results | Where-Object { $_.Status -eq "Offline" } | Measure-Object).Count
$deadProcessCount = ($processResults | Where-Object { $_.Status -ne "Running" } | Measure-Object).Count

$allOnline = ($offlineCount -eq 0) -and ($deadProcessCount -eq 0)

if ($allOnline) {
    Write-Host "All EHR system components are online and working correctly!" -ForegroundColor Green
    Write-Host "You can now access the EHR system at: http://localhost:8081/" -ForegroundColor Green
} else {
    Write-Host "Some EHR system components are offline or not running. Please check the status above." -ForegroundColor Yellow
    Write-Host "You can restart all components by running: ./restart_ehr.ps1" -ForegroundColor Yellow
}

Write-Host "" 