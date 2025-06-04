#!/usr/bin/env python3
"""
Script to set up the database and run migrations for the vaccine scheduling system
"""
import os
import sys
import psycopg2
import subprocess
import time
import glob

def run_sql_file(connection, file_path):
    """Execute a SQL file against the database"""
    print(f"Running migration: {os.path.basename(file_path)}")
    
    try:
        with open(file_path, 'r') as sql_file:
            sql = sql_file.read()
            
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error executing SQL file {file_path}: {e}")
        connection.rollback()
        return False

def create_basic_schema():
    """Create the basic database schema if it doesn't exist"""
    print("Creating basic database schema...")
    
    # Create basic tables for testing
    schema = """
    -- Create patients table
    CREATE TABLE IF NOT EXISTS patients (
        patient_id SERIAL PRIMARY KEY,
        first_name VARCHAR(100) NOT NULL,
        last_name VARCHAR(100) NOT NULL,
        birth_date DATE NOT NULL,
        sex VARCHAR(1) CHECK (sex IN ('M', 'F', 'O')),
        email VARCHAR(255),
        phone VARCHAR(20),
        address TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Create records table
    CREATE TABLE IF NOT EXISTS records (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        "patientId" INTEGER NOT NULL REFERENCES patients(patient_id) ON DELETE CASCADE,
        type VARCHAR(50) NOT NULL,
        provider VARCHAR(255),
        date DATE NOT NULL,
        status VARCHAR(50) DEFAULT 'Draft',
        notes TEXT,
        details JSONB,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Create sample patient
    INSERT INTO patients (first_name, last_name, birth_date, sex)
    VALUES ('John', 'Doe', '1980-01-01', 'M')
    ON CONFLICT DO NOTHING;
    """
    
    try:
        DB_HOST = os.environ.get('DB_HOST', 'localhost')
        DB_PORT = os.environ.get('DB_PORT', '5432')
        DB_NAME = os.environ.get('DB_NAME', 'healthrecords')
        DB_USER = os.environ.get('DB_USER', 'postgres')
        DB_PASSWORD = os.environ.get('DB_PASSWORD', 'postgres')
        
        # Connect to our database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.autocommit = True
        
        # Create the extension for UUID if not exists
        cursor = conn.cursor()
        cursor.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
        
        # Execute the schema script
        cursor.execute(schema)
        cursor.close()
        
        return True
    except Exception as e:
        print(f"Error creating basic schema: {e}")
        return False

def setup_database():
    """Create the database if it doesn't exist and run migrations"""
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '5432')
    DB_NAME = os.environ.get('DB_NAME', 'healthrecords')
    DB_USER = os.environ.get('DB_USER', 'postgres')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'postgres')
    
    # First check if database exists by connecting to postgres
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname="postgres",
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.autocommit = True
        
        # Check if our database exists
        cursor = conn.cursor()
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Creating database '{DB_NAME}'...")
            cursor.execute(f"CREATE DATABASE {DB_NAME}")
            print(f"Database '{DB_NAME}' created successfully")
        else:
            print(f"Database '{DB_NAME}' already exists")
            
        cursor.close()
        conn.close()
        
        # Create basic schema if needed
        if not create_basic_schema():
            return False
        
        # Now connect to our database for migrations
        print(f"Connecting to database '{DB_NAME}'...")
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.autocommit = False
        
        # Run the base vaccines table migration
        print("Setting up vaccines table...")
        vaccines_table_migration = 'migrations/20230821_create_vaccines_table.sql'
        if os.path.exists(vaccines_table_migration):
            success = run_sql_file(conn, vaccines_table_migration)
            if not success:
                print(f"Failed to run vaccines table migration")
                return False
        
        # Add some sample vaccine data
        print("Adding sample vaccine data...")
        sample_vaccine_file = 'sample_data/sample_vaccines.sql'
        if os.path.exists(sample_vaccine_file):
            run_sql_file(conn, sample_vaccine_file)
            # Continue even if sample data fails
        
        # Run the vaccine migrations
        print("Running vaccine scheduling migrations...")
        vaccine_migrations = [
            'migrations/20240410_create_vaccine_schedules.sql',
            'migrations/20240410_create_next_dose_function.sql',
            'migrations/20240410_create_vaccine_utils.sql', 
            'migrations/20240410_add_example_vaccine.sql',
            'migrations/20240410_add_alt_schedule_function.sql',
            'migrations/20240410_update_vaccine_model.sql'
        ]
        
        for migration in vaccine_migrations:
            if os.path.exists(migration):
                success = run_sql_file(conn, migration)
                if not success:
                    print(f"Failed to run vaccine migration {migration}")
                    return False
            else:
                print(f"Warning: Migration file {migration} not found")
        
        conn.commit()
        print("All migrations completed successfully")
        return True
        
    except Exception as e:
        print(f"Database setup error: {e}")
        return False
        
if __name__ == "__main__":
    print("Setting up vaccine scheduling database...")
    success = setup_database()
    
    if success:
        print("\n===== Database Setup Complete =====")
        print("The database has been set up successfully with the vaccine scheduling tables and functions.")
        print("You can now run the tests and start the server.")
    else:
        print("\n===== Database Setup Failed =====")
        print("There were errors during database setup. Please check the logs above.")
        sys.exit(1) 