#!/usr/bin/env python3
"""
Minimal version of the vaccine API server focusing just on the test_vaccines table
"""
import os
import sys
import datetime
import json
from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor

# Create Flask app
app = Flask(__name__)
CORS(app)

# Database configuration
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'postgres')
DB_NAME = os.environ.get('DB_NAME', 'test_vaccines')

# In-memory data (fallback if database connection fails)
test_vaccines = [
    {
        "id": 1,
        "name": "Flu Vaccine",
        "manufacturer": "BioPharm",
        "description": "Annual influenza vaccine for seasonal flu protection",
        "created_at": datetime.datetime.now().isoformat()
    },
    {
        "id": 2,
        "name": "COVID-19 Vaccine",
        "manufacturer": "ModernTech",
        "description": "mRNA-based vaccine against SARS-CoV-2",
        "created_at": datetime.datetime.now().isoformat()
    }
]

def initialize_database():
    """Create and initialize the test_vaccines database and table"""
    try:
        # First connect to default postgres database to create our database
        print(f"Connecting to postgres database to create {DB_NAME} if needed...")
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if our database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        if not cursor.fetchone():
            print(f"Creating database {DB_NAME}...")
            cursor.execute(f"CREATE DATABASE {DB_NAME}")
            print(f"Database {DB_NAME} created successfully")
        else:
            print(f"Database {DB_NAME} already exists")
            
        cursor.close()
        conn.close()
        
        # Now connect to our database to create table
        print(f"Connecting to {DB_NAME} database to create test_vaccines table if needed...")
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Create test_vaccines table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_vaccines (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            manufacturer VARCHAR(255),
            description TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
        """)
        print("Table test_vaccines created or already exists")
        
        # Check if we have data already
        cursor.execute("SELECT COUNT(*) FROM test_vaccines")
        if cursor.fetchone()[0] == 0:
            print("Inserting sample data into test_vaccines...")
            cursor.execute("""
            INSERT INTO test_vaccines (name, manufacturer, description)
            VALUES 
                ('Flu Vaccine', 'BioPharm', 'Annual influenza vaccine for seasonal flu protection'),
                ('COVID-19 Vaccine', 'ModernTech', 'mRNA-based vaccine against SARS-CoV-2'),
                ('Tdap Vaccine', 'ImmuneCorp', 'Tetanus, diphtheria, and pertussis vaccine for adults'),
                ('Hepatitis B Vaccine', 'LiverShield', 'Vaccine to prevent hepatitis B viral infection'),
                ('HPV Vaccine', 'CancerGuard', 'Human papillomavirus vaccine to prevent certain cancers')
            """)
            print("Sample data inserted successfully")
        else:
            print("Table test_vaccines already has data")
            
        cursor.close()
        conn.close()
        print("Database initialization successful")
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

@app.route('/api/vaccines/test', methods=['GET'])
def test_endpoint():
    """Simple test endpoint that doesn't require database access"""
    return jsonify({
        "success": True,
        "message": "Vaccine API is working",
        "timestamp": datetime.datetime.now().isoformat()
    })

@app.route('/api/vaccines/simple', methods=['GET'])
def get_simple_vaccines():
    """Get vaccines from test_vaccines table"""
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get vaccines from database
        cursor.execute("SELECT * FROM test_vaccines")
        vaccines = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "vaccines": vaccines
        })
    except Exception as e:
        print(f"Error accessing database: {e}")
        # Fall back to in-memory data
        return jsonify({
            "success": False,
            "message": f"Database error: {str(e)}",
            "vaccines": test_vaccines
        })

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get server status"""
    status = {
        "server": "running",
        "timestamp": datetime.datetime.now().isoformat(),
        "db_config": {
            "host": DB_HOST,
            "port": DB_PORT,
            "database": DB_NAME,
            "user": DB_USER
        }
    }
    
    # Try to get database status
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        
        # Check if test_vaccines table exists
        cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables WHERE table_name = 'test_vaccines'
        )
        """)
        table_exists = cursor.fetchone()[0]
        
        # Get count of vaccines
        if table_exists:
            cursor.execute("SELECT COUNT(*) FROM test_vaccines")
            count = cursor.fetchone()[0]
        else:
            count = 0
        
        status["database"] = {
            "connected": True,
            "test_vaccines_table_exists": table_exists,
            "test_vaccines_count": count
        }
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error checking database status: {e}")
        status["database"] = {
            "connected": False,
            "error": str(e)
        }
    
    return jsonify(status)

if __name__ == "__main__":
    print("Starting minimal vaccine API server")
    initialize_database()
    
    port = int(os.environ.get("PORT", 8004))
    print(f"Server running on http://localhost:{port}")
    print(f"Test endpoint: http://localhost:{port}/api/vaccines/test")
    print(f"Simple vaccines endpoint: http://localhost:{port}/api/vaccines/simple")
    print(f"Status endpoint: http://localhost:{port}/api/status")
    
    app.run(host='0.0.0.0', port=port) 