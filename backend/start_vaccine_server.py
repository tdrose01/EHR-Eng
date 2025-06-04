#!/usr/bin/env python3
"""
Simple script to start the vaccine API server with direct database setup
"""
import os
import sys
import psycopg2
import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import subprocess
import time
import signal
import atexit
import random
import json

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)
CORS(app)

def get_db_connection():
    """Create a connection to the PostgreSQL database"""
    try:
        # First try to use the connection string if provided
        conn_string = os.environ.get('DB_CONNECTION_STRING')
        if conn_string:
            conn = psycopg2.connect(conn_string)
            return conn
        
        # Otherwise use individual parameters
        conn = psycopg2.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            port=os.environ.get('DB_PORT', '5432'),
            dbname=os.environ.get('DB_NAME', 'ehr_db'),
            user=os.environ.get('DB_USER', 'postgres'),
            password=os.environ.get('DB_PASSWORD', 'postgres')
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def setup_database():
    """Set up a simple database for testing if migrations haven't been run"""
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return False
    
    conn.autocommit = True
    cursor = conn.cursor()
    
    try:
        # Check if the test_vaccines table exists
        cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'test_vaccines'
        )
        """)
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("Creating test_vaccines table...")
            # Create test table for vaccines with schema matching the migration
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_vaccines (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                manufacturer VARCHAR(255),
                description TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Insert sample data matching the migration
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
            print("test_vaccines table already exists")
        
        conn.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error setting up database: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

@app.route('/api/vaccines/test', methods=['GET'])
def test_endpoint():
    """Simple test endpoint that doesn't require complex DB setup"""
    return jsonify({
        "success": True,
        "message": "Vaccine API is working",
        "timestamp": datetime.datetime.now().isoformat()
    })

@app.route('/api/vaccines/simple', methods=['GET'])
def get_simple_vaccines():
    """Simple endpoint to get vaccines from test table"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database connection failed"}), 500
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM test_vaccines")
        vaccines = cursor.fetchall()
        
        return jsonify({
            "success": True,
            "vaccines": vaccines
        })
    except Exception as e:
        print(f"Error fetching vaccines: {e}")
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/vaccines/schedules', methods=['GET'])
def get_vaccine_schedules():
    """Get vaccine schedules from the vaccine_schedules table"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database connection failed"}), 500
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("""
        SELECT * FROM vaccine_schedules ORDER BY vaccine_name, dose_number
        """)
        schedules = cursor.fetchall()
        
        return jsonify({
            "success": True,
            "schedules": schedules
        })
    except Exception as e:
        print(f"Error fetching vaccine schedules: {e}")
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/vaccines/next-dose/<vaccine_name>/<int:dose_number>/<age_group>', methods=['GET'])
def get_next_dose_date(vaccine_name, dose_number, age_group):
    """Calculate next dose date based on the current dose"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database connection failed"}), 500
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Call the PostgreSQL function to calculate next dose date
        cursor.execute("""
        SELECT calculate_next_dose(%s, %s, %s) AS next_dose
        """, (vaccine_name, dose_number, age_group))
        
        result = cursor.fetchone()
        
        return jsonify({
            "success": True,
            "next_dose": result
        })
    except Exception as e:
        print(f"Error calculating next dose date: {e}")
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        conn = get_db_connection()
        if conn:
            conn.close()
            return jsonify({
                "status": "healthy",
                "database": "connected",
                "timestamp": datetime.datetime.now().isoformat()
            })
        else:
            return jsonify({
                "status": "unhealthy",
                "database": "disconnected",
                "timestamp": datetime.datetime.now().isoformat()
            }), 503
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.datetime.now().isoformat()
        }), 500

if __name__ == "__main__":
    print("Setting up test database...")
    if setup_database():
        print("Database setup complete")
    else:
        print("Database setup failed, but continuing anyway...")
    
    # Use fixed port 8004 to ensure consistency
    port = 8004
    print(f"Starting server on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port) 