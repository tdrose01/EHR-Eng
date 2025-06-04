const { test, expect } = require('@playwright/test');
const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

// Helper function to run SQL queries through the PostgreSQL CLI
async function runQuery(query) {
  try {
    // Configure your connection string to match your environment
    const connectionString = 'postgresql://tdrose01:password@localhost:5432/ehr_test';
    const { stdout, stderr } = await execPromise(`psql "${connectionString}" -c "${query}"`);
    if (stderr && !stderr.includes('SET')) {
      console.error(`Database query error: ${stderr}`);
    }
    return stdout;
  } catch (error) {
    console.error(`Error executing query: ${error.message}`);
    return null;
  }
}

test.describe('Patient management functionality', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to application and login
    await page.goto('http://localhost:8081/');
    
    // Check if login page is visible and login if needed
    if (await page.locator('input[type="text"][placeholder="Username"]').isVisible()) {
      await page.fill('input[type="text"][placeholder="Username"]', 'admin');
      await page.fill('input[type="password"][placeholder="Password"]', 'admin');
      await page.click('button:has-text("Sign In")');
      await page.waitForTimeout(2000);
    }
    
    // Navigate to Patients page
    await page.click('a:has-text("Patients")');
    await page.waitForTimeout(2000);
  });
  
  test('should display patients list from database', async ({ page }) => {
    // Check that patients are displayed in the UI
    const patientRows = page.locator('tbody tr');
    const uiCount = await patientRows.count();
    console.log(`Found ${uiCount} patients in the UI`);
    expect(uiCount).toBeGreaterThan(0);
    
    // Compare with database count
    const dbResult = await runQuery('SELECT COUNT(*) FROM patients');
    if (dbResult) {
      const dbCount = parseInt(dbResult.match(/\d+/)[0]);
      console.log(`Database has ${dbCount} patients`);
      
      // Verify that UI shows correct number of patients 
      // (might be less if pagination is used)
      expect(uiCount).toBeLessThanOrEqual(dbCount);
    }
  });
  
  test('should search for patients by name', async ({ page }) => {
    // Get a patient name from the first row
    const firstPatientName = await page.locator('tbody tr:first-child td:nth-child(2)').innerText();
    const searchTerm = firstPatientName.split(' ')[0]; // Use first name as search term
    
    // Enter search term
    await page.fill('input[placeholder="Search..."]', searchTerm);
    await page.waitForTimeout(1000);
    
    // Check results
    const patientRows = page.locator('tbody tr');
    const searchResultCount = await patientRows.count();
    expect(searchResultCount).toBeGreaterThan(0);
    
    // Verify that each result contains the search term
    for (let i = 0; i < searchResultCount; i++) {
      const patientName = await patientRows.nth(i).locator('td:nth-child(2)').innerText();
      expect(patientName.toLowerCase()).toContain(searchTerm.toLowerCase());
    }
    
    // Verify with database query
    const dbQuery = `SELECT COUNT(*) FROM patients WHERE name ILIKE '%${searchTerm}%'`;
    const dbResult = await runQuery(dbQuery);
    if (dbResult) {
      const dbCount = parseInt(dbResult.match(/\d+/)[0]);
      console.log(`Database found ${dbCount} patients matching '${searchTerm}'`);
      expect(searchResultCount).toBeLessThanOrEqual(dbCount);
    }
  });
  
  test('should navigate to patient details', async ({ page }) => {
    // Click view button on first patient
    await page.locator('tbody tr:first-child button:has-text("View")').click();
    await page.waitForTimeout(2000);
    
    // Verify we're on the patient details page
    await expect(page.locator('h3:has-text("Patient Details")')).toBeVisible();
    
    // Get patient ID from URL
    const url = page.url();
    const patientId = url.split('/').pop();
    
    // Verify with database that we're viewing the correct patient
    const dbQuery = `SELECT name FROM patients WHERE id = ${patientId}`;
    const dbResult = await runQuery(dbQuery);
    if (dbResult && !dbResult.includes('0 rows')) {
      // Get name from database result
      const dbName = dbResult.split('\n')[2].trim();
      console.log(`Database name for patient ${patientId}: ${dbName}`);
      
      // Get name displayed in UI
      const uiName = await page.locator('.patient-info h4').innerText();
      
      // Compare (allowing for formatting differences)
      expect(uiName.toLowerCase()).toContain(dbName.toLowerCase().split(' ')[0]);
    }
  });
}); 

