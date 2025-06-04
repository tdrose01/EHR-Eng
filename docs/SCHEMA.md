# Database Schema Documentation

## Overview

The EHR system uses a PostgreSQL database with the following tables:

1. **patients** - Patient information
2. **records** - Medical records
3. **users** - System users
4. **login_history** - Authentication tracking
5. **vaccines** - Vaccine information

## Tables

### patients

Contains basic patient information.

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | SERIAL | Unique identifier | PRIMARY KEY |
| first_name | VARCHAR(100) | Patient's first name | NOT NULL |
| last_name | VARCHAR(100) | Patient's last name | NOT NULL |
| dob | DATE | Date of birth | NOT NULL |
| gender | VARCHAR(10) | Patient's gender | NOT NULL |
| address | VARCHAR(200) | Street address | |
| city | VARCHAR(100) | City | |
| state | VARCHAR(50) | State or province | |
| postal_code | VARCHAR(20) | ZIP or postal code | |
| phone | VARCHAR(20) | Contact phone number | |
| email | VARCHAR(100) | Email address | |
| insurance_provider | VARCHAR(100) | Insurance company | |
| insurance_id | VARCHAR(50) | Insurance policy number | |
| created_at | TIMESTAMP | Record creation time | DEFAULT NOW() |
| updated_at | TIMESTAMP | Record update time | DEFAULT NOW() |

### records

Contains medical records for patients. 

**Note**: This table uses camelCase column naming convention.

| Column     | Type    | Description                                  | Constraints          |
|------------|---------|----------------------------------------------|---------------------|
| id         | UUID    | Unique identifier for the record             | PK                  |
| patientId  | UUID    | ID of the patient this record belongs to     | FK patients(id)     |
| type       | VARCHAR | Type of record (e.g., Annual Physical)       | NOT NULL            |
| date       | DATE    | Date when the record was created             | NOT NULL            |
| provider   | VARCHAR | Healthcare provider who created the record   | NOT NULL            |
| status     | VARCHAR | Status of the record (e.g., Draft, Complete) | NOT NULL            |
| notes      | TEXT    | Additional notes or observations             |                     |
| created_at | TIMESTAMP | When the record was created in the system  | DEFAULT NOW()       |
| updated_at | TIMESTAMP | When the record was last updated           | DEFAULT NOW()       |
| vaccineId  | UUID    | ID of associated vaccine data (if type is 'Vaccination') | FK vaccines(id) |

**Important**: When querying the records table with SQL, camelCase column names must be quoted:

```sql
SELECT r.id, r."patientId", r.type FROM records r WHERE r."patientId" = 1;
```

### users

Contains system user information.

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | SERIAL | Unique identifier | PRIMARY KEY |
| username | VARCHAR(50) | Login username | UNIQUE, NOT NULL |
| password_hash | VARCHAR(255) | Hashed password | NOT NULL |
| first_name | VARCHAR(100) | User's first name | NOT NULL |
| last_name | VARCHAR(100) | User's last name | NOT NULL |
| email | VARCHAR(100) | Email address | UNIQUE, NOT NULL |
| role | VARCHAR(20) | User role (admin, doctor, nurse) | NOT NULL |
| active | BOOLEAN | Account status | DEFAULT TRUE |
| created_at | TIMESTAMP | Account creation time | DEFAULT NOW() |
| updated_at | TIMESTAMP | Account update time | DEFAULT NOW() |

### login_history

Tracks user authentication attempts.

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | SERIAL | Unique identifier | PRIMARY KEY |
| user_id | INTEGER | Reference to users table | FOREIGN KEY |
| login_time | TIMESTAMP | Time of login attempt | DEFAULT NOW() |
| ip_address | VARCHAR(45) | IP address of client | |
| user_agent | VARCHAR(255) | Browser user agent | |
| success | BOOLEAN | Whether login succeeded | |

### vaccines

| Column       | Type      | Description                                | Constraints        |
|--------------|-----------|--------------------------------------------|--------------------|
| id           | UUID      | Unique identifier for the vaccine record   | PK                 |
| recordId     | UUID      | ID of the medical record                   | FK records(id)     |
| vaccineName  | VARCHAR   | Name of the vaccine                        | NOT NULL           |
| brandName    | VARCHAR   | Brand name of the vaccine                  |                    |
| manufacturer | VARCHAR   | Manufacturer of the vaccine                |                    |
| cvxCode      | VARCHAR   | CDC CVX code for the vaccine               |                    |
| ndcCode      | VARCHAR   | National Drug Code                         |                    |
| lotNumber    | VARCHAR   | Lot number of the vaccine                  |                    |
| doseAmount   | VARCHAR   | Amount administered (e.g., 0.5 mL)         |                    |
| route        | VARCHAR   | Administration route (e.g., IM, SC)        |                    |
| site         | VARCHAR   | Injection site (e.g., right arm)           |                    |
| doseNumber   | INTEGER   | Dose number in the series (e.g., 1, 2, 3)  |                    |
| totalDoses   | INTEGER   | Total doses needed in the series           |                    |
| nextDoseDate | DATE      | When the next dose is due                  |                    |
| contraindications | TEXT  | Known contraindications                   |                    |
| storageRequirements | TEXT | Storage requirements for the vaccine     |                    |
| additionalNotes | TEXT   | Additional notes about the vaccine         |                    |
| created_at   | TIMESTAMP | When the vaccine record was created        | DEFAULT NOW()      |
| updated_at   | TIMESTAMP | When the vaccine record was last updated   | DEFAULT NOW()      |

## Relationships

```
users --< login_history
patients --< records
```

## Naming Conventions

- The tables `patients`, `users`, and `login_history` use snake_case naming.
- The `records` table uses camelCase naming for the `patientId` column.
- Primary keys are named `id` across all tables.
- Foreign keys are named `[table_name]_id` or `[tableName]Id` depending on the table convention.
- Boolean columns use positive naming (e.g., `active` not `inactive`).

## SQL Examples

### Retrieving Patient Records

```sql
SELECT 
    p.id AS patient_id,
    p.first_name,
    p.last_name,
    r.id AS record_id,
    r.type,
    r.provider,
    r.date,
    r.status,
    r.details
FROM 
    patients p
JOIN 
    records r ON p.id = r."patientId"
WHERE 
    p.id = 1;
```

### Inserting a New Record

```sql
INSERT INTO records ("patientId", type, provider, date, status, details)
VALUES (1, 'Lab Test', 'Dr. Smith', '2023-06-15', 'Completed', 'Normal results');
```

### Updating a Record

```sql
UPDATE records
SET 
    "patientId" = 1,
    type = 'Prescription',
    provider = 'Dr. Jones',
    date = '2023-06-16',
    status = 'Active',
    details = 'Take twice daily with food'
WHERE 
    id = 1;
```

## Important Notes

1. Always use quotes around camelCase column names in SQL queries.
2. The records table structure was designed to match the frontend's data model, which uses camelCase properties.
3. Foreign key constraints ensure data integrity between patients and their records.
4. No timestamps are included in the records table by design.
5. The schema supports full CRUD operations for all entities. 