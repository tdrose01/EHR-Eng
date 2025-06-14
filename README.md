# Military Electronic Health Record (EHR) System

A web-based Electronic Health Record system designed for military healthcare providers. This application allows healthcare providers to manage patient records, appointments, and medical data with a user-friendly interface.

## Features

- **User Authentication**: Secure login system for healthcare providers
- **Patient Management**: Add, view, edit, and manage patient records
- **Appointments Management**: Schedule and review patient appointments
- **Dashboard**: Overview of key statistics (total patients, active patients, today's appointments, pending records)
- **Detail Views**: Specialized pages for patients, appointments, and medical records
- **Responsive Design**: Dark-themed UI optimized for healthcare environments
- **Admin User Management**: Admins can add new users via `/admin/create_user`
- **Secure Password Hashing**: New accounts use bcrypt while legacy SHA-256 hashes are still supported
- **Clinical Notes**: Add clinical notes to a patient record via the `/api/patients/<patient_id>/notes` endpoint

## System Architecture

The application consists of three main components:

1. **Frontend**: HTML/CSS/JavaScript web interface
2. **Authentication API**: Handles user login and session management (Port 8001)
3. **Patient API**: Provides patient data and medical record functionality (Port 8002)
4. **Appointments API**: Manages scheduling and retrieval of appointment data (Port 8003)
5. **HTTP Server**: Serves static files for the frontend (Port 8080)

## Database Schema

The system uses PostgreSQL with the following key tables:
- `users`: Healthcare providers with login credentials
- `patients`: Patient demographic and medical information
- `login_history`: Table storing a history of successful and failed user login attempts
- `ranks`: Military rank reference data
- `services`: Military service branch reference data
- `fmpcs`: Family Member Prefix Code reference data
- `patient_notes`: Stores clinical notes linked to each patient

The login events table is named `login_history`. Older scripts may refer to
`user_logins`, but the correct table name in this project is `login_history`.

## Setup Instructions

### Prerequisites

- Python 3.8+ 
- PostgreSQL 12+
- Required Python packages: flask, psycopg2, python-dotenv, passlib, flask-cors

### Database Setup

1. Create a PostgreSQL database named `ehr_db`
2. Run the database setup script: `python setup_db_tables.py`
3. Create a test user: `python create_test_user.py`

If you created the database before this version, drop the old `user_logins` table and recreate the tables to use `login_history` and the `hashed_password` column:
```bash
psql -d ehr_db -c "DROP TABLE IF EXISTS user_logins";
python setup_db_tables.py
```

### Environment Configuration

Create a `.env` file in the project root containing your database connection
settings:
```
DB_NAME=ehr_db       # PostgreSQL database name
DB_USER=postgres     # Database user
DB_PASSWORD=your_password  # Database user's password
DB_HOST=localhost    # Database host
DB_PORT=5432         # Database port
```

Optionally, set `ENV_PATH` to point to a custom environment file before running
any scripts. If not set, `.env` in the project root is used.

### Starting the Servers

1. Start the HTTP server: `python -m http.server 8080`
2. Start the Authentication API: `python login_api.py` (runs on port 8001)
3. Start the Patient API: `python patient_api.py` (runs on port 8002)
4. Start the Appointments API: `python appointments_api.py` (runs on port 8003)

Alternatively, run `python start_servers.py` to launch the HTTP, authentication, and patient APIs together. The appointments API should be started in a separate terminal.
## Usage

1. Access the application at `http://localhost:8080/login.html`
2. Alternatively, use the Vue-based login at `http://localhost:8080/login_vue.html`
3. Login with provided credentials
4. Navigate through the dashboard to access patients, appointments, and records

### Admin User Creation

Logged-in admins can add new users. Use the **Create User** button on the dashboard or open `http://localhost:8001/admin/create_user` with your session token. Submit a username, email, password and role. Passwords are stored using bcrypt hashing.

## Testing

Test users:
- Admin: `admin` / `adminpass123`
- Test user: `ehrtest` / `testpassword123`

## Contributors

This EHR system was developed as a project for military healthcare management.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 