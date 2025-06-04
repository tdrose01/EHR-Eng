import os
import sys
import sqlite3
import datetime

# Get the absolute path to the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
db_path = os.path.join(project_root, '..', 'ehr.db')

def setup_db():
    """Set up the SQLite database and initialize with test data"""
    print(f"Setting up database at {db_path}")
    
    # Check if database exists
    db_exists = os.path.exists(db_path)
    
    # Connect to database (creates it if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    if not db_exists:
        print("Creating new database...")
        
        # Create patients table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            date_of_birth TEXT NOT NULL,
            gender TEXT,
            contact_number TEXT,
            email TEXT,
            address TEXT,
            emergency_contact TEXT,
            emergency_contact_number TEXT,
            blood_type TEXT,
            rank TEXT,
            service TEXT,
            fmpc TEXT,
            allergies TEXT,
            medical_conditions TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        ''')
        
        # Insert test data
        test_patients = [
            {
                'first_name': 'Stacey',
                'last_name': 'Calderon',
                'date_of_birth': '1985-07-12',
                'gender': 'Female',
                'contact_number': '555-123-4567',
                'email': 'stacey.calderon@mail.mil',
                'service': 'Army',
                'rank': 'E-5',
                'blood_type': 'A+',
                'created_at': datetime.datetime.now().isoformat(),
                'updated_at': datetime.datetime.now().isoformat()
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
                'blood_type': 'O-',
                'created_at': datetime.datetime.now().isoformat(),
                'updated_at': datetime.datetime.now().isoformat()
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
                'blood_type': 'B+',
                'created_at': datetime.datetime.now().isoformat(),
                'updated_at': datetime.datetime.now().isoformat()
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
                'blood_type': 'AB+',
                'created_at': datetime.datetime.now().isoformat(),
                'updated_at': datetime.datetime.now().isoformat()
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
                'blood_type': 'A-',
                'created_at': datetime.datetime.now().isoformat(),
                'updated_at': datetime.datetime.now().isoformat()
            }
        ]
        
        for patient in test_patients:
            fields = ', '.join(patient.keys())
            placeholders = ', '.join(['?' for _ in patient])
            values = list(patient.values())
            
            cursor.execute(f"INSERT INTO patients ({fields}) VALUES ({placeholders})", values)
        
        # Commit changes
        conn.commit()
        print("Database initialized with test data!")
    else:
        print("Database already exists, checking for patients table...")
        
        # Check if patients table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='patients'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("Patients table doesn't exist, creating...")
            # Create patients table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                date_of_birth TEXT NOT NULL,
                gender TEXT,
                contact_number TEXT,
                email TEXT,
                address TEXT,
                emergency_contact TEXT,
                emergency_contact_number TEXT,
                blood_type TEXT,
                rank TEXT,
                service TEXT,
                fmpc TEXT,
                allergies TEXT,
                medical_conditions TEXT,
                created_at TEXT,
                updated_at TEXT
            )
            ''')
            conn.commit()
            print("Patients table created!")
        else:
            # Check if table has data
            cursor.execute("SELECT COUNT(*) FROM patients")
            count = cursor.fetchone()[0]
            
            if count == 0:
                print("Patients table exists but is empty, adding test data...")
                # Insert test data
                test_patients = [
                    {
                        'first_name': 'Stacey',
                        'last_name': 'Calderon',
                        'date_of_birth': '1985-07-12',
                        'gender': 'Female',
                        'contact_number': '555-123-4567',
                        'email': 'stacey.calderon@mail.mil',
                        'service': 'Army',
                        'rank': 'E-5',
                        'blood_type': 'A+',
                        'created_at': datetime.datetime.now().isoformat(),
                        'updated_at': datetime.datetime.now().isoformat()
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
                        'blood_type': 'O-',
                        'created_at': datetime.datetime.now().isoformat(),
                        'updated_at': datetime.datetime.now().isoformat()
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
                        'blood_type': 'B+',
                        'created_at': datetime.datetime.now().isoformat(),
                        'updated_at': datetime.datetime.now().isoformat()
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
                        'blood_type': 'AB+',
                        'created_at': datetime.datetime.now().isoformat(),
                        'updated_at': datetime.datetime.now().isoformat()
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
                        'blood_type': 'A-',
                        'created_at': datetime.datetime.now().isoformat(),
                        'updated_at': datetime.datetime.now().isoformat()
                    }
                ]
                
                for patient in test_patients:
                    fields = ', '.join(patient.keys())
                    placeholders = ', '.join(['?' for _ in patient])
                    values = list(patient.values())
                    
                    cursor.execute(f"INSERT INTO patients ({fields}) VALUES ({placeholders})", values)
                
                # Commit changes
                conn.commit()
                print("Test data added to patients table!")
            else:
                print(f"Patients table already exists with {count} records.")
    
    # Close connection
    conn.close()
    print("Database setup complete!")

if __name__ == "__main__":
    setup_db() 