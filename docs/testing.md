# Testing Documentation

This document provides an overview of testing procedures for the EHR system.

## Backend Testing

The backend tests are located in the `backend/tests/` directory.

### Running Backend Tests

```bash
cd backend
python -m pytest tests/
```

Key test files:
- `test_db_login.py` - Tests for database login functionality
- `test_ehr_login.py` - Tests for EHR login API
- `test_rbac.py` - Tests for role-based access control

## Frontend Testing

The frontend tests are located in the `ehr-vue-app/tests/` directory.

### Running Frontend Tests

The project uses Playwright for end-to-end testing:

```bash
cd ehr-vue-app
npx playwright test
```

For specific test suites:

```bash
# Run login tests
npx playwright test tests/login-tests/
```

## MCP Server Tests

For tests using the MCP server environment, use:

```bash
cd ehr-vue-app
./run-mcp-tests.bat
```

## Test Screenshots

Test screenshots are stored in:
- `ehr-vue-app/screenshots/`
- `ehr-vue-app/test-screenshots/` 