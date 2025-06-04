# EHR System Operation Guide

This guide provides instructions for running and troubleshooting the Electronic Health Record (EHR) system.

## Quick Start

1. Start the backend services:
   ```
   .\start_backend_admin.bat
   ```

2. Start the frontend service:
   ```
   .\start_frontend_simple.bat
   ```

3. Access the application at: http://localhost:8081

## All-In-One Startup

For a single-command startup experience:
```
.\start_ehr_system.bat
```
This script will:
- Run a diagnostic check
- Start backend services
- Start frontend service
- Open the application in your browser

## Troubleshooting

If you encounter any issues with the EHR system, you can run the diagnostic tool:

```
powershell -ExecutionPolicy Bypass -File .\ehr-diagnostic.ps1
```

The diagnostic tool will:
- Check if all services are running
- Test API endpoints
- Verify database and file system
- Attempt to fix common issues automatically

### Common Issues and Solutions

#### "Failed to load dashboard statistics" Error

This error may occur due to one of the following reasons:

1. **Backend API not running with proper permissions**
   - Solution: Use `.\start_backend_admin.bat` to start the backend with administrator privileges

2. **Database access permission issues**
   - Solution: Run the diagnostic script to fix permissions automatically

3. **Frontend is not properly connecting to the backend**
   - Solution: Restart both frontend and backend services

4. **Browser cache issues**
   - Solution: Clear your browser cache or open the application in incognito/private mode

#### Vite Cache Permission Issues

If you encounter errors like:
```
Error: EPERM: operation not permitted, unlink 'C:\tom\ehr-vue-app\node_modules\.vite\deps\chunk-VT7FWPCL.js'
```

Use one of these solutions:

1. **Quick fix**: Run `.\fix-vite-cache.bat` to clear cache and start frontend with admin rights
2. **Complete rebuild**: Run `.\rebuild-vite-cache.bat` for a more thorough solution
3. **Manual steps**: See `VITE-CACHE-TROUBLESHOOTING.md` for detailed instructions

#### Browser Not Opening

If browser tests or automated testing isn't working properly:

1. Try the simple test page:
   ```
   .\open-test-page.bat
   ```

2. Verify backend server status:
   ```
   powershell -ExecutionPolicy Bypass -File .\check-servers.ps1
   ```

## File Reference

### Batch Files

- `start_ehr_system.bat` - All-in-one system starter
- `start_backend_admin.bat` - Starts backend services with admin privileges
- `start_frontend_admin.bat` - Starts frontend with admin privileges
- `start_frontend_simple.bat` - Starts frontend with standard privileges
- `fix-vite-cache.bat` - Resolves Vite cache permission issues
- `rebuild-vite-cache.bat` - Completely rebuilds the Vite cache
- `open-test-page.bat` - Opens a test page in Chrome for diagnostic purposes

### PowerShell Scripts

- `ehr-diagnostic.ps1` - Comprehensive diagnostic and repair tool
- `check-servers.ps1` - Checks server status and provides detailed diagnostics
- `fix-dashboard-api.ps1` - Focuses on fixing dashboard API issues
- `chrome-launch-test.ps1` - Tests Chrome launching capabilities

### Documentation

- `VITE-CACHE-TROUBLESHOOTING.md` - Detailed guide for resolving Vite cache issues

## Advanced Testing

For advanced testing and automation, use:

```
powershell -ExecutionPolicy Bypass -File .\browser-popup-test.ps1
```

## System Requirements

- Windows 10 or later
- Node.js (14.x or later)
- Python (3.9 or later)
- Administrator access (for certain operations)

## Support

For additional support, please:
1. Run the diagnostic tool and review its output
2. Check application logs in the backend/logs directory
3. Contact technical support with details of the issue 