#!/usr/bin/env python3
"""Initialize the database with the schema."""

import os
import psycopg2

def init_db():
    """Initialize the database with the schema."""
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            port=os.environ.get('DB_PORT', '5432'),
            dbname=os.environ.get('DB_NAME', 'healthrecords'),
            user=os.environ.get('DB_USER', 'postgres'),
            password=os.environ.get('DB_PASSWORD', 'postgres')
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Read and execute schema
        with open(os.path.join(os.path.dirname(__file__), 'schema.sql'), 'r') as f:
            schema = f.read()
            cursor.execute(schema)
        
        print("Database initialized successfully")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    init_db() 