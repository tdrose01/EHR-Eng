/**
 * Standalone CVX Code Test
 * This is a simple script to test CVX code auto-population without using Playwright or other frameworks.
 * It uses Puppeteer directly which is easier to set up.
 */

// Import in CommonJS style for maximum compatibility
const puppeteer = require('puppeteer');

// Configuration
const config = {
  // Try multiple potential frontend URLs
  urls: [
    'http://localhost:4173', // Vite preview server
    'http://localhost:8081', // Dev server
    'http://localhost:5173',
    'http://localhost:8080'
  ],
  apiUrl: 'http://localhost:8004', // API server URL
  loginPath: '/login',
  credentials: {
    username: 'admin',
    password: 'password'
  },
  vaccine: {
    name: 'DTaP (Diphtheria, Tetanus, and acellular Pertussis)',
    brand: 'Infanrix',
    manufacturer: 'GlaxoSmithKline',
    doseNumber: '1',
    totalDoses: '5'
  },
  expectedCvxCodes: ['20', '106', '107'],
  screenshotBasename: 'cvx-test-screenshot',
  browserOptions: {
    headless: false,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-gpu',
      '--window-size=1280,800'
    ],
    defaultViewport: {
      width: 1280,
      height: 800
    }
  }
};

// Helper function for screenshots
async function takeScreenshot(page, label) {
  try {
    const screenshotPath = `${config.screenshotBasename}-${String(screenshotCounter).padStart(2, '0')}-${label}.png`;
    await page.screenshot({ 
      path: screenshotPath,
      fullPage: true
    });
    console.log(`Took screenshot: ${screenshotPath}`);
    screenshotCounter++;
  } catch (error) {
    console.log(`Warning: Could not take screenshot ${label}: ${error.message}`);
  }
}

