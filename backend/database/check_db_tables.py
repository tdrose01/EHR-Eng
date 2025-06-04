#!/usr/bin/env python3
"""
Check if all required database tables exist.
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database connection parameters
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'ehr_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

REQUIRED_TABLES = [
    'users', 'user_logins', 'user_sessions', 'patients',
    'records', 'appointments', 'medications'
]

def check_tables():
    """Check if all required tables exist in the database"""
    conn = None
    try:
        # Connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        
        # Create a cursor
        cur = conn.cursor()
        
        # Get all tables in the database
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        
        existing_tables = [row[0] for row in cur.fetchall()]
        
        # Check if all required tables exist
        missing_tables = [table for table in REQUIRED_TABLES if table not in existing_tables]
        
        if missing_tables:
            print(f"Missing tables: {', '.join(missing_tables)}")
            return False
        else:
            print("All required tables exist.")
            return True
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error checking tables: {error}")
        return False
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    success = check_tables()
    sys.exit(0 if success else 1) 