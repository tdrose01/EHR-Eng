// @ts-check
const { test, expect } = require('@playwright/test');

test('basic navigation test', async ({ page }) => {
  // Navigate to the application
  await page.goto('http://localhost:8081/');
  
  // Take a screenshot
  await page.screenshot({ path: 'homepage.png' });
  
  // Check if we need to login
  if (await page.locator('input[type="text"][placeholder="Username"]').isVisible()) {
    console.log('Login form detected, logging in');
    await page.fill('input[type="text"][placeholder="Username"]', 'admin');
    await page.fill('input[type="password"][placeholder="Password"]', 'admin');
    await page.click('button:has-text("Sign In")');
    await page.waitForTimeout(2000);
    
    // Take another screenshot after login
    await page.screenshot({ path: 'post-login.png' });
  }
  
  // Find and click the Patients link
  await page.click('a:has-text("Patients")');
  await page.waitForTimeout(2000);
  
  // Take a screenshot of the patients page
  await page.screenshot({ path: 'patients-page.png' });
  
  // Check if the page has patient data
  const patientRows = page.locator('tbody tr');
  const count = await patientRows.count();
  console.log(`Found ${count} patients in the table`);
  
  // Simple assertion 
  expect(count).toBeGreaterThan(0);
}); 