# EHR System Server Manager

This directory contains the backend API servers for the EHR system and includes a server manager script to handle starting and stopping all services properly.

## Prerequisites

Ensure you have the following installed:
- Python 3.7+
- Node.js 14+ and npm 6+ (for the frontend)
- PostgreSQL 12+

## Installation

1. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Install frontend dependencies:
   ```
   cd ../ehr-vue-app
   npm install
   ```

3. Configure your PostgreSQL connection in `.env` file (create it if it doesn't exist):
   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=ehr_db
   DB_USER=postgres
   DB_PASSWORD=postgres
   ```

## Using the Server Manager

The server manager script handles:
- Killing any existing processes using required ports
- Starting all servers in the correct order
- Monitoring server logs
- Graceful shutdown on Ctrl+C

### Start All EHR Services

```
python start_ehr_servers.py
```

This will:
1. Kill any existing processes using ports 8000, 8004, and 8081
2. Start the main API server on port 8000
3. Start the vaccine API server on port 8004
4. Start the frontend development server on port 8081
5. Display URLs where you can access each service

### Accessing the Application

After starting the servers, you can access:
- Frontend UI: http://localhost:8081
- Main API: http://localhost:8000
- Vaccine API: http://localhost:8004

### Stopping the Services

Press `Ctrl+C` in the terminal where the server manager is running to gracefully shut down all services.

## Individual Server Scripts

If you need to run servers individually (not recommended):

- Main API Server: `python start_server_with_logging.py`
- Vaccine API Server: `python start_vaccine_server.py`
- Frontend Development Server: 
  ```
  cd ../ehr-vue-app
  npm run dev
  ```

## Troubleshooting

Logs are stored in the `logs` directory with timestamps to help diagnose issues.

If you encounter port conflicts, run the server manager with admin/sudo privileges to ensure it can kill processes using the required ports.

If PostgreSQL connection issues occur, verify your database is running and `.env` file has correct credentials.

## Directory Structure

- `api/` - API endpoint implementations
- `migrations/` - Database migration scripts
- `logs/` - Server logs (created when servers are run)
- `start_ehr_servers.py` - Server manager script to run all services
- `start_server_with_logging.py` - Main API server with logging
- `start_vaccine_server.py` - Vaccine API server

# Vaccine Management API

This API provides endpoints for managing vaccine records, schedules, and calculating next dose dates.

## Setup and Installation

### Prerequisites

- Python 3.7+
- PostgreSQL 12+ 

### Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set up environment variables (optional):

```
DB_CONNECTION_STRING=postgresql://username:password@localhost:5432/test_vaccines
PORT=8004
```

## Running the API

There are several ways to run the API server:

### Option 1: Minimal Server (Recommended)

For a simple demonstration focused on the test_vaccines table:

```bash
python minimal_server.py
```

This script will:
1. Create the database if it doesn't exist
2. Create the test_vaccines table
3. Insert sample data
4. Start the API server

### Option 2: Full Setup Script

For a more complete setup with migrations:

```bash
python setup_and_run.py
```

This script will:
1. Create the database if it doesn't exist
2. Run all migrations
3. Start the API server
4. Open a test page to interact with the API

### Option 3: Server with Enhanced Logging

For debugging purposes:

```bash
python start_server_with_logging.py
```

## API Endpoints

### Basic Endpoints
- `GET /api/vaccines/test` - Basic health check that doesn't require DB access
- `GET /api/vaccines/simple` - Get basic vaccine data
- `GET /api/status` - Get server and database status

### Advanced Endpoints (Only in full server)
- `GET /api/vaccines/schedules` - Get vaccine schedules
- `GET /api/vaccines/next-dose/{vaccine_name}/{dose_number}/{age_group}` - Calculate next dose date

## Testing

### HTML Test Page

An HTML test page is available at `vaccine_api_test.html` that allows you to:
- Test the API endpoints
- Check server status
- View responses

### API Test Script

You can run a test script to verify the API is working:

```bash
python test_api.py
```

## Database Schema

The minimal API uses the following table:
- `test_vaccines` - Simple vaccine data for API testing

The full API includes additional tables:
- `records` - Basic patient records
- `vaccines` - Vaccine administration records
- `vaccine_schedules` - Recommended vaccine schedules with intervals

## Troubleshooting

If you encounter issues:

1. Check the database connection parameters
2. Ensure PostgreSQL is running
3. Try the minimal server first to verify basic functionality
4. Use the server with enhanced logging for detailed error information

## PostgreSQL Functions

The API includes the following database functions:
- `calculate_next_dose` - Calculate the next dose date based on vaccine, dose number, and age group
- `get_alt_schedule` - Get alternative schedule based on patient age
- `get_test_vaccines` - Get test vaccines in JSON format 