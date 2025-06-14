# Military Electronic Health Record (EHR) System

This repository contains a small Electronic Health Record system used in the Codex examples. It includes several Flask APIs, a static HTML frontend and scripts for setting up a PostgreSQL database.

## Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [API Reference](#api-reference)
- [Environment Variables](#environment-variables)
- [Setup](#setup)
- [Running the Application](#running-the-application)
- [Frontend Overview](#frontend-overview)
- [License](#license)

## Features
- **User Authentication** – secure login API
- **Patient Management** – CRUD endpoints for patient records
- **Appointments Management** – schedule and manage appointments
- **Dashboard Stats** – simple statistics for the dashboard page

## Architecture
The system is split into multiple services:
1. **Login API** (`login_api.py`) – runs on port **8001**
2. **Patient API** (`patient_api.py`) – runs on port **8002**
3. **Appointments API** (`appointments_api.py`) – runs on port **8003**
4. **Static HTML server** – serves the contents of this repository on port **8080**

Each service reads database settings from a `.env` file.

## API Reference
### Authentication
| Method | Route | Description |
|-------|-------|-------------|
| `POST` | `/api/login` | Validate username and password. Expects JSON `{"username": "...", "password": "..."}` and returns `{ success, token, user }` on success. |
| `POST` | `/api/change-password` | Update a user's password. JSON body must contain `username`, `old_password` and `new_password`. Returns `{ success, message }`. |

### Patients
| Method | Route | Description |
|-------|-------|-------------|
| `GET` | `/api/patients` | List patients. Accepts `search`, `limit` and `offset` query parameters. Returns `{ success, total, limit, offset, patients }`. |
| `GET` | `/api/patients/<patient_id>` | Retrieve a single patient record. Returns `{ success, patient }`. |
| `POST` | `/api/patients` | Create a new patient. Body should contain patient fields such as `first_name`, `last_name`, etc. Returns `{ success, patient_id }` when created. |
| `PUT` | `/api/patients/<patient_id>` | Update an existing patient with the provided JSON fields. Returns `{ success, patient_id }`. |
| `GET` | `/api/dashboard-stats` | Basic statistics for the dashboard. Returns `{ success, stats }`. |

### Appointments
| Method | Route | Description |
|-------|-------|-------------|
| `GET` | `/api/appointments` | List appointments with optional `limit` and `offset` query parameters. Returns `{ success, appointments }`. |
| `GET` | `/api/appointments/<appointment_id>` | Retrieve one appointment. Returns `{ success, appointment }`. |
| `POST` | `/api/appointments` | Create an appointment with fields `patient_id`, `provider_id`, `appointment_time`, `reason` and optional `status`. Returns `{ success, appointment_id }`. |
| `PUT` | `/api/appointments/<appointment_id>` | Update an appointment. Body may contain any of the appointment fields. Returns `{ success, message }`. |
| `DELETE` | `/api/appointments/<appointment_id>` | Delete an appointment. Returns `{ success, message }`. |

## Environment Variables
Create a `.env` file in the project root containing your PostgreSQL connection settings:
```
DB_NAME=<database name>
DB_USER=<database user>
DB_PASSWORD=<user password>
DB_HOST=<database host>
DB_PORT=<database port>
```
All scripts use this file by default. You can override the location by setting the `ENV_PATH` environment variable before running any script.

## Setup
1. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Initialize the database** (requires PostgreSQL)
   ```bash
   python setup_db_tables.py
   python create_test_user.py
   ```
   The test user created by `create_test_user.py` has username `ehrtest` and password `testpassword123`.

## Running the Application
You may run the servers individually:
```bash
python login_api.py          # port 8001
python patient_api.py        # port 8002
python appointments_api.py   # port 8003
python -m http.server 8080   # serves HTML files
```
Or launch them all at once:
```bash
python start_servers.py
```
After all services start, open `http://localhost:8080/login.html` and log in with the test credentials.

## Frontend Overview
The HTML files in this repository (`login.html`, `dashboard.html`, `add_patient.html`, etc.) call the Flask APIs on ports 8001–8003. Login requests hit the Login API, while patient and appointment pages fetch data from the respective APIs. Static files are served by a simple Python HTTP server.

## License
This project is licensed under the MIT License. See `LICENSE` for details.

