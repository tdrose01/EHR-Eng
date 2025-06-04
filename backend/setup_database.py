#!/usr/bin/env python3
"""
Database initialization script for EHR system.
This script should be run before starting the EHR system to ensure the database is properly set up.
"""

import os
import sys
import time
import psycopg2
from datetime import datetime

# Add the parent directory to path so we can import modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))

# Import database setup functions
from database.setup_db_tables import get_db_connection, create_tables, insert_sample_data
from database.check_db_tables import check_tables

def initialize_database():
    """Initialize the database with tables and sample data"""
    print("\n====================================")
    print("  EHR Database Initialization Tool  ")
    print("====================================\n")
    
    print("Starting database initialization...")
    
    # Check if all tables already exist
    print("Checking if database tables already exist...")
    if check_tables():
        print("All required tables already exist, skipping initialization.")
        return True
    
    # Try to connect to the database
    try:
        print("Connecting to database...")
        conn = get_db_connection()
        if not conn:
            print("ERROR: Could not connect to database. Please check your configuration.")
            return False
        
        # Create tables
        print("\nCreating tables...")
        create_tables(conn)
        
        # Insert sample data
        print("\nInserting sample data...")
        insert_sample_data(conn)
        
        # Close the connection
        conn.close()
        
        # Verify tables were created
        if check_tables():
            print("\nDatabase initialization completed successfully!")
            print("\n=========================================")
            print("  All tables and sample data are ready!  ")
            print("=========================================\n")
            return True
        else:
            print("\nERROR: Some tables are still missing after initialization.")
            return False
        
    except Exception as e:
        print(f"ERROR: Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    initialize_database() 