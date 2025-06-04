import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

/**
 * Automated CVX Browser Test
 * A simplified version of the test for the fully automated approach
 */

// Test configuration
const config = {
  credentials: {
    username: 'admin',
    password: 'password'
  },
  vaccine: {
    name: 'DTaP (Diphtheria, Tetanus, and acellular Pertussis)',
    brand: 'Infanrix',
    manufacturer: 'GlaxoSmithKline',
    doseNumber: '1',
    totalDoses: '5'
  },
  screenshotDir: './screenshots'
};

// Helper function for screenshots
function screenshotPath(name) {
  return path.join(config.screenshotDir, `${name}.png`);
}

test('CVX Code Auto-Population Test', async ({ page }) => {
  console.log('Starting CVX auto-population test');
  
  // Step 1: Navigate to the login page
  console.log('Step 1: Navigating to login page');
  await page.goto('/login');
  await page.screenshot({ path: screenshotPath('01-login-page') });
  
  // Step 2: Login
  console.log('Step 2: Logging in');
  await page.fill('input[name="username"]', config.credentials.username);
  await page.fill('input[name="password"]', config.credentials.password);
  await page.click('button[type="submit"]');
  
  // Wait for navigation after login
  await page.waitForNavigation({ timeout: 10000 }).catch(e => {
    console.log('Navigation timeout after login, continuing anyway');
  });
  await page.screenshot({ path: screenshotPath('02-after-login') });
  
  // Step 3: Navigate to patients page
  console.log('Step 3: Navigating to patients page');
  await page.goto('/patients');
  await page.screenshot({ path: screenshotPath('03-patients-page') });
  
  // Step 4: Select the first patient
  console.log('Step 4: Selecting a patient');
  const patientRows = page.locator('table tbody tr');
  const count = await patientRows.count();
  
  if (count > 0) {
    await patientRows.first().click();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: screenshotPath('04-patient-selected') });
  } else {
    console.log('No patients found, test cannot continue');
    await page.screenshot({ path: screenshotPath('04-no-patients') });
    test.fail(true, 'No patients found in the system');
    return;
  }
  
  // Step 5: Navigate to records
  console.log('Step 5: Navigating to records');
  await page.locator('a:has-text("Records"), a:has-text("Medical Records")').first().click().catch(() => {
    console.log('Could not click Records tab, trying direct navigation');
    return page.goto('/records');
  });
  await page.screenshot({ path: screenshotPath('05-records-page') });
  
  // Step 6: Add a new record
  console.log('Step 6: Adding a new record');
  await page.locator('button:has-text("Add Record"), button:has-text("New Record")').first().click();
  await page.waitForTimeout(1000);
  await page.screenshot({ path: screenshotPath('06-new-record-form') });
  
  // Step 7: Select record type as Vaccination
  console.log('Step 7: Selecting Vaccination record type');
  await page.selectOption('select#recordType, select[name="type"]', 'Vaccination').catch(() => {
    console.log('Could not select record type using standard selector, trying alternatives');
    const options = page.locator('select option:has-text("Vaccination")');
    return options.first().click();
  });
  await page.waitForTimeout(1000);
  await page.screenshot({ path: screenshotPath('07-record-type-selected') });
  
  // Step 8: Fill in vaccine details
  console.log('Step 8: Filling in vaccine details');
  
  // Select vaccine name
  await page.selectOption('#vaccineName, select[name="vaccineName"]', config.vaccine.name).catch(e => {
    console.log(`Error selecting vaccine: ${e.message}`);
    test.fail(true, `Could not select vaccine: ${e.message}`);
    return;
  });
  
  // Wait for CVX code to auto-populate
  await page.waitForTimeout(1000);
  await page.screenshot({ path: screenshotPath('08-vaccine-selected') });
  
  // Fill other fields
  await page.fill('#brandName, input[name="brandName"]', config.vaccine.brand);
  await page.fill('#manufacturer, input[name="manufacturer"]', config.vaccine.manufacturer);
  await page.fill('#doseNumber, input[name="doseNumber"]', config.vaccine.doseNumber);
  await page.fill('#totalDoses, input[name="totalDoses"]', config.vaccine.totalDoses);
  await page.screenshot({ path: screenshotPath('09-form-filled') });
  
  // Step 9: Verify CVX code auto-population
  console.log('Step 9: Verifying CVX code auto-population');
  const cvxCodeField = page.locator('#cvxCode, input[name="cvxCode"]');
  
  if (await cvxCodeField.isVisible()) {
    const cvxCodeValue = await cvxCodeField.inputValue();
    console.log(`Found CVX code: ${cvxCodeValue}`);
    
    // Verify that CVX code is not empty
    expect(cvxCodeValue).not.toBe('');
    
    // Verify that CVX code is either '20' (generic DTaP) or '106' (Infanrix-specific)
    expect(['20', '106', '107']).toContain(cvxCodeValue);
    
    console.log('✅ CVX code was successfully auto-populated');
  } else {
    console.log('Could not find CVX code field');
    await page.screenshot({ path: screenshotPath('error-no-cvx-field') });
    test.fail(true, 'Could not find CVX code field');
    return;
  }
  
  // Step 10: Save the record
  console.log('Step 10: Saving the record');
  await page.locator('button[type="submit"], button:has-text("Save")').click();
  await page.waitForTimeout(2000);
  await page.screenshot({ path: screenshotPath('10-record-saved') });
  
  console.log('Test completed successfully');
}); 