#!/usr/bin/env python3
"""
Simple script to count patients in the PostgreSQL database
"""

import psycopg2
import sys

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'ehr_db',
    'user': 'postgres',
    'password': 'postgres'
}

def get_patient_count():
    """Connect to the database and get the total patient count"""
    try:
        print("Connecting to PostgreSQL database...")
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        
        cursor = conn.cursor()
        
        # Check if patients table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'patients'
            )
        """)
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("Patients table does not exist in the database.")
            return None
        
        # Get patient count
        cursor.execute("SELECT COUNT(*) FROM patients")
        count = cursor.fetchone()[0]
        
        # Close connection
        cursor.close()
        conn.close()
        
        return count
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

if __name__ == "__main__":
    count = get_patient_count()
    if count is not None:
        print(f"\nTotal patients in database: {count}")
    else:
        print("\nFailed to retrieve patient count from database.") 