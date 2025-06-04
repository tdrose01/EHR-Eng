# EHR Server Management Rules

## Overview

This document outlines the standard approach for starting, managing, and stopping the EHR system services to ensure consistent development and testing environments with no port conflicts.

## Server Components

The EHR system consists of three main components:

1. **Main API Server** (Port 8000)
   - Handles patient, record, and dashboard data
   - Runs on Flask with PostgreSQL

2. **Vaccine API Server** (Port 8004)
   - Manages vaccine-specific functionality
   - Provides schedule and next dose calculations

3. **Frontend Development Server** (Port 8081)
   - Vue.js application with Vite
   - Communicates with both API servers

## Standard Startup Procedure

Always use the Server Manager to handle proper startup of all components:

```bash
cd backend
python start_ehr_servers.py
```

The Server Manager automatically:
- Detects and kills any processes using the required ports
- Starts servers in the correct order with proper environment variables
- Provides consolidated logging to the `logs` directory
- Enables graceful shutdown of all services with Ctrl+C

## Environment Configuration

The server manager automatically sets the proper environment variables for communication between services:

- `VITE_API_BASE_URL`: http://localhost:8000
- `VITE_VACCINE_API_URL`: http://localhost:8004

## Troubleshooting

Common issues and their solutions:

1. **Connection Refused Errors**
   - Ensure PostgreSQL is running
   - Check if servers are running on expected ports

2. **Port Conflicts**
   - The Server Manager automatically handles port conflicts
   - If issues persist, manually check for processes using ports:
     ```bash
     # Windows
     netstat -ano | findstr :8000
     # Linux/macOS
     lsof -i :8000
     ```

3. **Failed to Load Dashboard Statistics**
   - Ensure Main API server is running (Port 8000)
   - Check PostgreSQL connection

## Testing Vaccine Functionality

To test vaccine functionality:
1. Navigate to Medical Records
2. Create a new record with type "Vaccination"
3. Use the vaccine dropdown to select a vaccine
4. Test the "Calculate" button for next dose dates

## Key Rules

1. **Always use the Server Manager script** - Never start services individually
2. **Check logs for errors** - All logs are in `backend/logs` directory with timestamps
3. **Use consistent ports** - Don't manually change port assignments
4. **Clean shutdown** - Always use Ctrl+C in the Server Manager terminal to stop all services

## Documentation

See `backend/README.md` for detailed documentation on:
- Installation requirements
- PostgreSQL setup
- Detailed API endpoints
- Database schema information
- Troubleshooting guides 