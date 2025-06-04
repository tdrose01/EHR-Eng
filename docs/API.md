# API Documentation

## Overview

The EHR system consists of three separate API services:

1. **Authentication API** (Port 8001) - Handles user authentication and session management
2. **Patient API** (Port 8002) - Manages patient information and search functionality
3. **Records API** (Port 8003) - Handles medical records CRUD operations

## Authentication API

Base URL: `http://localhost:8001/api`

### Endpoints

| Method | Endpoint | Description | Parameters | Response |
|--------|----------|-------------|------------|----------|
| POST | `/login` | Authenticate user | `username`, `password` | JWT token |
| POST | `/logout` | Log out user | Auth token | Success message |
| GET | `/verify` | Verify token | Auth token | Verification result |
| GET | `/users` | Get all users | Auth token | List of users |
| GET | `/users/:id` | Get user by ID | Auth token, `id` | User details |

## Patient API

Base URL: `http://localhost:8002/api`

### Endpoints

| Method | Endpoint | Description | Parameters | Response |
|--------|----------|-------------|------------|----------|
| GET | `/patients` | Get all patients | Auth token, `page`, `limit`, `search` | List of patients with pagination |
| GET | `/patients/:id` | Get patient by ID | Auth token, `id` | Patient details |
| POST | `/patients` | Create patient | Auth token, Patient data | Created patient |
| PUT | `/patients/:id` | Update patient | Auth token, `id`, Patient data | Updated patient |
| DELETE | `/patients/:id` | Delete patient | Auth token, `id` | Success message |
| GET | `/patients/search` | Search patients | Auth token, `query`, `page`, `limit` | List of matching patients |

## Records API

Base URL: `http://localhost:8003/api`

### Endpoints

| Method | Endpoint | Description | Parameters | Response |
|--------|----------|-------------|------------|----------|
| GET | `/records` | Get all records | Auth token, `page`, `limit`, `type`, `status` | List of records with pagination |
| GET | `/records/:id` | Get record by ID | Auth token, `id` | Record details |
| POST | `/records` | Create record | Auth token, Record data | Created record |
| PUT | `/records/:id` | Update record | Auth token, `id`, Record data | Updated record |
| DELETE | `/records/:id` | Delete record | Auth token, `id` | Success message |
| GET | `/patients/:id/records` | Get records for patient | Auth token, `id` | List of patient's records |

### Records Data Model

The Records API uses a database table with the following structure:

```sql
CREATE TABLE records (
    id SERIAL PRIMARY KEY,
    "patientId" INTEGER NOT NULL,
    type VARCHAR(50) NOT NULL,
    provider VARCHAR(100),
    date DATE,
    status VARCHAR(20),
    details TEXT,
    FOREIGN KEY ("patientId") REFERENCES patients(id)
);
```

**Note**: The records table uses camelCase column naming (`patientId`) rather than snake_case (`patient_id`).

### Request Body Examples

#### Create/Update Record

```json
{
  "patientId": 1,
  "type": "Lab Test",
  "provider": "Dr. Smith",
  "date": "2023-06-15",
  "status": "Completed",
  "details": "Blood work analysis shows normal ranges for all tested items."
}
```

## Error Handling

All APIs follow a consistent error handling pattern:

### Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 409 | Conflict - Resource already exists |
| 500 | Server Error |

### Error Response Format

```json
{
  "error": true,
  "message": "Descriptive error message",
  "code": "ERROR_CODE",
  "details": {}  // Optional additional details
}
```

## Authentication

All protected endpoints require an Authorization header with a JWT token:

```
Authorization: Bearer <token>
```

The token is obtained from the `/api/login` endpoint and should be included in all subsequent requests.

## Environment Configuration

The APIs read their configuration from environment variables:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ehr_db
DB_USER=postgres
DB_PASSWORD=postgres
JWT_SECRET=your_jwt_secret
```

## Development Notes

1. Use the `.env` file to configure the APIs
2. All APIs are accessible through CORS from the frontend origin
3. The Records API specifically requires attention to camelCase column names in the database
4. When accessing records table columns from SQL queries, use double quotes for camelCase columns: `r."patientId"`
5. Ensure all three API services are running for the full application to function 