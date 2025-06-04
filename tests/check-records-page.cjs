const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// Configuration
const BASE_URL = 'http://localhost:8081';
const RECORDS_URL = `${BASE_URL}/#/records`; 