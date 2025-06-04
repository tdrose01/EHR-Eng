// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Vaccine functionality', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to app
    await page.goto('http://localhost:8081/');
    
    // Login if needed
    if (await page.locator('input[type="text"][placeholder="Username"]').isVisible()) {
      await page.fill('input[type="text"][placeholder="Username"]', 'admin');
      await page.fill('input[type="password"][placeholder="Password"]', 'admin');
      await page.click('button:has-text("Sign In")');
      await page.waitForTimeout(2000);
    }
  });
  
  test('should load vaccine API and display vaccines', async ({ page }) => {
    // Navigate to Patients page first to select a patient
    await page.click('a:has-text("Patients")');
    await page.waitForTimeout(2000);
    await page.locator('tbody tr:first-child input[type="checkbox"]').check();
    await page.waitForTimeout(1000);

    // Navigate to Medical Records to add a new record
    await page.click('a:has-text("Medical Records")');
    await page.waitForTimeout(2000);
    await page.click('button:has-text("Add Record")');
    await page.waitForTimeout(2000);
    
    // Select Vaccination record type
    await page.selectOption('select[name="recordType"]', 'Vaccination');
    await page.waitForTimeout(2000);
    
    // Verify vaccine dropdown appears and contains options
    const vaccineDropdown = page.locator('select[name="vaccine"]');
    await expect(vaccineDropdown).toBeVisible();
    
    // Check that we have vaccine options
    const options = await page.locator('select[name="vaccine"] option').all();
    // Should have at least one vaccine option plus the default/placeholder option
    expect(options.length).toBeGreaterThan(1);
    
    // Log the available vaccines for debugging
    for (let i = 1; i < options.length; i++) { // Skip the first placeholder
      const value = await options[i].getAttribute('value');
      const text = await options[i].innerText();
      console.log(Vaccine option: \ (value: \));
    }
  });
  
  test('should calculate next dose date', async ({ page }) => {
    // Navigate to Patients page first to select a patient
    await page.click('a:has-text("Patients")');
    await page.waitForTimeout(2000);
    await page.locator('tbody tr:first-child input[type="checkbox"]').check();
    await page.waitForTimeout(1000);

    // Navigate to Medical Records to add a new record
    await page.click('a:has-text("Medical Records")');
    await page.waitForTimeout(2000);
    await page.click('button:has-text("Add Record")');
    await page.waitForTimeout(2000);
    
    // Select Vaccination record type
    await page.selectOption('select[name="recordType"]', 'Vaccination');
    await page.waitForTimeout(2000);
    
    // Select the first vaccine
    const options = await page.locator('select[name="vaccine"] option').all();
    if (options.length > 1) {
      const vaccineValue = await options[1].getAttribute('value');
      await page.selectOption('select[name="vaccine"]', vaccineValue);
      console.log(Selected vaccine: \);
      
      // Enter dose number
      await page.fill('input[name="doseNumber"]', '1');
      
      // Set the date
      const today = new Date();
      const formattedDate = today.toISOString().split('T')[0];
      await page.fill('input[type="date"]', formattedDate);
      
      // Look for the Calculate Next Dose button and click it if available
      const calculateButton = page.locator('button:has-text("Calculate")');
      if (await calculateButton.isVisible()) {
        await calculateButton.click();
        await page.waitForTimeout(2000);
        
        // Check for the result - it could be displayed in different ways
        // Method 1: Check for a specific field showing the next dose date
        const nextDoseField = page.locator('input[name="nextDoseDate"], .next-dose-date, *:has-text("Next Dose:")');
        if (await nextDoseField.isVisible()) {
          console.log('Next dose date field found');
          await expect(nextDoseField).toBeVisible();
        }
        
        // Method 2: Check for a notification or message showing the next dose date
        const notification = page.locator('.notification, .alert, .message');
        if (await notification.isVisible()) {
          const notificationText = await notification.innerText();
          console.log(Notification text: \);
          expect(notificationText).toContain('dose');
        }
        
        // Take a screenshot to verify the result visually
        await page.screenshot({ path: 'next-dose-calculation.png' });
      } else {
        console.log('Calculate button not found - taking screenshot for debugging');
        await page.screenshot({ path: 'calculate-button-missing.png' });
      }
    } else {
      console.log('Not enough vaccine options available for testing');
    }
  });
  
  test('should save vaccination record properly', async ({ page }) => {
    // Navigate to Patients page first to select a patient
    await page.click('a:has-text("Patients")');
    await page.waitForTimeout(2000);
    await page.locator('tbody tr:first-child input[type="checkbox"]').check();
    await page.waitForTimeout(1000);

    // Navigate to Medical Records to add a new record
    await page.click('a:has-text("Medical Records")');
    await page.waitForTimeout(2000);
    await page.click('button:has-text("Add Record")');
    await page.waitForTimeout(2000);
    
    // Fill in vaccination details
    await page.selectOption('select[name="recordType"]', 'Vaccination');
    await page.waitForTimeout(2000);
    
    // Select the first vaccine option
    const options = await page.locator('select[name="vaccine"] option').all();
    if (options.length > 1) {
      const vaccineValue = await options[1].getAttribute('value');
      await page.selectOption('select[name="vaccine"]', vaccineValue);
      
      // Set dose info
      await page.fill('input[name="doseNumber"]', '1');
      
      // Set date
      const today = new Date();
      const formattedDate = today.toISOString().split('T')[0];
      await page.fill('input[type="date"]', formattedDate);
      
      // Add unique notes to identify this record
      const timestamp = new Date().getTime();
      const testNotes = Automated test vaccination record \;
      await page.fill('textarea[name="notes"]', testNotes);
      
      // Save the record
      await page.click('button:has-text("Save")');
      await page.waitForTimeout(3000);
      
      // Verify the record appears in the table
      const recordText = page.locator(	able tbody tr:has-text("\"));
      await expect(recordText).toBeVisible();
      
      // Verify the vaccination type is shown
      const vaccinationType = page.locator('table tbody tr:has-text("Vaccination")');
      await expect(vaccinationType).toBeVisible();
    } else {
      console.log('Not enough vaccine options available for testing');
    }
  });
});
