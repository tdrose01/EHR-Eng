#!/usr/bin/env python3
"""
Start the main API services for the EHR Vue application

This script starts the main API on port 8000 which includes patient and dashboard functionality
"""

import os
import sys
import subprocess
import time
import signal
import atexit
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import random
import json

# Database configuration
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'postgres')
DB_NAME = os.environ.get('DB_NAME', 'ehr_db')

# API configuration
API_PORT = int(os.environ.get('API_PORT', '8000'))
API_HOST = os.environ.get('API_HOST', '0.0.0.0')
DEBUG_MODE = os.environ.get('DEBUG', 'False').lower() == 'true'

app = Flask(__name__)
CORS(app)

# Remove these sample data sections
SAMPLE_PATIENTS = []
DASHBOARD_STATS = {}

# Helper function to connect to database
def get_db_connection():
    """Get a connection to the PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

# API endpoints for patients
@app.route('/api/patients', methods=['GET'])
def get_patients():
    """Get all patients or filtered by query"""
    limit = request.args.get('limit', default=None, type=int)
    offset = request.args.get('offset', default=0, type=int)
    search = request.args.get('search', default='', type=str)
    
    conn = get_db_connection()
    if not conn:
        return jsonify({
            "success": False,
            "error": "Database connection failed"
        }), 503
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build query with filters
        query_conditions = []
        query_params = []
        
        # Add search filter if provided
        if search:
            query_conditions.append("(first_name ILIKE %s OR last_name ILIKE %s)")
            search_pattern = f"%{search}%"
            query_params.extend([search_pattern, search_pattern])
        
        # Construct WHERE clause
        where_clause = " AND ".join(query_conditions)
        if where_clause:
            where_clause = f"WHERE {where_clause}"
        
        # Get total count
        count_query = f"SELECT COUNT(*) FROM patients {where_clause}"
        cursor.execute(count_query, query_params)
        total_count = cursor.fetchone()['count']
        
        # Get paginated patients
        query = f"""
            SELECT 
                patient_id as id, 
                first_name, 
                last_name,
                date_of_birth as dob,
                gender,
                email,
                phone,
                status,
                blood_type
            FROM patients
            {where_clause}
            ORDER BY last_name, first_name
            LIMIT %s OFFSET %s
        """
        query_params.extend([limit if limit else 100, offset])
        cursor.execute(query, query_params)
        
        patients = cursor.fetchall()
        
        # Format the patients for the frontend
        formatted_patients = []
        for patient in patients:
            # Convert RealDictRow to dict and rename keys to match frontend expectations
            patient_dict = dict(patient)
            # Add camelCase versions of keys for frontend compatibility
            patient_dict["firstName"] = patient["first_name"]
            patient_dict["lastName"] = patient["last_name"]
            patient_dict["dateOfBirth"] = patient["dob"]
            formatted_patients.append(patient_dict)
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "patients": formatted_patients,
            "total": total_count
        })
    
    except Exception as e:
        print(f"Error fetching patients from database: {e}")
        if conn:
            conn.close()
        
        return jsonify({
            "success": False,
            "error": "Database error occurred"
        }), 500

@app.route('/api/patients/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    """Get a specific patient by ID"""
    conn = get_db_connection()
    if not conn:
        return jsonify({
            "success": False,
            "error": "Database connection failed"
        }), 503
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = """
            SELECT 
                patient_id as id,
                first_name,
                last_name,
                date_of_birth as dob,
                gender,
                email,
                phone,
                status,
                blood_type
            FROM patients 
            WHERE patient_id = %s
        """
        cursor.execute(query, (patient_id,))
        patient = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if patient:
            # Format patient data for frontend
            patient_dict = dict(patient)
            patient_dict["firstName"] = patient["first_name"]
            patient_dict["lastName"] = patient["last_name"]
            patient_dict["dateOfBirth"] = patient["dob"]
            return jsonify(patient_dict)
        
        return jsonify({"success": False, "error": "Patient not found"}), 404
        
    except Exception as e:
        print(f"Error fetching patient from database: {e}")
        if conn:
            conn.close()
        return jsonify({
            "success": False,
            "error": "Database error occurred"
        }), 500

@app.route('/api/patients', methods=['POST'])
def create_patient():
    """Create a new patient"""
    data = request.json
    required_fields = ['firstName', 'lastName', 'dateOfBirth', 'gender']
    
    # Validate required fields
    for field in required_fields:
        if field not in data:
            return jsonify({
                "success": False,
                "error": f"Missing required field: {field}"
            }), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({
            "success": False,
            "error": "Database connection failed"
        }), 503
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = """
            INSERT INTO patients (
                first_name,
                last_name,
                date_of_birth,
                gender,
                email,
                phone,
                status,
                blood_type
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING patient_id as id
        """
        
        cursor.execute(query, (
            data['firstName'],
            data['lastName'],
            data['dateOfBirth'],
            data['gender'],
            data.get('email'),
            data.get('phone'),
            data.get('status', 'Active'),
            data.get('bloodType')
        ))
        
        new_patient_id = cursor.fetchone()['id']
        conn.commit()
        
        # Fetch the created patient
        cursor.execute("""
            SELECT 
                patient_id as id,
                first_name,
                last_name,
                date_of_birth as dob,
                gender,
                email,
                phone,
                status,
                blood_type
            FROM patients 
            WHERE patient_id = %s
        """, (new_patient_id,))
        
        new_patient = cursor.fetchone()
        cursor.close()
        conn.close()
        
        # Format patient data for frontend
        patient_dict = dict(new_patient)
        patient_dict["firstName"] = new_patient["first_name"]
        patient_dict["lastName"] = new_patient["last_name"]
        patient_dict["dateOfBirth"] = new_patient["dob"]
        
        return jsonify({
            "success": True,
            "message": "Patient created successfully",
            "patient": patient_dict
        })
        
    except Exception as e:
        print(f"Error creating patient in database: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return jsonify({
            "success": False,
            "error": "Database error occurred"
        }), 500

@app.route('/api/patients/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    """Update an existing patient"""
    data = request.json
    
    conn = get_db_connection()
    if not conn:
        return jsonify({
            "success": False,
            "error": "Database connection failed"
        }), 503
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # First check if patient exists
        cursor.execute("SELECT patient_id FROM patients WHERE patient_id = %s", (patient_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "error": "Patient not found"
            }), 404
        
        # Build update query dynamically based on provided fields
        update_fields = []
        update_values = []
        
        field_mapping = {
            'firstName': 'first_name',
            'lastName': 'last_name',
            'dateOfBirth': 'date_of_birth',
            'gender': 'gender',
            'email': 'email',
            'phone': 'phone',
            'status': 'status',
            'bloodType': 'blood_type'
        }
        
        for frontend_field, db_field in field_mapping.items():
            if frontend_field in data:
                update_fields.append(f"{db_field} = %s")
                update_values.append(data[frontend_field])
        
        if not update_fields:
            return jsonify({
                "success": False,
                "error": "No fields to update"
            }), 400
        
        # Add patient_id to values
        update_values.append(patient_id)
        
        # Execute update
        query = f"""
            UPDATE patients 
            SET {', '.join(update_fields)}
            WHERE patient_id = %s
            RETURNING 
                patient_id as id,
                first_name,
                last_name,
                date_of_birth as dob,
                gender,
                email,
                phone,
                status,
                blood_type
        """
        
        cursor.execute(query, update_values)
        updated_patient = cursor.fetchone()
        conn.commit()
        
        cursor.close()
        conn.close()
        
        # Format patient data for frontend
        patient_dict = dict(updated_patient)
        patient_dict["firstName"] = updated_patient["first_name"]
        patient_dict["lastName"] = updated_patient["last_name"]
        patient_dict["dateOfBirth"] = updated_patient["dob"]
        
        return jsonify({
            "success": True,
            "message": "Patient updated successfully",
            "patient": patient_dict
        })
        
    except Exception as e:
        print(f"Error updating patient in database: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return jsonify({
            "success": False,
            "error": "Database error occurred"
        }), 500

@app.route('/api/patients/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    """Delete a patient"""
    conn = get_db_connection()
    if not conn:
        return jsonify({
            "success": False,
            "error": "Database connection failed"
        }), 503
    
    try:
        cursor = conn.cursor()
        
        # First check if patient exists
        cursor.execute("SELECT patient_id FROM patients WHERE patient_id = %s", (patient_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "error": "Patient not found"
            }), 404
        
        # Delete the patient
        cursor.execute("DELETE FROM patients WHERE patient_id = %s", (patient_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": f"Patient {patient_id} deleted successfully"
        })
        
    except Exception as e:
        print(f"Error deleting patient from database: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return jsonify({
            "success": False,
            "error": "Database error occurred"
        }), 500

# Dashboard API endpoints
@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics from the database"""
    print("\n==== DASHBOARD STATS API CALLED ====")
    print(f"Time: {datetime.now().isoformat()}")
    print(f"Request headers: {dict(request.headers)}")
    
    conn = get_db_connection()
    if not conn:
        print("ERROR: Database connection failed")
        return jsonify({
            "success": False,
            "error": "Database connection failed"
        }), 503
    
    print("Database connection successful")
    
    try:
        cursor = conn.cursor()
        
        stats = {
            "totalPatients": 0,
            "activePatients": 0,
            "appointmentsToday": 0,
            "pendingRecords": 0
        }
        
        # Get total patients count - this should always work
        try:
            cursor.execute("SELECT COUNT(*) FROM patients")
            stats["totalPatients"] = cursor.fetchone()[0]
            print(f"Total patients count: {stats['totalPatients']}")
        except Exception as e:
            print(f"Error getting total patients: {e}")
            # Continue with default value
        
        # Get active patients count - this should always work
        try:
            cursor.execute("SELECT COUNT(*) FROM patients WHERE status = 'Active'")
            stats["activePatients"] = cursor.fetchone()[0]
            print(f"Active patients count: {stats['activePatients']}")
        except Exception as e:
            print(f"Error getting active patients: {e}")
            # Continue with default value
        
        # Get today's appointments - verify table exists first
        try:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'appointments'
                )
            """)
            table_exists = cursor.fetchone()[0]
            print(f"Appointments table exists: {table_exists}")
            
            if table_exists:
                today = datetime.now().strftime('%Y-%m-%d')
                cursor.execute("SELECT COUNT(*) FROM appointments WHERE DATE(appointment_date) = %s", (today,))
                stats["appointmentsToday"] = cursor.fetchone()[0]
                print(f"Today's appointments count: {stats['appointmentsToday']}")
        except Exception as e:
            print(f"Error getting appointments: {e}")
            # Continue with default value
        
        # Get pending records count - verify table exists first
        try:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'records'
                )
            """)
            table_exists = cursor.fetchone()[0]
            print(f"Records table exists: {table_exists}")
            
            if table_exists:
                cursor.execute("SELECT COUNT(*) FROM records WHERE status = 'Pending'")
                stats["pendingRecords"] = cursor.fetchone()[0]
                print(f"Pending records count: {stats['pendingRecords']}")
        except Exception as e:
            print(f"Error getting pending records: {e}")
            # Continue with default value
        
        cursor.close()
        conn.close()
        
        print(f"Returning stats: {stats}")
        print("==== DASHBOARD STATS API COMPLETED ====\n")
        
        return jsonify({
            "success": True,
            "stats": stats
        })
    except Exception as e:
        print(f"Error retrieving dashboard stats: {e}")
        print("==== DASHBOARD STATS API FAILED ====\n")
        if conn:
            conn.close()
        
        return jsonify({
            "success": False,
            "error": "Database error occurred"
        }), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get API status"""
    return jsonify({
        "status": "running",
        "service": "patient_api",
        "timestamp": datetime.now().isoformat()
    })

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
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "status": "unhealthy",
                "database": "disconnected",
                "timestamp": datetime.now().isoformat()
            }), 503
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    print(f"Starting Main API on {API_HOST}:{API_PORT}")
    print(f"Database: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    app.run(host=API_HOST, port=API_PORT, debug=DEBUG_MODE) 