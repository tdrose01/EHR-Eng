// EHR Application Browser Automation Test - Enhanced with Error Handling
// Run with: npx playwright test ehr-test-automation.js --headed

const { test, expect } = require('@playwright/test');
const fs = require('fs');

// Helper to capture browser console logs to a file
async function setupConsoleLogs(page, filePath) {
  const logs = [];
  page.on('console', msg => {
    const text = `[${msg.type()}] ${msg.text()}`;
    logs.push(text);
    console.log(`Browser console: ${text}`);
  });
  
  // Save logs on page close
  page.on('close', () => {
    fs.writeFileSync(filePath, logs.join('\n'), 'utf8');
  });
}

test('Test EHR Application Login, Dashboard, and Navigation', async ({ page }) => {
  console.log('Starting EHR application test...');
  
  // Setup console logging
  await setupConsoleLogs(page, './test-results/browser-console.log');
  
  // Setup request monitoring
  page.on('request', request => {
    if (request.url().includes('/api/')) {
      console.log(`Network request: ${request.method()} ${request.url()}`);
    }
  });
  
  page.on('response', response => {
    if (response.url().includes('/api/')) {
      console.log(`Network response: ${response.status()} ${response.url()}`);
      
      // For dashboard API specifically, try to get response content
      if (response.url().includes('/api/dashboard')) {
        response.text().then(text => {
          console.log(`Dashboard API response content: ${text}`);
          fs.writeFileSync('./test-results/dashboard-api-response.json', text, 'utf8');
        }).catch(err => {
          console.log(`Could not read dashboard API response: ${err.message}`);
        });
      }
    }
  });
  
  // Capture uncaught errors in the page
  page.on('pageerror', error => {
    console.log(`Uncaught error in page: ${error.message}`);
    fs.appendFileSync('./test-results/page-errors.log', `${error.message}\n`, 'utf8');
  });
  
  try {
    // Navigate to the application
    console.log('Navigating to application...');
    await page.goto('http://localhost:8081', { timeout: 30000 });
    await page.screenshot({ path: './test-results/01-homepage.png' });
    console.log('Loaded homepage');
    
    // Check if we need to log in
    const isLoginPage = await page.locator('text=Login').isVisible().catch(() => false);
    if (isLoginPage) {
      console.log('Login page detected, attempting login...');
      
      // Fill in login credentials - using test credentials
      await page.fill('input[name="username"]', 'testuser');
      await page.fill('input[type="password"]', 'password');
      
      // Take screenshot of filled login form
      await page.screenshot({ path: './test-results/02-login-form.png' });
      
      // Click login button
      await page.click('button[type="submit"]');
      
      // Wait for navigation to complete
      await page.waitForLoadState('networkidle', { timeout: 30000 });
      console.log('Login submitted');
      
      // Check if login was successful
      const loginError = await page.locator('text=Invalid username or password').isVisible().catch(() => false);
      if (loginError) {
        console.log('Login failed! Invalid credentials.');
        await page.screenshot({ path: './test-results/03-login-failed.png' });
        return;
      }
    } else {
      console.log('Already logged in or no login required');
    }
    
    // Wait for dashboard to load
    console.log('Waiting for dashboard to load...');
    await page.waitForLoadState('networkidle', { timeout: 30000 });
    await page.screenshot({ path: './test-results/03-after-login.png' });
    
    // Check if we're on the dashboard
    const isDashboard = await page.url().includes('/dashboard');
    if (!isDashboard) {
      console.log('Navigating to dashboard...');
      
      // Try to find dashboard link with more flexible selector
      const dashboardLink = await page.locator('a[href="/dashboard"], a:has-text("Dashboard")').first();
      if (await dashboardLink.isVisible()) {
        await dashboardLink.click();
        await page.waitForLoadState('networkidle', { timeout: 30000 });
      } else {
        console.log('Could not find dashboard link, trying direct navigation');
        await page.goto('http://localhost:8081/dashboard', { timeout: 30000 });
        await page.waitForLoadState('networkidle', { timeout: 30000 });
      }
    }
    
    console.log('On dashboard page');
    await page.screenshot({ path: './test-results/04-dashboard.png' });
    
    // Save page HTML for debugging
    const dashboardHtml = await page.content();
    fs.writeFileSync('./test-results/dashboard.html', dashboardHtml, 'utf8');
    
    // Check for dashboard error
    const dashboardError = await page.locator('text=Failed to load dashboard statistics').isVisible().catch(() => false);
    if (dashboardError) {
      console.log('Dashboard error detected: Failed to load dashboard statistics');
      
      // Take a detailed screenshot of the error
      await page.screenshot({ path: './test-results/05-dashboard-error.png' });
      
      // Check browsers dev tools network tab for dashboard API request
      console.log('Checking for dashboard API requests...');
      
      // Click the OK button on the error dialog if it exists
      const okButton = await page.locator('button:has-text("OK")');
      if (await okButton.isVisible()) {
        await okButton.click();
        console.log('Clicked OK on error dialog');
      }
      
      // Try to open browser dev tools network tab
      await page.evaluate(() => {
        console.log('API_BASE_URL:', window.API_BASE_URL || 'not defined');
        console.log('Vite environment variables:', import.meta?.env || 'not available');
        console.log('Dashboard stats retrieval attempted');
      });
    } else {
      console.log('Dashboard loaded successfully without errors');
    }
    
    // Navigate to Patients page
    console.log('Navigating to Patients page...');
    const patientsLink = await page.locator('a[href="/patients"], a:has-text("Patients")').first();
    if (await patientsLink.isVisible()) {
      await patientsLink.click();
      await page.waitForLoadState('networkidle', { timeout: 30000 });
      await page.screenshot({ path: './test-results/06-patients-page.png' });
      
      // Check if patients loaded
      const patientsTable = await page.locator('table.patient-table, table:has-text("Patient ID")').isVisible().catch(() => false);
      if (patientsTable) {
        console.log('Patients table loaded successfully');
        
        // Save patients HTML for debugging
        const patientsHtml = await page.content();
        fs.writeFileSync('./test-results/patients.html', patientsHtml, 'utf8');
      } else {
        console.log('Patients table not found or failed to load');
        await page.screenshot({ path: './test-results/06b-patients-error.png' });
      }
    } else {
      console.log('Could not find Patients link, trying direct navigation');
      await page.goto('http://localhost:8081/patients', { timeout: 30000 });
      await page.waitForLoadState('networkidle', { timeout: 30000 });
      await page.screenshot({ path: './test-results/06-patients-direct.png' });
    }
    
    // Navigate to Medical Records page
    console.log('Navigating to Medical Records page...');
    const recordsLink = await page.locator('a[href="/records"], a:has-text("Records")').first();
    if (await recordsLink.isVisible()) {
      await recordsLink.click();
      await page.waitForLoadState('networkidle', { timeout: 30000 });
      await page.screenshot({ path: './test-results/07-records-page.png' });
      
      // Check if records loaded
      const recordsTable = await page.locator('table.records-table, table:has-text("Record ID")').isVisible().catch(() => false);
      if (recordsTable) {
        console.log('Medical records table loaded successfully');
        
        // Save records HTML for debugging
        const recordsHtml = await page.content();
        fs.writeFileSync('./test-results/records.html', recordsHtml, 'utf8');
      } else {
        console.log('Medical records table not found or failed to load');
        await page.screenshot({ path: './test-results/07b-records-error.png' });
      }
    } else {
      console.log('Could not find Records link, trying direct navigation');
      await page.goto('http://localhost:8081/records', { timeout: 30000 });
      await page.waitForLoadState('networkidle', { timeout: 30000 });
      await page.screenshot({ path: './test-results/07-records-direct.png' });
    }
    
    // Manually trigger API calls by refreshing dashboard
    console.log('Refreshing dashboard to observe API traffic...');
    await page.goto('http://localhost:8081/dashboard', { timeout: 30000 });
    await page.waitForLoadState('networkidle', { timeout: 30000 });
    await page.screenshot({ path: './test-results/08-final-dashboard.png' });
    
    // Extract information about API URLs from the console
    await page.evaluate(() => {
      // Try to get configuration details
      try {
        console.log('-------- API CONFIGURATION --------');
        // Get API URLs from the global scope or import.meta.env
        const apiBaseUrl = window.API_BASE_URL || import.meta?.env?.VITE_API_BASE_URL || 'Not found';
        console.log('API Base URL:', apiBaseUrl);
        
        // Look for dashboard service in global object
        const dashboardService = window.dashboardService || 'Not found in window';
        console.log('Dashboard Service:', typeof dashboardService);
        
        // Try to access localStorage for any API URLs
        const ehrToken = localStorage.getItem('ehrToken') || 'No token found';
        console.log('EHR Token exists:', ehrToken !== 'No token found');
        
        console.log('-------- END API CONFIGURATION --------');
      } catch (e) {
        console.error('Error extracting API information:', e);
      }
    });
    
    console.log('Browser automation test completed successfully');
  } catch (error) {
    console.error(`Test failed with error: ${error.message}`);
    await page.screenshot({ path: './test-results/error-screenshot.png' });
    throw error;
  }
}); 