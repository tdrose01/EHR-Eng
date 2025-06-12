import os
import sys
import json
import psycopg2
import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
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

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def get_db_connection():
    """Connect to the PostgreSQL database server"""
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error connecting to database: {error}")
        return None

@app.route('/api/patients', methods=['GET'])
def get_patients():
    """API endpoint to retrieve patient data"""
    # Get query parameters
    search = request.args.get('search', '')
    limit = int(request.args.get('limit', 10))
    offset = int(request.args.get('offset', 0))
    
    # Connect to database
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database connection failed"}), 500
    
    cursor = conn.cursor()
    
    try:
        # Get total count for pagination
        if search:
            cursor.execute(
                """
                SELECT COUNT(*) 
                FROM patients 
                WHERE 
                    first_name ILIKE %s OR 
                    last_name ILIKE %s OR 
                    CAST(patient_id AS TEXT) LIKE %s
                """,
                (f'%{search}%', f'%{search}%', f'%{search}%')
            )
        else:
            cursor.execute("SELECT COUNT(*) FROM patients")
        
        total_count = cursor.fetchone()[0]
        
        # Fetch patients with pagination and search
        if search:
            cursor.execute(
                """
                SELECT 
                    p.patient_id, 
                    p.first_name, 
                    p.last_name, 
                    p.date_of_birth, 
                    p.gender,
                    p.contact_number,
                    p.email,
                    p.blood_type,
                    p.rank,
                    p.service,
                    p.allergies,
                    p.medical_conditions
                FROM patients p
                WHERE 
                    p.first_name ILIKE %s OR 
                    p.last_name ILIKE %s OR 
                    CAST(p.patient_id AS TEXT) LIKE %s
                ORDER BY p.last_name, p.first_name
                LIMIT %s OFFSET %s
                """,
                (f'%{search}%', f'%{search}%', f'%{search}%', limit, offset)
            )
        else:
            cursor.execute(
                """
                SELECT 
                    p.patient_id, 
                    p.first_name, 
                    p.last_name, 
                    p.date_of_birth, 
                    p.gender,
                    p.contact_number,
                    p.email,
                    p.blood_type,
                    p.rank,
                    p.service,
                    p.allergies,
                    p.medical_conditions
                FROM patients p
                ORDER BY p.last_name, p.first_name
                LIMIT %s OFFSET %s
                """,
                (limit, offset)
            )
        
        # Convert query result to list of dictionaries
        column_names = [desc[0] for desc in cursor.description]
        patients = []
        
        for row in cursor.fetchall():
            patient = dict(zip(column_names, row))
            
            # Convert date objects to string
            if isinstance(patient['date_of_birth'], (datetime.date, datetime.datetime)):
                patient['date_of_birth'] = patient['date_of_birth'].isoformat()
            
            patients.append(patient)
        
        return jsonify({
            "success": True,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "patients": patients
        })
        
    except Exception as e:
        print(f"Error fetching patients: {e}")
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/patients/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    """API endpoint to retrieve a specific patient's data"""
    # Connect to database
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database connection failed"}), 500
    
    cursor = conn.cursor()
    
    try:
        # Fetch the specific patient
        cursor.execute(
            """
            SELECT 
                p.patient_id, 
                p.first_name, 
                p.last_name, 
                p.date_of_birth, 
                p.gender,
                p.contact_number,
                p.email,
                p.address,
                p.emergency_contact,
                p.emergency_contact_number,
                p.blood_type,
                p.rank,
                p.service,
                p.fmpc,
                p.allergies,
                p.medical_conditions,
                p.created_at,
                p.updated_at
            FROM patients p
            WHERE p.patient_id = %s
            """,
            (patient_id,)
        )
        
        result = cursor.fetchone()
        
        if not result:
            return jsonify({"success": False, "message": "Patient not found"}), 404
        
        # Convert query result to dictionary
        column_names = [desc[0] for desc in cursor.description]
        patient = dict(zip(column_names, result))
        
        # Convert date/datetime objects to string
        for key, value in patient.items():
            if isinstance(value, (datetime.date, datetime.datetime)):
                patient[key] = value.isoformat()
        
        return jsonify({
            "success": True,
            "patient": patient
        })
        
    except Exception as e:
        print(f"Error fetching patient: {e}")
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/dashboard-stats', methods=['GET'])
def get_dashboard_stats():
    """API endpoint to retrieve dashboard statistics"""
    # Connect to database
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database connection failed"}), 500
    
    cursor = conn.cursor()
    
    try:
        # Get total patients count
        cursor.execute("SELECT COUNT(*) FROM patients")
        total_patients = cursor.fetchone()[0]
        
        # For this example, we'll simulate some of the dashboard stats
        # In a real application, we would calculate these from the database
        
        # Active patients (90% of total for this example)
        active_patients = int(total_patients * 0.9)
        
        # Pending records (5% of total)
        pending_records = int(total_patients * 0.05)
        
        # Today's appointments (simulated)
        appointments_today = min(12, int(total_patients * 0.1))
        
        return jsonify({
            "success": True,
            "stats": {
                "totalPatients": total_patients,
                "activePatients": active_patients,
                "appointmentsToday": appointments_today,
                "pendingRecords": pending_records
            }
        })
        
    except Exception as e:
        print(f"Error fetching dashboard stats: {e}")
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/patients', methods=['POST'])
def add_patient():
    """API endpoint to create a new patient"""
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database connection failed"}), 500

    cursor = conn.cursor()

    try:
        allowed_fields = [
            "first_name",
            "last_name",
            "date_of_birth",
            "gender",
            "contact_number",
            "email",
            "address",
            "emergency_contact",
            "emergency_contact_number",
            "blood_type",
            "rank",
            "service",
            "fmpc",
            "allergies",
            "medical_conditions"
        ]

        fields = []
        placeholders = []
        params = []

        for field in allowed_fields:
            if field in data:
                fields.append(field)
                placeholders.append("%s")
                params.append(data[field])

        # Add timestamps
        fields.extend(["created_at", "updated_at"])
        placeholders.extend(["%s", "%s"])
        now = datetime.datetime.now()
        params.extend([now, now])

        query = f"""
            INSERT INTO patients ({', '.join(fields)})
            VALUES ({', '.join(placeholders)})
            RETURNING patient_id
        """

        cursor.execute(query, params)
        new_id = cursor.fetchone()[0]
        conn.commit()

        return jsonify({
            "success": True,
            "message": "Patient added successfully",
            "patient_id": new_id
        })

    except Exception as e:
        conn.rollback()
        print(f"Error adding patient: {e}")
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/patients/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    """API endpoint to update a patient's data"""
    # Get request data
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400
    
    # Connect to database
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database connection failed"}), 500
    
    cursor = conn.cursor()
    
    try:
        # First, check if the patient exists
        cursor.execute("SELECT patient_id FROM patients WHERE patient_id = %s", (patient_id,))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({"success": False, "message": "Patient not found"}), 404
        
        # Build update query and parameter list dynamically based on provided fields
        update_fields = []
        params = []
        
        # Define fields that can be updated
        allowed_fields = [
            "first_name", 
            "last_name", 
            "date_of_birth", 
            "gender", 
            "contact_number", 
            "email", 
            "address", 
            "emergency_contact", 
            "emergency_contact_number",
            "blood_type", 
            "rank", 
            "service", 
            "fmpc", 
            "allergies", 
            "medical_conditions"
        ]
        
        # Add updated_at timestamp
        update_fields.append("updated_at = %s")
        params.append(datetime.datetime.now())
        
        # Add fields from request
        for field in allowed_fields:
            if field in data and data[field] is not None:
                update_fields.append(f"{field} = %s")
                params.append(data[field])
        
        # Only proceed if there are fields to update
        if update_fields:
            # Add patient_id to params
            params.append(patient_id)
            
            # Construct and execute update query
            query = f"""
                UPDATE patients 
                SET {", ".join(update_fields)}
                WHERE patient_id = %s
                RETURNING patient_id
            """
            
            cursor.execute(query, params)
            updated_id = cursor.fetchone()[0]
            
            # Commit the transaction
            conn.commit()
            
            return jsonify({
                "success": True,
                "message": "Patient updated successfully",
                "patient_id": updated_id
            })
        else:
            return jsonify({"success": False, "message": "No valid fields to update"}), 400
        
    except Exception as e:
        # Roll back in case of error
        conn.rollback()
        print(f"Error updating patient: {e}")
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8002, debug=True) 