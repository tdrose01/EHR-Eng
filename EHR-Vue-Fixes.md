# EHR Vue Application - Troubleshooting and Fixes

This documentation provides an overview of issues encountered with the EHR Vue application and the solutions implemented to resolve them.

## Common Issues

### Dashboard Statistics Not Loading

The dashboard was failing to load statistics with the error: "Failed to load dashboard statistics". This was caused by several issues:

1. **Incorrect API endpoint configuration**: The dashboard API endpoint in `vite.config.js` was pointing to port 8002 instead of port 8000.
2. **Incorrect URL construction**: The `dashboardService.getStats()` method in `api.js` was constructing the URL incorrectly, causing a double `/api` prefix.
3. **Missing icon props**: The `StatCard` components in `Dashboard.vue` were missing required icon props.
4. **Permission issues**: Vite cache files were locked due to permission issues, preventing the frontend from starting properly.

### Permission Issues

Various permission-related errors have been encountered, particularly:

1. **"EPERM: operation not permitted"**: This occurs when trying to delete Vite cache files during development server startup.
2. **Access denied errors**: These occur when trying to terminate Node.js processes or delete locked files.

## Solutions Implemented

### 1. Fix Scripts

We've created several scripts to address these issues:

#### fix-vue-frontend.bat

A batch script that:
- Terminates running Node.js processes
- Clears Vite cache with elevated privileges
- Cleans npm cache
- Reinstalls dependencies
- Applies configuration fixes to:
  - `vite.config.js`
  - `api.js`
  - `Dashboard.vue`
- Starts the frontend with administrative privileges

#### fix-vue-frontend.ps1

A PowerShell version of the fix script with enhanced permissions handling:
- Requires administrative privileges to run
- Takes ownership of locked files
- Fixes Jest dependency conflicts
- Performs all the fixes from the batch version
- Uses more reliable regex patterns for file modifications

#### start-ehr-app.ps1

A comprehensive starter script that:
- Terminates existing Node.js and Python processes
- Starts the backend services (Main API and Vaccine API)
- Starts the frontend service with the correct permissions
- Opens the application in a browser
- Provides status information about all services

### 2. Configuration Fixes

#### vite.config.js Changes

```javascript
// Before
'/api/dashboard': {
  target: 'http://localhost:8002',  // INCORRECT
  changeOrigin: true,
  secure: false,
},

// After
'/api/dashboard': {
  target: 'http://localhost:8000',  // CORRECTED
  changeOrigin: true,
  secure: false,
},
```

#### api.js Changes

```javascript
// Before
async getStats() {
  try {
    const endpoint = `${API_BASE_URL}/api/dashboard/stats`; // INCORRECT (double /api)
    console.log('Attempting to fetch dashboard stats from:', endpoint);
    
    // Rest of the function...
  }
}

// After
async getStats() {
  try {
    const endpoint = '/api/dashboard/stats'; // CORRECTED
    console.log('Attempting to fetch dashboard stats from:', endpoint);
    
    // Rest of the function...
  }
}
```

#### Dashboard.vue Changes

Added missing icon props to StatCard components:

```vue
<StatCard 
  :value="stats.totalPatients"
  label="Total Patients"
  icon="fas fa-users"  <!-- Added -->
  @click="navigateTo('/patients')"
/>
```

### 3. Other Improvements

- Enhanced error handling in the `loadDashboardStats` function
- Added fallback to zero values instead of showing alerts
- Implemented proper console logging for diagnostics
- Created admin-privileged batch files for starting services

## How to Run the Application

1. **With Administrative Privileges (Recommended)**:
   - Run `start-ehr-app.ps1` (Right-click → Run with PowerShell as Administrator)
   - This script will start both backend and frontend services with proper permissions

2. **Fix Permissions Issues**:
   - If you encounter permission issues, run `fix-vue-frontend.ps1` as Administrator
   - This will reset Vite cache and fix any locked files

3. **Manual Startup**:
   - Start backend: Run `start_backend_admin.bat`
   - Start frontend: Run `start_frontend_admin.bat`

## Troubleshooting Checklist

If you still experience issues:

1. Verify backend services are running:
   - Main API should be accessible at http://localhost:8000
   - Vaccine API should be accessible at http://localhost:8004

2. Check browser console for JavaScript errors:
   - Press F12 in your browser
   - Navigate to the Console tab
   - Look for any error messages

3. Verify network requests:
   - In browser developer tools, go to the Network tab
   - Check if requests to `/api/dashboard/stats` are returning 200 OK

4. Clear browser cache:
   - Use Ctrl+F5 to force reload
   - Or try in an Incognito/Private window

5. Check if any Node.js processes are still running:
   - Open Task Manager and check for node.exe
   - Terminate any node.exe processes before restarting

## Contact

If you continue to experience issues after applying these fixes, please report them with:
1. Screenshots of any error messages
2. Browser console logs
3. Steps to reproduce the issue 