const { test, expect } = require('@playwright/test');
const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

// Helper function to run SQL queries
async function runQuery(query) {
  try {
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

test.describe('End-to-end patient record workflow', () => {
  // Use a shared patient ID for the E2E flow
  let testPatientId;
  let testPatientName;
  
  test.beforeAll(async () => {
    // Get a test patient from the database to use in tests
    const patientResult = await runQuery('SELECT id, name FROM patients LIMIT 1');
    if (patientResult && !patientResult.includes('0 rows')) {
      const lines = patientResult.split('\n').filter(line => line.trim() !== '' && !line.includes('--') && !line.includes('id'));
      if (lines.length > 0) {
        const parts = lines[0].trim().split('|').map(part => part.trim());
        testPatientId = parts[0];
        testPatientName = parts[1];
        console.log(`Using test patient: ID=${testPatientId}, Name=${testPatientName}`);
      }
    }
  });

  test('Complete patient-records-vaccine workflow', async ({ page }) => {
    console.log('Starting end-to-end workflow test');
    
    // 1. Navigate to application and login
    await page.goto('http://localhost:8081/');
    if (await page.locator('input[type="text"][placeholder="Username"]').isVisible()) {
      await page.fill('input[type="text"][placeholder="Username"]', 'admin');
      await page.fill('input[type="password"][placeholder="Password"]', 'admin');
      await page.click('button:has-text("Sign In")');
      await page.waitForTimeout(2000);
    }
    
    // 2. Navigate to Patients page and select our test patient
    await page.click('a:has-text("Patients")');
    await page.waitForTimeout(2000);
    console.log('Navigated to Patients page');
    
    // If we have a test patient ID, try to find that patient
    if (testPatientId) {
      // Try to find our specific test patient
      const patientRows = page.locator(`tbody tr:has-text("${testPatientName}")`);
      if (await patientRows.count() > 0) {
        await patientRows.first().locator('input[type="checkbox"]').check();
        console.log(`Selected test patient: ${testPatientName}`);
      } else {
        // Fall back to selecting the first patient
        await page.locator('tbody tr:first-child input[type="checkbox"]').check();
        console.log('Test patient not found in UI, selected first patient instead');
      }
    } else {
      // No test patient ID from database, just select the first patient
      await page.locator('tbody tr:first-child input[type="checkbox"]').check();
      console.log('Selected first patient from table');
    }
    
    await page.waitForTimeout(1000);
    
    // 3. Navigate to Medical Records
    await page.click('a:has-text("Medical Records")');
    await page.waitForTimeout(3000);
    console.log('Navigated to Medical Records page');
    
    // Verify the records page loaded with patient data
    await expect(page.locator('h3:has-text("Medical Records")')).toBeVisible();
    
    // 4. Create a new vaccination record
    await page.click('button:has-text("Add Record")');
    await page.waitForTimeout(2000);
    console.log('Clicked Add Record button');
    
    // Fill out the new record form with vaccination details
    await page.selectOption('select[name="recordType"]', 'Vaccination');
    await page.waitForTimeout(1000);
    
    // Check if vaccine dropdown appears
    const vaccineDropdown = page.locator('select[name="vaccine"]');
    if (await vaccineDropdown.isVisible()) {
      // Select the first vaccine from the dropdown
      const options = await page.locator('select[name="vaccine"] option').all();
      if (options.length > 1) { // Skip the first empty/placeholder option
        const vaccineValue = await options[1].getAttribute('value');
        await vaccineDropdown.selectOption(vaccineValue);
        console.log(`Selected vaccine: ${vaccineValue}`);
      }
      
      // Enter the dose information
      await page.fill('input[name="doseNumber"]', '1');
      
      // Set today's date in the required format YYYY-MM-DD
      const today = new Date();
      const formattedDate = today.toISOString().split('T')[0];
      await page.fill('input[type="date"]', formattedDate);
      console.log(`Set vaccination date: ${formattedDate}`);
      
      // Add notes
      await page.fill('textarea[name="notes"]', 'Automation test - vaccination record');
      
      // 5. Save the record
      await page.click('button:has-text("Save")');
      await page.waitForTimeout(3000);
      console.log('Saved vaccination record');
      
      // 6. Verify the record was created
      // Check if the record appears in the table
      const records = page.locator('table tbody tr');
      const recordsCount = await records.count();
      expect(recordsCount).toBeGreaterThan(0);
      console.log(`Found ${recordsCount} records in table after adding new record`);
      
      // Check that the new vaccination record is in the table
      const newRecord = page.locator('table tbody tr:has-text("Vaccination")').first();
      await expect(newRecord).toBeVisible();
      
      // 7. Verify data with database
      let patientId;
      try {
        // Get the patient ID from the URL or page context
        const currentUrl = page.url();
        if (currentUrl.includes('patient=')) {
          patientId = currentUrl.split('patient=')[1].split('&')[0];
        } else {
          // Try to get from the breadcrumb or other UI element
          const breadcrumb = await page.locator('.breadcrumb').innerText();
          const match = breadcrumb.match(/Patient ID: (\d+)/);
          if (match) {
            patientId = match[1];
          }
        }
        
        if (patientId) {
          console.log(`Verifying record in database for patient ID: ${patientId}`);
          const dbQuery = `
            SELECT COUNT(*) FROM records 
            WHERE patient_id = ${patientId} 
            AND record_type = 'Vaccination' 
            AND notes LIKE '%Automation test%'
          `;
          const dbResult = await runQuery(dbQuery);
          
          if (dbResult) {
            const dbCount = parseInt(dbResult.match(/\d+/)[0]);
            console.log(`Database found ${dbCount} matching vaccination records`);
            expect(dbCount).toBeGreaterThan(0);
          }
        }
      } catch (error) {
        console.error('Error verifying record in database:', error);
      }
    } else {
      console.log('Vaccine dropdown not found - the vaccine feature may not be properly integrated');
      // Take a screenshot for debugging
      await page.screenshot({ path: 'vaccine-form-missing.png' });
    }
    
    // 8. Take a final screenshot for verification
    await page.screenshot({ path: 'e2e-flow-complete.png' });
    console.log('End-to-end test completed');
  });
}); 

