// Simple browser test
const { chromium } = require('@playwright/test');

(async () => {
  console.log('Starting browser test...');
  try {
    console.log('Launching browser...');
    const browser = await chromium.launch({ 
      headless: false,
      args: ['--start-maximized'],
      executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH || undefined
    });
    console.log('Browser launched successfully');
    
    const context = await browser.newContext({ 
      viewport: { width: 1280, height: 720 } 
    });
    const page = await context.newPage();
    
    console.log('Navigating to localhost...');
    await page.goto('http://localhost:8081', { timeout: 30000 });
    console.log('Page loaded');
    
    await page.screenshot({ path: './browser-test/screenshot.png' });
    console.log('Screenshot taken');
    
    // Try to navigate to dashboard
    console.log('Attempting to navigate to dashboard');
    try {
      const dashboardLink = await page.locator('a[href="/dashboard"], a:has-text("Dashboard")').first();
      if (await dashboardLink.isVisible()) {
        await dashboardLink.click();
        await page.waitForLoadState('networkidle', { timeout: 30000 });
        await page.screenshot({ path: './browser-test/dashboard.png' });
        console.log('Dashboard screenshot taken');
      } else {
        console.log('Dashboard link not found, trying direct navigation');
        await page.goto('http://localhost:8081/dashboard', { timeout: 30000 });
        await page.waitForLoadState('networkidle', { timeout: 30000 });
        await page.screenshot({ path: './browser-test/dashboard-direct.png' });
      }
    } catch (navError) {
      console.error('Error navigating to dashboard:', navError);
    }
    
    // Wait to see the browser
    console.log('Waiting 20 seconds to observe the browser...');
    await new Promise(r => setTimeout(r, 20000)); 
    
    console.log('Test completed successfully');
    await browser.close();
  } catch (error) {
    console.error('Error during browser test:');
    console.error(error);
  }
})();