// Main test function
async function runTest() {
  console.log('Starting CVX code auto-population test');
  let browser;

  try {
    // Launch browser
    console.log('Launching browser');
    browser = await puppeteer.launch({
      headless: false, // Set to true for headless mode
      args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });

    // Helper function for screenshots
    let screenshotCounter = 0;
    async function takeScreenshot(label) {
      try {
        const screenshotPath = `${config.screenshotBasename}-${String(screenshotCounter).padStart(2, '0')}-${label}.png`;
        await page.screenshot({ path: screenshotPath });
        console.log(`Took screenshot: ${screenshotPath}`);
        screenshotCounter++;
      } catch (error) {
        console.error(`Failed to take screenshot: ${error.message}`);
      }
    }

    // Try to find a working frontend URL
    console.log('Trying to find a working frontend URL');
    let workingUrl = null;
    
    for (const url of config.urls) {
      try {
        console.log(`Trying ${url}...`);
        await page.goto(`${url}`, { 
          waitUntil: 'networkidle2', 
          timeout: 10000  // Increased timeout
        });
        
        // Check if we can access the page content
        const pageContent = await page.content();
        if (pageContent.length > 0) {
          console.log(`Successfully connected to ${url}`);
          console.log(`Page title: ${await page.title()}`);
          workingUrl = url;
          break;
        }
      } catch (error) {
        console.log(`Could not connect to ${url}: ${error.message}`);
      }
    }
    
    if (!workingUrl) {
      throw new Error("Could not find a working frontend URL");
    }

    // Step 1: Navigate to the login page
    console.log('Step 1: Navigating to login page');
    await page.goto(`${workingUrl}${config.loginPath}`, { waitUntil: 'networkidle2', timeout: 30000 });
    await takeScreenshot('login-page');

    // Step 2: Log in
    console.log('Step 2: Logging in');
    await page.type('input[name="username"]', config.credentials.username);
    await page.type('input[name="password"]', config.credentials.password);
    
    // Click login button
    await Promise.all([
      page.click('button[type="submit"]'),
      page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 30000 }).catch(e => {
        console.log('Navigation timeout after login, continuing');
      })
    ]);
    await takeScreenshot('after-login');

    // Step 3: Navigate to patients page
    console.log('Step 3: Navigating to patients page');
    await page.goto(`${workingUrl}/patients`, { waitUntil: 'networkidle2', timeout: 30000 });
    await takeScreenshot('patients-page');

    // Step 4: Select the first patient
    console.log('Step 4: Selecting a patient');
    const patientRows = await page.$$('table tbody tr');
    
    if (patientRows.length > 0) {
      await patientRows[0].click();
      await page.waitForTimeout(1000); // Give time for patient details to load
      await takeScreenshot('patient-selected');
    } else {
      console.error('No patients found, test cannot continue');
      await takeScreenshot('no-patients');
      throw new Error('No patients found in the system');
    }

    // Step 5: Navigate to records
    console.log('Step 5: Navigating to patient records');
    
    // Try clicking the Records tab
    const recordsTabExists = await page.evaluate(() => {
      const links = Array.from(document.querySelectorAll('a'));
      return links.some(link => 
        link.textContent.includes('Records') || 
        link.textContent.includes('Medical Records')
      );
    });
    
    if (recordsTabExists) {
      await page.click('a:has-text("Records"), a:has-text("Medical Records")');
    } else {
      console.log('Could not find Records tab, trying direct navigation');
      await page.goto(`${workingUrl}/records`, { waitUntil: 'networkidle2', timeout: 30000 });
    }
    
    await takeScreenshot('records-page');

    // Step 6: Create a new vaccination record
    console.log('Step 6: Creating new vaccination record');
    
    // Look for Add Record button
    const addRecordButton = await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      return buttons.findIndex(button => 
        button.textContent.includes('Add Record') || 
        button.textContent.includes('New Record')
      );
    });
    
    if (addRecordButton !== -1) {
      await page.evaluate((index) => {
        document.querySelectorAll('button')[index].click();
      }, addRecordButton);
    } else {
      console.error('Could not find Add Record button');
      await takeScreenshot('no-add-record-button');
      throw new Error('Could not find Add Record button');
    }
    
    await page.waitForTimeout(1000);
    await takeScreenshot('new-record-form');

    // Step 7: Set record type to Vaccination
    console.log('Step 7: Setting record type to Vaccination');
    
    // Try to find the record type dropdown
    const recordTypeSelector = await page.evaluate(() => {
      // Look for record type dropdown
      const selects = Array.from(document.querySelectorAll('select'));
      
      for (let i = 0; i < selects.length; i++) {
        const select = selects[i];
        
        // Check if this is the record type selector
        const options = Array.from(select.options);
        if (options.some(option => option.textContent.includes('Vaccination'))) {
          return {
            index: i,
            vaccinationOptionValue: options.find(option => 
              option.textContent.includes('Vaccination')
            ).value
          };
        }
      }
      
      return null;
    });
    
    if (recordTypeSelector) {
      await page.evaluate((selector) => {
        const select = document.querySelectorAll('select')[selector.index];
        select.value = selector.vaccinationOptionValue;
        
        // Trigger change event
        const event = new Event('change', { bubbles: true });
        select.dispatchEvent(event);
      }, recordTypeSelector);
    } else {
      console.error('Could not find record type selector');
      await takeScreenshot('no-record-type-selector');
      throw new Error('Could not find record type selector');
    }
    
    await page.waitForTimeout(1000);
    await takeScreenshot('vaccination-type-selected');

    // Step 8: Fill vaccination details
    console.log('Step 8: Filling vaccination details');
    
    // Find and select vaccine name
    const vaccineSelector = await page.evaluate((vaccineName) => {
      const selects = Array.from(document.querySelectorAll('select'));
      
      for (let i = 0; i < selects.length; i++) {
        const select = selects[i];
        const options = Array.from(select.options);
        
        if (options.some(option => option.textContent.includes('DTaP'))) {
          return {
            index: i,
            vaccineOptionValue: options.find(option => 
              option.textContent.includes(vaccineName)
            )?.value || options.find(option => 
              option.textContent.includes('DTaP')
            ).value
          };
        }
      }
      
      return null;
    }, config.vaccine.name);
    
    if (vaccineSelector) {
      await page.evaluate((selector) => {
        const select = document.querySelectorAll('select')[selector.index];
        select.value = selector.vaccineOptionValue;
        
        // Trigger change event
        const event = new Event('change', { bubbles: true });
        select.dispatchEvent(event);
      }, vaccineSelector);
    } else {
      console.error('Could not find vaccine selector');
      await takeScreenshot('no-vaccine-selector');
      throw new Error('Could not find vaccine selector');
    }
    
    // Wait for CVX code to auto-populate
    await page.waitForTimeout(1000);
    
    // Fill in other fields
    await page.evaluate((vaccineData) => {
      const inputs = document.querySelectorAll('input');
      
      for (let input of inputs) {
        if (input.id === 'brandName' || input.name === 'brandName') {
          input.value = vaccineData.brand;
          input.dispatchEvent(new Event('input', { bubbles: true }));
        }
        
        if (input.id === 'manufacturer' || input.name === 'manufacturer') {
          input.value = vaccineData.manufacturer;
          input.dispatchEvent(new Event('input', { bubbles: true }));
        }
        
        if (input.id === 'doseNumber' || input.name === 'doseNumber') {
          input.value = vaccineData.doseNumber;
          input.dispatchEvent(new Event('input', { bubbles: true }));
        }
        
        if (input.id === 'totalDoses' || input.name === 'totalDoses') {
          input.value = vaccineData.totalDoses;
          input.dispatchEvent(new Event('input', { bubbles: true }));
        }
      }
    }, config.vaccine);
    
    await takeScreenshot('form-filled');

    // Step 9: Verify CVX code auto-population
    console.log('Step 9: Verifying CVX code auto-population');
    
    // Check if CVX code field exists and is populated
    const cvxCodeResult = await page.evaluate((expectedCodes) => {
      const cvxCodeInput = Array.from(document.querySelectorAll('input')).find(input => 
        input.id === 'cvxCode' || input.name === 'cvxCode'
      );
      
      if (!cvxCodeInput) {
        return { found: false, value: null };
      }
      
      return { 
        found: true, 
        value: cvxCodeInput.value,
        isValid: expectedCodes.includes(cvxCodeInput.value)
      };
    }, config.expectedCvxCodes);
    
    if (!cvxCodeResult.found) {
      console.error('CVX code field not found');
      await takeScreenshot('cvx-code-field-not-found');
      throw new Error('CVX code field not found');
    }
    
    if (!cvxCodeResult.isValid) {
      console.error(`CVX code ${cvxCodeResult.value} is not in the expected list: ${config.expectedCvxCodes.join(', ')}`);
      await takeScreenshot('invalid-cvx-code');
      throw new Error(`Invalid CVX code: ${cvxCodeResult.value}`);
    }
    
    console.log(`✅ CVX code auto-population verified: ${cvxCodeResult.value}`);
    await takeScreenshot('cvx-code-verified');

    // Step 10: Submit the form
    console.log('Step 10: Submitting the form');
    
    // Find and click the Save button
    const saveButtonResult = await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      
      // Look for submit button
      const saveButton = buttons.find(button => 
        button.type === 'submit' || 
        button.textContent.includes('Save')
      );
      
      if (!saveButton) {
        return { found: false };
      }
      
      saveButton.click();
      return { found: true };
    });
    
    if (!saveButtonResult.found) {
      console.error('Save button not found');
      await takeScreenshot('save-button-not-found');
      throw new Error('Save button not found');
    }
    
    await page.waitForTimeout(2000);
    await takeScreenshot('form-submitted');

    console.log('✅ Test completed successfully');
    return { success: true, message: 'CVX code auto-population verified' };
    
  } catch (error) {
    console.error(`❌ Test failed: ${error.message}`);
    return { success: false, message: error.message };
  } finally {
    // Close the browser
    if (browser) {
      await browser.close();
    }
  }
}

// Run the test
if (require.main === module) {
  (async () => {
    const result = await runTest();
    
    if (result.success) {
      console.log(`✅ SUCCESS: ${result.message}`);
      process.exit(0);
    } else {
      console.error(`❌ FAILURE: ${result.message}`);
      process.exit(1);
    }
  })();
} 