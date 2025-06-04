module.exports = { 
  timeout: 30000, 
  use: { headless: false }, 
  projects: [{ name: 'chromium' }], 
  reporter: 'list', 
  outputDir: 'test-results/', 
}; 
