$envFile = "db_config.env"
$envContent = Get-Content $envFile

foreach ($line in $envContent) {
    if ($line -match '^\s*([^#][^=]+)=(.*)$') {
        $name = $matches[1].Trim()
        $value = $matches[2].Trim()
        [Environment]::SetEnvironmentVariable($name, $value, "Process")
    }
}

Write-Host "Environment variables set. You can now use psql without password prompts."
Write-Host "Example: psql -c 'SELECT current_database();'"

# Test connection
psql -c "SELECT 'Connection to PostgreSQL successful!' AS status;" 