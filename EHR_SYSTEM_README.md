# EHR System Documentation

## Port Assignments

| Service      | Port | Status       |
|--------------|------|--------------|
| Frontend     | 8081 | Static Port  |
| Login API    | 8001 | Static Port  |
| Patient API  | 8002 | Static Port  |
| Records API  | 8003 | Static Port  |
| Vaccine API  | 8004 | Static Port  |

## Using the EHR Manager

A simplified management script has been created to handle all aspects of the EHR system.

### Quick Start

To start all services with a single command:

```
.\ehr_manager.bat
```

Or using PowerShell:

```
.\ehr_manager.ps1 start
```

### Available Commands

| Command  | Description                           | Example                     |
|----------|---------------------------------------|-----------------------------|
| start    | Start all EHR system services         | .\ehr_manager.ps1 start     |
| stop     | Stop all running services             | .\ehr_manager.ps1 stop      |
| restart  | Restart all EHR system services       | .\ehr_manager.ps1 restart   |
| status   | Check status of all services          | .\ehr_manager.ps1 status    |
| fix      | Apply fixes for known issues          | .\ehr_manager.ps1 fix       |

## Key Features

- **Fixed Ports**: All services use static ports for consistent access
- **Automatic Fixes**: The system automatically applies fixes for known issues, including the Records API indentation error
- **Comprehensive Service Management**: Start, stop, restart, and check status of all services from a single command
- **Reliable Process Management**: Gracefully handles killing old processes and starting new ones
- **Health Checks**: Verifies that services are not just running but also responding to requests

## Known Issues and Fixes

### Records API Indentation Error

The Records API had an indentation error in the `records_api.py` file that has been addressed by the management script. The script automatically:

1. Fixes the indentation
2. Uses a special startup method for the Records API
3. Verifies that the API is responding to requests

### Vaccine API Issues

The Vaccine API may show as "Running but not responding". This is a known issue with the API implementation and may require additional development work to resolve.

## Troubleshooting

### "Address already in use" errors

If you see errors about addresses already being in use, try stopping all services and starting again:

```
.\ehr_manager.ps1 restart
```

### API requests returning 404 errors

If API endpoints are returning 404 errors:

1. Check if all services are running with `.\ehr_manager.ps1 status`
2. Make sure you're using the correct URLs for each API
3. For Vaccine API issues, ensure all required dependencies are installed

## Accessing the System

Once all services are running, access the EHR system at:

**Frontend URL:** http://localhost:8081/

## Development Notes

The management script creates a special startup script for the Records API to ensure it launches correctly with the proper environment variables and configuration. This approach has proven more reliable than direct command execution. 