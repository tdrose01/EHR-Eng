# Repository Guidelines

This repository contains a multi-component EHR system. To work with the project locally follow these steps:

## Environment configuration
Create a `.env` file in the project root defining the following variables used by the scripts:

```
DB_NAME=<database name>
DB_USER=<database user>
DB_PASSWORD=<user password>
DB_HOST=<database host>
DB_PORT=<database port>
```

Optionally set `ENV_PATH` before running scripts to point to a custom env file. The default is `.env` in the project root.

## Database setup
1. Initialize database tables:
   ```bash
   python setup_db_tables.py
   ```
2. Create a test user:
   ```bash
   python create_test_user.py
   ```
   The script creates a user with username `ehrtest` and password `testpassword123` by default.

## Running the application
Start each component individually using:

```bash
python login_api.py          # authentication API on port 8001
python patient_api.py        # patient API on port 8002
python appointments_api.py   # appointments API on port 8003
python -m http.server 8080   # static file server
```

Alternatively, run all services at once:

```bash
python start_servers.py
```

After the servers start, visit `http://localhost:8080/login.html` and log in using the credentials from `create_test_user.py`.

## Pull request requirements
All pull requests must keep the working tree clean. Reference these guidelines in your PR description so contributors know how to set up and run the application.
