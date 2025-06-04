# EHR System (Military Electronic Health Record)

A comprehensive Electronic Health Record (EHR) system designed for military healthcare operations, built with Vue.js, Flask, and PostgreSQL.

## Project Overview

This EHR system provides a modern web interface for healthcare professionals to manage patient records, including:

- Patient registration and management
- Medical record creation and updates
- Dashboard with key statistics
- User authentication and authorization

The system is built with a Vue.js frontend and Flask-based APIs, with PostgreSQL database for data storage.

## System Requirements

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Modern web browser (Chrome, Firefox, Edge)

## Setup Instructions

### 1. Database Setup

1. Install PostgreSQL and create a database:

```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo su - postgres
createdb ehr_db
```

2. Configure the database connection in `backend/.env`:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ehr_db
DB_USER=postgres
DB_PASSWORD=your_password
```

3. Initialize the database schema and sample data:

```bash
cd backend
python scripts/setup_postgres_db.py
```

### 2. Backend Setup

1. Create a Python virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install backend dependencies:

```bash
pip install -r requirements.txt
```

3. Start the backend servers:

```bash
cd backend
python scripts/run_server.py
```

This will start the following services:
- Login API on port 8001
- Patient API on port 8002
- Records API on port 8003

### 3. Frontend Setup

1. Install frontend dependencies:

```bash
cd ehr-vue-app
npm install
```

2. Configure the API URLs in `ehr-vue-app/.env`:

```
VITE_API_BASE_URL=http://localhost:8002
VITE_PATIENT_API_URL=http://localhost:8002
VITE_AUTH_API_URL=http://localhost:8001
VITE_RECORDS_API_URL=http://localhost:8003
```

3. Start the development server:

```bash
npm run dev
```

The application will be available at:
- http://localhost:8081

## Default Users

The system is pre-configured with the following test users:

| Username | Password   | Role  |
|----------|------------|-------|
| admin    | adminpass123 | Admin |
| testuser | password   | User  |

## Testing

### API Tests

Run the API tests to verify backend functionality:

```bash
cd backend
python scripts/test_api.py
```

### Frontend Tests

Run the frontend tests to verify UI functionality:

```bash
cd ehr-vue-app
npm run test
```

### Browser Automation Tests

Run end-to-end browser automation tests to verify the complete application flow:

1. Install Playwright dependencies:

```bash
cd ehr-vue-app
npm install
npx playwright install chromium
```

2. Run the browser tests:

```bash
npm run test:browser
```

For detailed information about browser testing, see [Browser Test Guide](docs/BROWSER_TEST_GUIDE.md).

### Connection Tests

Test the connectivity between frontend and backend:

```bash
cd ehr-vue-app
node scripts/test_connection.js
```

## Production Deployment

For production deployment, follow these additional steps:

1. Build the frontend:

```bash
cd ehr-vue-app
npm run build
```

2. Configure a production web server (Nginx, Apache) to serve the built files.

3. Set up Gunicorn or uWSGI to serve the Flask APIs:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8002 api.patient_api:app
```

4. Set up proper SSL certificates for secure connections.

## Documentation

Additional documentation:

- [Regression Test Report](docs/REGRESSION_TEST_REPORT.md) - Detailed analysis of system fixes
- [API Documentation](docs/API.md) - API endpoints and usage
- [Database Schema](docs/SCHEMA.md) - Database design and structure
- [Browser Test Guide](docs/BROWSER_TEST_GUIDE.md) - Guide for running browser automation tests

## Recent Updates

### Medical Records Feature
- Fixed database column naming in records table (camelCase vs snake_case)
- Implemented the records API endpoints at port 8003
- Fixed frontend integration with the records API
- Added support for CRUD operations on medical records
- Improved form handling and validation for record creation and editing

### UI Improvements
- Fixed dropdown styling in medical records screens
- Improved navigation between patient and record views
- Fixed routing issues with record editing

## Troubleshooting

### Common Issues

1. **Database connection errors**:
   - Ensure PostgreSQL is running on the configured port
   - Verify database credentials in `.env` file
   - Check that the database has been initialized with the setup script

2. **API unavailable errors**:
   - Check that the API servers are running using `python scripts/run_server.py`
   - Verify the API URLs in the frontend `.env` file match the running server ports
   - Ensure there are no firewall rules blocking the API ports

3. **Frontend build errors**:
   - Clear the npm cache: `npm cache clean --force`
   - Delete node_modules directory and reinstall: `rm -rf node_modules && npm install`

4. **Port conflicts**:
   - If services can't start because of port conflicts, check for existing processes
   - Use `lsof -i :PORT` (Linux/Mac) or `netstat -ano | findstr PORT` (Windows)
   - Kill conflicting processes before restarting servers

## Support

For technical support or questions, please contact the development team.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For support or inquiries, please contact the development team. 