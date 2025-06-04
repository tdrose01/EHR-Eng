// Simple EHR test 
const { test } = require('@playwright/test'); 
test('Simple EHR test', async ({ page }) =
  console.log('Starting test...'); 
  await page.goto('http://localhost:8081'); 
  await page.screenshot({ path: './test-results/homepage.png' }); 
  const dashboardLink = await page.locator('a[href="/dashboard"], text=Dashboard').first(); 
  if (await dashboardLink.isVisible()) { 
    await dashboardLink.click(); 
    await page.screenshot({ path: './test-results/dashboard.png' }); 
  } 
  console.log('Test completed'); 
}); 
