# Vite Cache Permission Issues Troubleshooting Guide

## Common Error Messages

If you encounter any of these errors when starting the frontend server:

```
Error: EPERM: operation not permitted, unlink '[path]\node_modules\.vite\deps\chunk-[HASH].js'
```

```
Error: EBUSY: resource busy or locked, rmdir '[path]\node_modules\.vite'
```

This indicates a Vite cache permission issue, which is common in Windows environments.

## Quick Fix

Run our automated fix script:

```
.\fix-vite-cache.bat
```

This script will:
1. Terminate any Node.js processes that might be locking the files
2. Clear the Vite cache directory
3. Start the frontend with administrative privileges

## Manual Fix Steps

If the script doesn't work, follow these manual steps:

### Step 1: Close All Node.js Processes

```powershell
# Using PowerShell
Stop-Process -Name "node" -Force -ErrorAction SilentlyContinue

# Using Command Prompt
taskkill /F /IM node.exe
```

### Step 2: Remove the Vite Cache Directory

```
cd ehr-vue-app
rmdir /S /Q node_modules\.vite
```

### Step 3: Start the Frontend with Administrative Privileges

```
.\start_frontend_admin.bat
```

## Advanced Troubleshooting

If issues persist, try these additional steps:

### Clear npm Cache

```
npm cache clean --force
```

### Start with No Cache Flag

```
cd ehr-vue-app
npm run dev -- --port 8081 --force --no-cache
```

### Check for File Locking Issues

1. Install Process Explorer from Microsoft Sysinternals
2. Search for any processes that have open handles to files in the Vite cache directory
3. Close those processes and retry

### Reinstall Node Modules (Last Resort)

```
cd ehr-vue-app
rmdir /S /Q node_modules
npm install
```

## Prevention

To prevent these issues in the future:

1. Always use the `start_frontend_admin.bat` script to start the frontend
2. Ensure you properly close Node.js processes before shutting down
3. Consider running your development environment as an administrator 

## Additional Resources

- [Vite Documentation](https://vitejs.dev/)
- [Node.js Windows Issues](https://nodejs.org/en/download/) 