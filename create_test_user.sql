-- SQL Script to create a dedicated test user for EHR automation testing
-- Run this script as a PostgreSQL superuser (e.g., postgres)

-- Create test user if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'ehr_test_user') THEN
        CREATE USER ehr_test_user WITH PASSWORD 'ehr_test_password';
    END IF;
END
$$;

-- Create test database if it doesn't exist
-- Note: If the database already exists with different owner, you may need to adjust this
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ehr_test') THEN
        CREATE DATABASE ehr_test;
    END IF;
END
$$;

-- Connect to the test database to set up permissions
\c ehr_test

-- Grant privileges to the test user
GRANT ALL PRIVILEGES ON DATABASE ehr_test TO ehr_test_user;
ALTER DEFAULT PRIVILEGES GRANT ALL ON TABLES TO ehr_test_user;
ALTER DEFAULT PRIVILEGES GRANT ALL ON SEQUENCES TO ehr_test_user;
ALTER DEFAULT PRIVILEGES GRANT ALL ON FUNCTIONS TO ehr_test_user;

-- If the schema and tables already exist, grant permissions on them
DO $$
DECLARE
    schema_name text;
BEGIN
    FOR schema_name IN SELECT nspname FROM pg_namespace WHERE nspname NOT LIKE 'pg_%' AND nspname != 'information_schema'
    LOOP
        EXECUTE format('GRANT ALL PRIVILEGES ON SCHEMA %I TO ehr_test_user', schema_name);
        EXECUTE format('GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA %I TO ehr_test_user', schema_name);
        EXECUTE format('GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA %I TO ehr_test_user', schema_name);
        EXECUTE format('GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA %I TO ehr_test_user', schema_name);
    END LOOP;
END
$$;

-- Output success message
\echo 'Test user created successfully: ehr_test_user'
\echo 'Test database: ehr_test'
\echo 'Connection string: postgresql://ehr_test_user:ehr_test_password@localhost:5432/ehr_test' 