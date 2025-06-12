import os
import sys
import psycopg2
from psycopg2 import sql
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file (configurable via ENV_PATH)
env_path = os.getenv('ENV_PATH', '.env')
load_dotenv(env_path)

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
            hashed_password VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'user',
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS login_history (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            timestamp TIMESTAMP NOT NULL,
            "ipAddress" VARCHAR(45) NOT NULL,
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
            id SERIAL PRIMARY KEY,
            medical_record_number VARCHAR(50) UNIQUE NOT NULL,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            date_of_birth DATE NOT NULL,
            gender VARCHAR(20),
            address VARCHAR(255),
            phone VARCHAR(20),
            email VARCHAR(100),
            insurance_provider VARCHAR(100),
            insurance_id VARCHAR(50),
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS visits (
            id SERIAL PRIMARY KEY,
            patient_id INTEGER REFERENCES patients(id),
            visit_date TIMESTAMP NOT NULL,
            visit_type VARCHAR(50) NOT NULL,
            provider_id INTEGER REFERENCES users(id),
            reason_for_visit TEXT,
            diagnosis TEXT,
            notes TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS medications (
            id SERIAL PRIMARY KEY,
            patient_id INTEGER REFERENCES patients(id),
            medication_name VARCHAR(100) NOT NULL,
            dosage VARCHAR(50) NOT NULL,
            frequency VARCHAR(50) NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE,
            prescriber_id INTEGER REFERENCES users(id),
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
        """
        CREATE TABLE IF NOT EXISTS appointments (
            id SERIAL PRIMARY KEY,
            patient_id INTEGER REFERENCES patients(id),
            provider_id INTEGER REFERENCES users(id),
            appointment_time TIMESTAMP NOT NULL,
            reason TEXT,
            status VARCHAR(20) NOT NULL DEFAULT 'Scheduled',
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
    commands = [
        """
        INSERT INTO users (username, email, full_name, hashed_password, role)
        VALUES 
            ('admin', 'admin@example.com', 'Administrator', 
             '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'admin'),
            ('doctor1', 'doctor1@example.com', 'Dr. John Smith', 
             '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 'doctor'),
            ('nurse1', 'nurse1@example.com', 'Jane Doe, RN', 
             '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 'nurse')
        ON CONFLICT (username) DO NOTHING
        """,
        """
        INSERT INTO patients (medical_record_number, first_name, last_name, date_of_birth, gender, 
                            address, phone, email, insurance_provider, insurance_id)
        VALUES 
            ('MRN12345', 'John', 'Doe', '1975-05-15', 'Male', 
             '123 Main St, Anytown, ST 12345', '555-123-4567', 'john.doe@example.com', 
             'Blue Cross', 'BC123456789'),
            ('MRN67890', 'Jane', 'Smith', '1980-08-20', 'Female', 
             '456 Oak Ave, Sometown, ST 67890', '555-987-6543', 'jane.smith@example.com', 
             'Aetna', 'AE987654321')
        ON CONFLICT (medical_record_number) DO NOTHING
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