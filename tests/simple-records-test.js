const { chromium } = require('playwright');

async function runSimpleTest() {
  console.log('Starting simple Records test...');
  
  const browser = await chromium.launch({ headless: false, slowMo: 100 });
  const context = await browser.newContext();
  const page = await context.newPage();
  
  try {
    // Navigate to the application
    console.log('Navigating to the application...');
    await page.goto('http://localhost:8081');
    await page.waitForLoadState('networkidle');
    
    console.log('Checking navigation to records page...');
    // Look for Records in the navigation
    const recordsNavLink = page.locator('text=Records');
    if (await recordsNavLink.isVisible()) {
      console.log('✅ Found Records link in navigation');
      await recordsNavLink.click();
      console.log('Clicked on Records link');
      await page.waitForTimeout(2000);
    } else {
      // Try to navigate directly
      console.log('Records link not found in navigation, trying direct navigation');
      await page.goto('http://localhost:8081/#/records');
    }
    
    await page.waitForLoadState('networkidle');
    
    // Check if we're on the Records page
    const recordsHeading = page.locator('h3:has-text("Medical Records")');
    if (await recordsHeading.isVisible()) {
      console.log('✅ Successfully navigated to Records page');
    } else {
      console.log('❌ Could not find Medical Records heading');
      await page.screenshot({ path: 'records-page-fail.png' });
    }
    
    // Check if records are being displayed
    const recordsTable = page.locator('table');
    if (await recordsTable.isVisible()) {
      console.log('✅ Records table is visible');
      const rowCount = await page.locator('table tbody tr').count();
      console.log(`Found ${rowCount} records in the table`);
    } else {
      console.log('❌ Records table not found');
    }
    
    // Look for the filter section
    const filterSection = page.locator('.filter-section');
    if (await filterSection.isVisible()) {
      console.log('✅ Filter section is present');
    } else {
      console.log('❌ Filter section not found');
    }
    
    // Take a screenshot
    await page.screenshot({ path: 'records-test-result.png' });
    console.log('Screenshot saved to records-test-result.png');
    
    // Pause to manually check the page
    console.log('Waiting for 10 seconds to manually check the page...');
    await page.waitForTimeout(10000);
    
    console.log('Simple records test completed');
  } catch (error) {
    console.error('❌ Test failed with error:', error);
    await page.screenshot({ path: 'records-test-error.png' });
  } finally {
    await browser.close();
  }
}

runSimpleTest(); 