# Military Electronic Health Record (EHR) System

A web-based Electronic Health Record system designed for military healthcare providers. This application allows healthcare providers to manage patient records, appointments, and medical data with a user-friendly interface.

## Features

- **User Authentication**: Secure login system for healthcare providers
- **Patient Management**: Add, view, edit, and manage patient records
- **Dashboard**: Overview of key statistics (total patients, active patients, today's appointments, pending records)
- **Detail Views**: Specialized pages for patients, appointments, and medical records
- **Responsive Design**: Dark-themed UI optimized for healthcare environments

## System Architecture

The application consists of three main components:

1. **Frontend**: HTML/CSS/JavaScript web interface
2. **Authentication API**: Handles user login and session management (Port 8000)
3. **Patient API**: Provides patient data and medical record functionality (Port 8002)
4. **HTTP Server**: Serves static files for the frontend (Port 8080)

## Database Schema

The system uses PostgreSQL with the following key tables:
- `users`: Healthcare providers with login credentials
- `patients`: Patient demographic and medical information
- `login_history`: Record of user login events
- `ranks`: Military rank reference data
- `services`: Military service branch reference data
- `fmpcs`: Family Member Prefix Code reference data

## Setup Instructions

### Prerequisites

- Python 3.8+ 
- PostgreSQL 12+
- Required Python packages: flask, psycopg2, python-dotenv, passlib, flask-cors

### Database Setup

1. Create a PostgreSQL database named `ehr_db`
2. Run the database setup script: `python setup_db_tables.py`
3. Create a test user: `python create_test_user.py`

### Environment Configuration

Create a `.env` file in the project root with the following variables:
```
DB_NAME=ehr_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### Starting the Servers

1. Start the HTTP server: `python -m http.server 8080`
2. Start the Authentication API: `python auth_api.py`
3. Start the Patient API: `python patient_api.py`

## Usage

1. Access the application at `http://localhost:8080/login.html`
2. Login with provided credentials
3. Navigate through the dashboard to access patients, appointments, and records

## Testing

Test users:
- Admin: `admin` / `adminpass123`
- Test user: `ehrtest` / `testpassword`

## Contributors

This EHR system was developed as a project for military healthcare management.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 