const { chromium } = require('playwright');

(async () => {
  try {
    console.log('Starting test...');
    const browser = await chromium.launch({ headless: false });
    const page = await browser.newPage();
    
    // Capture patients page
    await page.goto('http://localhost:8081/patients');
    console.log('Navigated to patients page');
    await page.waitForTimeout(5000);
    const patientRows = page.locator('tbody tr');
    const patientCount = await patientRows.count();
    console.log(`Found ${patientCount} patients in the table`);
    
    // Select the first patient if there are any
    if (patientCount > 0) {
      console.log('Selecting first patient');
      await page.locator('tbody tr:first-child input[type="checkbox"]').check();
      console.log('Patient selected');
      await page.screenshot({ path: 'patients-page-with-selection.png' });
    } else {
      await page.screenshot({ path: 'patients-page.png' });
    }
    
    // Capture records page
    await page.goto('http://localhost:8081/records');
    console.log('Navigated to records page');
    await page.waitForTimeout(5000);
    
    const recordsTable = page.locator('table');
    if (await recordsTable.isVisible()) {
      console.log('Records table is visible');
      const recordCount = await page.locator('table tbody tr').count();
      console.log(`Found ${recordCount} records in the table`);
    } else {
      console.log('Records table not found');
    }
    
    await page.screenshot({ path: 'records-page.png' });
    console.log('Test complete. Screenshots saved.');
    
    await browser.close();
  } catch (error) {
    console.error('Test error:', error);
  }
})(); 