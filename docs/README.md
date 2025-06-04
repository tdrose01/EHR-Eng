# EHR System Project

This is an Electronic Health Record (EHR) system with a Vue.js frontend and a Python backend.

## Project Structure

The project has been reorganized for better maintainability and separation of concerns:

### Root Directory
- `ehr-vue-app/` - Main Vue.js frontend application
- `backend/` - Server-side Python code
- `server/` - Server configuration
- `docs/` - Project documentation
- `scripts/` - Utility scripts for operations
- `legacy/` - Legacy HTML and other files

### Backend
- `backend/api/` - API endpoints (patient_api.py, records_api.py, login_api.py)
- `backend/database/` - Database scripts and models
- `backend/tests/` - Backend tests
- `backend/scripts/` - Backend utility scripts

### Frontend (ehr-vue-app)
- `ehr-vue-app/src/` - Vue.js source code
- `ehr-vue-app/public/` - Static assets
- `ehr-vue-app/tests/` - Frontend tests
- `ehr-vue-app/docs/` - Frontend documentation

## Getting Started

### Frontend
```bash
cd ehr-vue-app
npm install
npm run dev
```

### Backend
```bash
cd backend
# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r ../requirements.txt
# Run the backend server
python scripts/run_server.py
```

This will start all backend services:
- Login API on port 8001
- Patient API on port 8002
- Records API on port 8003

## API Endpoints

### Patient API (Port 8002)
- `GET /api/patients` - Get all patients
- `GET /api/patients/:id` - Get patient by ID
- `POST /api/patients` - Create a new patient
- `PUT /api/patients/:id` - Update a patient
- `DELETE /api/patients/:id` - Delete a patient
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/health` - Health check endpoint

### Records API (Port 8003)
- `GET /api/records` - Get all medical records
- `GET /api/records/:id` - Get medical record by ID
- `POST /api/records` - Create a new medical record
- `PUT /api/records/:id` - Update a medical record
- `DELETE /api/records/:id` - Delete a medical record
- `GET /api/patients/:id/records` - Get records for a specific patient
- `GET /api/health` - Health check endpoint

### Login API (Port 8001)
- `POST /api/login` - Authenticate user
- `POST /api/logout` - Logout user
- `GET /api/health` - Health check endpoint

## Database Schema

The PostgreSQL database contains the following tables:
- `patients` - Patient information
- `records` - Medical records
- `users` - User accounts
- `login_history` - Authentication logs

## Recent Updates

- Fixed database column naming conventions
- Added support for medical records
- Improved authentication system
- Fixed UI styling issues in dropdown components
- Implemented proper routing for record editing

## Testing
See the testing documentation in `docs/testing.md` for more details.

## Additional Resources
- Project documentation in `docs/`
- API documentation in `ehr-vue-app/docs/` 