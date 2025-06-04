// @ts-check
const { test, expect } = require('@playwright/test');

test('minimal test example', async ({ page }) => {
  // Go to application homepage
  await page.goto('http://localhost:8081/');
  
  // Check that the page loaded
  await expect(page).toHaveTitle(/EHR/);
  
  // Take a screenshot
  await page.screenshot({ path: 'minimal-test-screenshot.png' });
}); 