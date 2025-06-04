const { test, expect } = require('@playwright/test');

test('Patient selection and records display', async ({ page }) => {
  // Go to the application
  console.log('Starting test - navigating to application');
  await page.goto('http://localhost:8081/');
  
  // Login if needed
  if (await page.locator('input[type="text"][placeholder="Username"]').isVisible()) {
    console.log('Login form detected, attempting to login');
    await page.fill('input[type="text"][placeholder="Username"]', 'admin');
    await page.fill('input[type="password"][placeholder="Password"]', 'admin');
    await page.click('button:has-text("Sign In")');
    await page.waitForTimeout(2000);
  }
  
  // Navigate to Patients page
  console.log('Navigating to Patients page');
  await page.click('a:has-text("Patients")');
  await page.waitForTimeout(2000);
  
  // Verify patients are loaded
  const patientRows = page.locator('tbody tr');
  const count = await patientRows.count();
  console.log(`Found ${count} patients in the table`);
  expect(count).toBeGreaterThan(0);
  
  // Select the first patient
  console.log('Selecting first patient');
  await patientRows.first().locator('input[type="checkbox"]').click();
  await page.waitForTimeout(1000);
  
  // Navigate to Medical Records
  console.log('Navigating to Medical Records page');
  await page.click('a:has-text("Medical Records")');
  await page.waitForTimeout(3000);
  
  // Verify records page loaded with patient data
  const recordsHeading = page.locator('h3:has-text("Medical Records")');
  await expect(recordsHeading).toBeVisible();
  
  // Take a screenshot for verification
  await page.screenshot({ path: 'patient-selection-test.png' });
  console.log('Test completed and screenshot saved');
}); 