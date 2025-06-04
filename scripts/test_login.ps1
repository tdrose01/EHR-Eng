$formData = "username=admin@example.com&password=admin123"

Write-Host "Logging in as admin..."
try {
    $response = Invoke-RestMethod -Uri 'http://localhost:8000/api/auth/login' -Method Post -Body $formData -ContentType 'application/x-www-form-urlencoded' -ErrorAction Stop
    Write-Host "Login successful:"
    $response | ConvertTo-Json
    
    # Store the session cookie for subsequent requests
    $sessionId = $response.access_token
    Write-Host "Session ID: $sessionId"
    
    # Test accessing a protected endpoint
    Write-Host "`nTesting access to /api/auth/me..."
    $headers = @{
        "Cookie" = "session_id=$sessionId"
    }
    $userInfo = Invoke-RestMethod -Uri 'http://localhost:8000/api/auth/me' -Method Get -Headers $headers
    Write-Host "User info:"
    $userInfo | ConvertTo-Json
    
    # Test accessing patients endpoint
    Write-Host "`nTesting access to /api/patients..."
    $patients = Invoke-RestMethod -Uri 'http://localhost:8000/api/patients' -Method Get -Headers $headers
    Write-Host "Number of patients: $($patients.Count)"
    
    # Test logout
    Write-Host "`nTesting logout..."
    $logoutResponse = Invoke-RestMethod -Uri 'http://localhost:8000/api/auth/logout' -Method Post -Headers $headers
    Write-Host "Logout response:"
    $logoutResponse | ConvertTo-Json
    
    # Try accessing protected endpoint after logout
    Write-Host "`nTrying to access /api/auth/me after logout..."
    try {
        $userInfoAfterLogout = Invoke-RestMethod -Uri 'http://localhost:8000/api/auth/me' -Method Get -Headers $headers
        Write-Host "Still authenticated (this shouldn't happen)"
    } catch {
        Write-Host "Correctly received unauthorized error after logout"
    }
} catch {
    Write-Host "Error during login: $_"
    Write-Host "Status Code: $($_.Exception.Response.StatusCode.value__)"
    
    try {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $reader.BaseStream.Position = 0
        $reader.DiscardBufferedData()
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response body: $responseBody"
    } catch {
        Write-Host "Could not read response body: $_"
    }
} 