Navigating to Medical Records page...
try {
  console.log("Trying direct navigation to records page...");
  await page.goto('http://localhost:8081/#/records');
  await page.waitForTimeout(2000);
  console.log("Successfully navigated to records page");
} catch (error) {
  console.error("Failed to navigate to records page:", error);
} 