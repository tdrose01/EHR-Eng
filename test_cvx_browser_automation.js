import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

/**
 * CVX Code Browser Automation Test
 * This script tests the CVX code auto-population functionality in the UI
 */

// Test configuration
const config = {
  baseUrl: 'http://localhost:5173', // Primary port to try
  fallbackPorts: [8080, 8081, 3000, 5174, 5175], // Additional ports to try
  credentials: {
    username: 'admin', // Default test username
    password: 'password' // Default test password
  },
  vaccine: {
    name: 'DTaP (Diphtheria, Tetanus, and acellular Pertussis)',
    brand: 'Infanrix',
    manufacturer: 'GlaxoSmithKline',
    doseNumber: '1',
    totalDoses: '5'
  },
  screenshotDir: './cvx-test-results/screenshots'
};

// Create screenshot directory if it doesn't exist
if (!fs.existsSync(config.screenshotDir)) {
  fs.mkdirSync(config.screenshotDir, { recursive: true });
}

// Helper function to get screenshot path
function getScreenshotPath(name) {
  return path.join(config.screenshotDir, `${name}.png`);
}

// Update the screenshot paths - use basic names with no directories
async function takeScreenshot(page, name) {
  try {
    await page.screenshot({ path: `${name}.png` });
  } catch (error) {
    console.log(`Failed to take screenshot ${name}: ${error.message}`);
  }
}

