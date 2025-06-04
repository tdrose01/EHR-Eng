import os
import sys
import psycopg2
from psycopg2 import sql
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('ehr-project/backend/.env')

# Database connection parameters
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'ehr_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

def get_db_connection():
    """Connect to the PostgreSQL database server"""
    conn = None
    try:
        # Connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        print(f"Host: {DB_CONFIG['host']}")
        print(f"Port: {DB_CONFIG['port']}")
        print(f"Database: {DB_CONFIG['database']}")
        print(f"User: {DB_CONFIG['user']}")
        
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        
        # Create a cursor
        cur = conn.cursor()
        
        # Execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')
        
        # Display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)
        
        # Close the cursor
        cur.close()
        
        print("Database connection successful!")
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        if conn is not None:
            conn.close()
        sys.exit(1)

def create_tables(conn):
    """Create necessary tables for the EHR system"""
    commands = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            full_name VARCHAR(100) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'user',
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS user_logins (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            login_time TIMESTAMP NOT NULL,
            ip_address VARCHAR(45) NOT NULL,
            success BOOLEAN NOT NULL,
            user_agent VARCHAR(255)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS user_sessions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            session_token VARCHAR(255) NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT TRUE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS patients (
            patient_id SERIAL PRIMARY KEY,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            date_of_birth DATE NOT NULL,
            gender VARCHAR(20),
            contact_number VARCHAR(20),
            email VARCHAR(100),
            address VARCHAR(255),
            emergency_contact VARCHAR(100),
            emergency_contact_number VARCHAR(20),
            blood_type VARCHAR(10),
            rank VARCHAR(50),
            service VARCHAR(50),
            fmpc VARCHAR(50),
            allergies TEXT,
            medical_conditions TEXT,
            status VARCHAR(20) DEFAULT 'Active',
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS records (
            id SERIAL PRIMARY KEY,
            "patientId" INTEGER REFERENCES patients(patient_id),
            type VARCHAR(50) NOT NULL,
            provider VARCHAR(100),
            date DATE NOT NULL,
            notes TEXT,
            status VARCHAR(20) DEFAULT 'Pending',
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS appointments (
            id SERIAL PRIMARY KEY,
            patient_id INTEGER REFERENCES patients(patient_id),
            provider_id INTEGER,
            appointment_date TIMESTAMP NOT NULL,
            reason TEXT,
            status VARCHAR(20) DEFAULT 'Scheduled',
            notes TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS medications (
            id SERIAL PRIMARY KEY,
            patient_id INTEGER REFERENCES patients(patient_id),
            medication_name VARCHAR(100) NOT NULL,
            dosage VARCHAR(50) NOT NULL,
            frequency VARCHAR(50) NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE,
            prescriber_id INTEGER,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    ]
    
    try:
        cur = conn.cursor()
        # Execute each command
        for command in commands:
            print(f"Executing: {command[:60]}...")
            cur.execute(command)
        
        # Close the cursor
        cur.close()
        
        # Commit the changes
        conn.commit()
        
        print("Tables created successfully!")
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error creating tables: {error}")
        conn.rollback()

def insert_sample_data(conn):
    """Insert sample data into the EHR system"""
    try:
        # First, check if the users table exists and what columns it has
        cur = conn.cursor()
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'public' AND table_name = 'users'
        """)
        
        user_columns = [col[0] for col in cur.fetchall()]
        print(f"Detected user table columns: {user_columns}")
        
        # Create appropriate insert command based on available columns
        if 'username' in user_columns and 'password_hash' in user_columns:
            if 'email' in user_columns and 'full_name' in user_columns:
                # Standard schema with email and full_name
                users_cmd = """
                INSERT INTO users (username, email, full_name, password_hash, role)
                VALUES 
                    ('admin', 'admin@example.com', 'Administrator', 
                     '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'admin'),
                    ('doctor1', 'doctor1@example.com', 'Dr. John Smith', 
                     '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 'doctor'),
                    ('nurse1', 'nurse1@example.com', 'Jane Doe, RN', 
                     '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 'nurse')
                ON CONFLICT (username) DO NOTHING
                """
            else:
                # Simplified schema without email
                users_cmd = """
                INSERT INTO users (username, password_hash, role)
                VALUES 
                    ('admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'admin'),
                    ('doctor1', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 'doctor'),
                    ('nurse1', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 'nurse')
                ON CONFLICT (username) DO NOTHING
                """
            
            print(f"Executing users insert command: {users_cmd[:60]}...")
            cur.execute(users_cmd)
            print("Successfully inserted user data")
        else:
            print("Users table does not have expected columns, skipping user data insertion")
            
        # Continue with other inserts that we know are working
        commands = [
            """
            INSERT INTO patients (first_name, last_name, date_of_birth, gender, 
                                contact_number, email, address, blood_type, rank, service, status)
            VALUES 
                ('John', 'Doe', '1975-05-15', 'Male', 
                 '555-123-4567', 'john.doe@example.com', '123 Main St, Anytown, ST 12345',
                 'O+', 'E-4', 'Army', 'Active'),
                ('Jane', 'Smith', '1980-08-20', 'Female', 
                 '555-987-6543', 'jane.smith@example.com', '456 Oak Ave, Sometown, ST 67890',
                 'A-', 'O-3', 'Navy', 'Active'),
                ('Robert', 'Johnson', '1982-03-12', 'Male',
                 '555-555-1234', 'robert.j@example.com', '789 Pine St, Othertown, ST 34567',
                 'B+', 'E-5', 'Air Force', 'Active'),
                ('Sarah', 'Williams', '1990-11-28', 'Female',
                 '555-222-3333', 'sarah.w@example.com', '321 Elm St, Anycity, ST 45678',
                 'AB-', 'O-2', 'Marines', 'Active')
            ON CONFLICT (patient_id) DO NOTHING
            """,
            """
            INSERT INTO records ("patientId", type, provider, date, notes, status)
            VALUES 
                (1, 'Physical Examination', 'Dr. John Smith', '2023-05-15', 'Annual physical exam. Patient in good health.', 'Completed'),
                (1, 'Vaccination', 'Dr. Jane Green', '2023-06-10', 'COVID-19 booster shot administered', 'Completed'),
                (2, 'Physical Examination', 'Dr. John Smith', '2023-07-20', 'Annual physical exam. Recommended follow-up for blood pressure.', 'Completed'),
                (3, 'Lab Work', 'Dr. Michael Brown', '2023-08-05', 'Blood work results within normal range.', 'Completed'),
                (2, 'Follow-up', 'Dr. John Smith', '2023-09-15', 'Blood pressure check. Prescribed medication.', 'Pending'),
                (4, 'Physical Examination', 'Dr. Jane Green', '2023-09-28', 'Annual physical exam. Recommended diet modifications.', 'Pending')
            ON CONFLICT (id) DO NOTHING
            """,
            """
            INSERT INTO appointments (patient_id, provider_id, appointment_date, reason, status, notes)
            VALUES 
                (1, 1, CURRENT_DATE + INTERVAL '2 hours', 'Follow-up appointment', 'Scheduled', 'Regular check-up'),
                (2, 2, CURRENT_DATE + INTERVAL '4 hours', 'Blood pressure check', 'Scheduled', 'Follow-up on medication effectiveness'),
                (3, 1, CURRENT_DATE + INTERVAL '1 day', 'Vaccination', 'Scheduled', 'Annual flu shot'),
                (4, 2, CURRENT_DATE + INTERVAL '3 days', 'Physical examination', 'Scheduled', 'Annual physical')
            ON CONFLICT (id) DO NOTHING
            """
        ]
        
        # Execute each command
        for command in commands:
            print(f"Executing: {command[:60]}...")
            cur.execute(command)
        
        # Close the cursor
        cur.close()
        
        # Commit the changes
        conn.commit()
        
        print("Sample data inserted successfully!")
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error inserting sample data: {error}")
        conn.rollback()

def main():
    """Main function to set up the database"""
    print("EHR System Database Setup")
    print("=========================")
    
    try:
        # Get database connection
        conn = get_db_connection()
        
        # Create tables
        create_tables(conn)
        
        # Insert sample data
        insert_sample_data(conn)
        
        # Close the connection
        conn.close()
        
        print("Database setup completed successfully!")
    except Exception as e:
        print(f"An error occurred during database setup: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 