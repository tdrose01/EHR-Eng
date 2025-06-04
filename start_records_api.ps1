# Use absolute path for the backend directory
$backendDir = "C:\tom\backend"

# Change to the backend directory
Set-Location $backendDir

# Run the command
python -c "import os; os.environ['PORT'] = '8003'; from api.records_api import app; app.run(host='0.0.0.0', port=8003, debug=False)"