test.describe('CVX Code Auto-Population Tests', () => {
  // Helper function to find a working frontend URL
  async function findWorkingFrontendUrl(page) {
    // Try the primary URL first
    try {
      await page.goto(config.baseUrl, { timeout: 5000 });
      if (page.url().includes(config.baseUrl)) {
        console.log(`Connected to primary frontend URL: ${config.baseUrl}`);
        return config.baseUrl;
      }
    } catch (error) {
      console.log(`Could not connect to primary URL: ${error.message}`);
    }
    
    // Try fallback ports
    for (const port of config.fallbackPorts) {
      const url = `http://localhost:${port}`;
      try {
        console.log(`Trying fallback URL: ${url}`);
        await page.goto(url, { timeout: 5000 });
        console.log(`Connected to fallback URL: ${url}`);
        return url;
      } catch (error) {
        console.log(`Could not connect to ${url}: ${error.message}`);
      }
    }
    
    return null;
  }
  
  test('should auto-populate CVX code when creating a vaccine record', async ({ page }) => {
    // Find a working frontend URL
    const frontendUrl = await findWorkingFrontendUrl(page);
    if (!frontendUrl) {
      test.fail(true, 'Could not connect to any frontend URL');
      return;
    }
    
    console.log('Step 1: Logging in to the system');
    await page.goto(`${frontendUrl}/login`);
    
    // Check if we're already on a login page
    const usernameField = page.locator('input[name="username"]');
    const passwordField = page.locator('input[name="password"]');
    
    if (await usernameField.isVisible() && await passwordField.isVisible()) {
      // Fill login form
      await usernameField.fill(config.credentials.username);
      await passwordField.fill(config.credentials.password);
      
      // Take screenshot of login page
      await takeScreenshot(page, 'login-page');
      
      // Click login button
      await page.locator('button[type="submit"]').click();
      
      // Wait for navigation
      await page.waitForNavigation({ timeout: 10000 }).catch(e => {
        console.log('Navigation timeout after login, continuing anyway...');
      });
    } else {
      console.log('Not on login page or already logged in');
    }
    
    console.log('Step 2: Navigating to patients page');
    // Try to navigate to patients
    await page.goto(`${frontendUrl}/patients`);
    
    // Take screenshot of patients page
    await takeScreenshot(page, 'patients-page');
    
    console.log('Step 3: Selecting a patient');
    // Click on the first patient in the list
    try {
      await page.locator('.patients-table tbody tr').first().click();
    } catch (error) {
      console.log('Could not click on patient row, trying alternative selector');
      try {
        await page.locator('table tbody tr').first().click();
      } catch (error2) {
        console.log('Still could not find a patient to click on - taking screenshot');
        await takeScreenshot(page, 'no-patients-found');
        test.fail(true, 'Could not find a patient to select');
        return;
      }
    }
    
    // Wait for patient details to load
    await page.waitForTimeout(1000);
    
    console.log('Step 4: Navigating to patient records');
    // Go to the Records tab for this patient
    try {
      await page.locator('a:has-text("Records")').click();
    } catch (error) {
      console.log('Could not find Records tab, trying alternative navigation');
      await page.goto(`${frontendUrl}/records`);
    }
    
    // Take screenshot of records page
    await takeScreenshot(page, 'records-page');
    
    console.log('Step 5: Creating new vaccination record');
    // Click on "Add Record" or similar button
    try {
      await page.locator('button:has-text("Add Record"), button:has-text("New Record")').first().click();
    } catch (error) {
      console.log('Could not find Add Record button, taking screenshot');
      await takeScreenshot(page, 'no-add-record-button');
      test.fail(true, 'Could not find Add Record button');
      return;
    }
    
    // Wait for the new record form to appear
    await page.waitForTimeout(1000);
    
    // Take screenshot of new record form
    await takeScreenshot(page, 'new-record-form');
    
    console.log('Step 6: Selecting vaccination record type');
    // Select Vaccination as the record type
    try {
      await page.selectOption('select#recordType, select[name="type"]', 'Vaccination');
    } catch (error) {
      console.log('Could not select Vaccination type, trying alternative approach');
      const recordTypeOptions = page.locator('select option:has-text("Vaccination")');
      if (await recordTypeOptions.count() > 0) {
        const value = await recordTypeOptions.getAttribute('value');
        await page.selectOption('select', value);
      }
    }
    
    // Wait for form to update based on selection
    await page.waitForTimeout(1000);
    
    console.log('Step 7: Filling out vaccination details');
    // Fill out the vaccination form
    try {
      // Select vaccine name
      await page.selectOption('#vaccineName, select[name="vaccineName"]', config.vaccine.name);
      
      // Wait for CVX code to auto-populate
      await page.waitForTimeout(1000);
      
      // Fill other fields
      await page.fill('#brandName, input[name="brandName"]', config.vaccine.brand);
      await page.fill('#manufacturer, input[name="manufacturer"]', config.vaccine.manufacturer);
      await page.fill('#doseNumber, input[name="doseNumber"]', config.vaccine.doseNumber);
      await page.fill('#totalDoses, input[name="totalDoses"]', config.vaccine.totalDoses);
      
      // Take screenshot after filling form
      await takeScreenshot(page, 'filled-vaccine-form');
      
      console.log('Step 8: Verifying CVX code auto-population');
      // Check if CVX code field has been auto-populated
      const cvxCodeField = page.locator('#cvxCode, input[name="cvxCode"]');
      
      if (await cvxCodeField.isVisible()) {
        const cvxCodeValue = await cvxCodeField.inputValue();
        console.log(`Found CVX code: ${cvxCodeValue}`);
        
        // Verify that CVX code is not empty
        expect(cvxCodeValue).not.toBe('');
        
        // Verify that CVX code is either '20' (generic DTaP) or '106' (Infanrix-specific)
        expect(['20', '106', '107']).toContain(cvxCodeValue);
        
        console.log('✅ CVX code was successfully auto-populated!');
      } else {
        console.log('Could not find CVX code field, taking screenshot');
        await takeScreenshot(page, 'no-cvx-code-field');
        test.fail(true, 'Could not find CVX code field');
      }
      
      console.log('Step 9: Submitting the form');
      // Submit the form
      await page.locator('button[type="submit"], button:has-text("Save")').click();
      
      // Wait for form submission to complete
      await page.waitForTimeout(2000);
      
      // Take final screenshot
      await takeScreenshot(page, 'after-submission');
      
    } catch (error) {
      console.log(`Error during test: ${error.message}`);
      await takeScreenshot(page, 'error-screenshot');
      test.fail(true, error.message);
    }
  });
}); 