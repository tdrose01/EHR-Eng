import os
import sys
import datetime
import psycopg2
from dotenv import load_dotenv

# Get the absolute path to the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables
load_dotenv(os.path.join(project_root, '.env'))

# Database connection parameters
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'ehr_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

def setup_db():
    """Set up the PostgreSQL database and initialize with test data"""
    print(f"Setting up PostgreSQL database: {DB_CONFIG['database']} on {DB_CONFIG['host']}:{DB_CONFIG['port']}")

    try:
        # Connect to the PostgreSQL server without specifying a database first
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database='postgres'  # Connect to default postgres database first
        )
        conn.autocommit = True  # Required for CREATE DATABASE
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_CONFIG['database'],))
        db_exists = cursor.fetchone()
        
        if not db_exists:
            print(f"Creating database {DB_CONFIG['database']}...")
            # Create database
            cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']}")
            print(f"Database {DB_CONFIG['database']} created")
        else:
            print(f"Database {DB_CONFIG['database']} already exists")
        
        # Close connection to postgres database
        cursor.close()
        conn.close()
        
        # Connect to the newly created database
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database']
        )
        cursor = conn.cursor()
        
        # Create patients table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id SERIAL PRIMARY KEY,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            date_of_birth DATE NOT NULL,
            gender VARCHAR(20),
            contact_number VARCHAR(20),
            email VARCHAR(100),
            address TEXT,
            emergency_contact VARCHAR(100),
            emergency_contact_number VARCHAR(20),
            blood_type VARCHAR(10),
            rank VARCHAR(10),
            service VARCHAR(50),
            fmpc VARCHAR(50),
            allergies TEXT,
            medical_conditions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Create users table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            hashed_password VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE,
            role VARCHAR(20) DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
        """)
        
        # Create login_history table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS login_history (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            "ipAddress" VARCHAR(50),
            success BOOLEAN DEFAULT FALSE
        )
        """)
        
        # Check if patients table has data
        cursor.execute("SELECT COUNT(*) FROM patients")
        patient_count = cursor.fetchone()[0]
        
        if patient_count == 0:
            print("Adding sample patient data...")
            
            # Sample patients
            sample_patients = [
                {
                    'first_name': 'Stacey',
                    'last_name': 'Calderon',
                    'date_of_birth': '1985-07-12',
                    'gender': 'Female',
                    'contact_number': '555-123-4567',
                    'email': 'stacey.calderon@mail.mil',
                    'service': 'Army',
                    'rank': 'E-5',
                    'blood_type': 'A+'
                },
                {
                    'first_name': 'Ian',
                    'last_name': 'Williams',
                    'date_of_birth': '1992-03-24',
                    'gender': 'Male',
                    'contact_number': '555-987-6543',
                    'email': 'ian.williams@mail.mil',
                    'service': 'Navy',
                    'rank': 'O-3',
                    'blood_type': 'O-'
                },
                {
                    'first_name': 'Michael',
                    'last_name': 'Castaneda',
                    'date_of_birth': '1978-11-05',
                    'gender': 'Male',
                    'contact_number': '555-345-6789',
                    'email': 'michael.castaneda@mail.mil',
                    'service': 'Air Force',
                    'rank': 'E-7',
                    'blood_type': 'B+'
                },
                {
                    'first_name': 'Matthew',
                    'last_name': 'Howard',
                    'date_of_birth': '1990-09-30',
                    'gender': 'Male',
                    'contact_number': '555-234-5678',
                    'email': 'matthew.howard@mail.mil',
                    'service': 'Marines',
                    'rank': 'E-4',
                    'blood_type': 'AB+'
                },
                {
                    'first_name': 'Sophia',
                    'last_name': 'Torres',
                    'date_of_birth': '1982-05-17',
                    'gender': 'Female',
                    'contact_number': '555-876-5432',
                    'email': 'sophia.torres@mail.mil',
                    'service': 'Coast Guard',
                    'rank': 'O-2',
                    'blood_type': 'A-'
                }
            ]
            
            for patient in sample_patients:
                # Create placeholders for the insert statement
                placeholders = ', '.join(['%s'] * len(patient))
                columns = ', '.join(patient.keys())
                
                # Insert statement
                insert_query = f"INSERT INTO patients ({columns}) VALUES ({placeholders})"
                cursor.execute(insert_query, list(patient.values()))
            
            print(f"Added {len(sample_patients)} sample patients")
            
        else:
            print(f"Patients table already has {patient_count} records")
        
        # Check if users table has data
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            print("Adding sample user data...")
            
            # Add default user account
            # In a production system, use a more secure password hashing algorithm
            cursor.execute(
                "INSERT INTO users (username, hashed_password, email, role) VALUES (%s, %s, %s, %s)",
                ('admin', 'f4c44df4c968cc29158d5886d034b699faf69cda0e3c8fb3c11845ebd0e84fa6', 'admin@example.com', 'admin')
            )
            cursor.execute(
                "INSERT INTO users (username, hashed_password, email, role) VALUES (%s, %s, %s, %s)",
                ('testuser', '2555e06e5b55e1ff1c346de5ba02bedd24fb5f17a2c1a4ad4397965d1dc9cc20', 'testuser@example.com', 'user')
            )
            
            print("Added sample users (admin/adminpass123, testuser/password)")
        else:
            print(f"Users table already has {user_count} records")
        
        # Commit changes
        conn.commit()
        print("PostgreSQL database setup complete!")
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error setting up database: {error}")
    finally:
        if 'conn' in locals() and conn:
            cursor.close()
            conn.close()
            print("Database connection closed")

if __name__ == "__main__":
    setup_db() 