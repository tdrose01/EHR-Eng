# EHR Application Fix Guide

## Quick Fix Instructions

1. **Double-click** on the file: `RUN-EHR-AS-ADMIN.bat`
2. When prompted, click **Yes** to allow administrator access
3. Wait for the script to complete its tasks:
   - Stopping existing Node.js processes
   - Fixing Vite cache permission issues
   - Starting the backend and frontend servers
4. Once complete, open your browser to **http://localhost:8081**
5. Login with:
   - Username: **admin**
   - Password: **password**

## What This Fix Addresses

The fix resolves several common issues:

1. Permission errors related to Vite cache files
2. Node.js process conflicts
3. Server startup sequence issues
4. Authentication problems

## If You Still Have Issues

If the automatic fix doesn't resolve your issue:

1. **Restart Your Computer** to clear any locked processes
2. Run the `RUN-EHR-AS-ADMIN.bat` script again after restart
3. Check if PostgreSQL is running (required for the backend)
4. If needed, manually start PostgreSQL with:
   ```
   pg_ctl -D "C:\path\to\postgres\data" start
   ```

## Troubleshooting Tips

- If you see this error: `EPERM: operation not permitted`, it means the script needs to be run with administrative privileges
- If you see `Connection refused` errors, make sure the backend server is running
- Both servers (backend and frontend) must be running for the application to work properly

## Technical Details

The fix script performs the following operations:

1. Kills all Node.js processes to release locked files
2. Uses administrator privileges to remove Vite cache files that have permission issues
3. Reinstalls npm dependencies to ensure proper configuration
4. Starts both servers in the correct sequence with proper environment variables

The application should now be accessible and allow you to log in successfully. 