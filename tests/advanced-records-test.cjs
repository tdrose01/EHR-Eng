const { chromium } = require('playwright');
const fs = require('fs');
// Test configuration'path');
const BASE_URL = 'http://localhost:8081';
const RECORDS_PAGE_URL = `${BASE_URL}/#/records`;

const baseUrl = 'http://localhost:8081'; 