$body = @{
    email = 'test2@example.com'
    password = 'test123'
    full_name = 'Test User 2'
} | ConvertTo-Json

Write-Host "Registering user..."
try {
    $response = Invoke-RestMethod -Uri 'http://localhost:8000/api/auth/register' -Method Post -Body $body -ContentType 'application/json' -ErrorAction Stop
    Write-Host "User registered successfully:"
    $response | ConvertTo-Json
} catch {
    Write-Host "Error registering user: $_"
    Write-Host "Status Code: $($_.Exception.Response.StatusCode.value__)"
    
    $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
    $reader.BaseStream.Position = 0
    $reader.DiscardBufferedData()
    $responseBody = $reader.ReadToEnd()
    Write-Host "Response body: $responseBody"
} 