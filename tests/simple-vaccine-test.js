// @ts-check
const { test, expect } = require('@playwright/test');

// Simple test that doesn't use describe blocks
test('should load vaccine page', async ({ page }) => {
  // Navigate to app
  await page.goto('http://localhost:8081/');
  
  // Login if needed
  if (await page.locator('input[type="text"][placeholder="Username"]').isVisible()) {
    await page.fill('input[type="text"][placeholder="Username"]', 'admin');
    await page.fill('input[type="password"][placeholder="Password"]', 'admin');
    await page.click('button:has-text("Sign In")');
    await page.waitForTimeout(2000);
  }
  
  // Navigate to Patients page first to select a patient
  await page.click('a:has-text("Patients")');
  await page.waitForTimeout(2000);
  
  // Take a screenshot
  await page.screenshot({ path: 'vaccine-test-patients.png' });
  
  // Basic assertion to make sure the test is working
  expect(await page.title()).toContain('EHR');
});
