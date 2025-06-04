import os
import sys
import json
import psycopg2
import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from asgiref.wsgi import WsgiToAsgi
import uvicorn

# Get the absolute path to the project root and load environment variables
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
env_path = os.path.join(project_root, '.env')
print(f"Loading environment variables from: {env_path}")
load_dotenv(env_path)

# Database connection parameters
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'ehr_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

print("Database configuration loaded:")
print(f"Host: {DB_CONFIG['host']}")
print(f"Port: {DB_CONFIG['port']}")
print(f"Database: {DB_CONFIG['database']}")
print(f"User: {DB_CONFIG['user']}")
print("Password: [REDACTED]")

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Add health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        print("Starting health check...")
        # Test database connection
        print("Attempting to get database connection...")
        conn = get_db_connection()
        if conn:
            print("Database connection successful, closing connection...")
            conn.close()
            print("Connection closed, returning response...")
            response = jsonify({
                'status': 'healthy',
                'database': 'connected',
                'timestamp': datetime.datetime.now().isoformat()
            })
            print(f"Response prepared: {response.get_data(as_text=True)}")
            return response, 200
        else:
            print("Database connection failed, returning unhealthy response...")
            return jsonify({
                'status': 'unhealthy',
                'database': 'disconnected',
                'timestamp': datetime.datetime.now().isoformat()
            }), 503
    except Exception as e:
        print(f"Error in health check: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        print("Stack trace printed, returning error response...")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.datetime.now().isoformat()
        }), 500

@app.route('/api/health', methods=['GET'])
def api_health_check():
    """API-specific health check endpoint"""
    return health_check()

def get_db_connection():
    """Connect to the PostgreSQL database server"""
    try:
        print(f"Attempting to connect to database with config: {DB_CONFIG}")
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']  # Use the actual password from DB_CONFIG
        )
        print("Successfully established database connection")
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error connecting to PostgreSQL database: {error}")
        print(f"Error type: {type(error)}")
        import traceback
        traceback.print_exc()
        return None

@app.route('/api/patients', methods=['GET'])
def get_patients():
    """API endpoint to retrieve patient data"""
    print("\n=== GET PATIENTS REQUEST STARTED ===")
    # Get query parameters
    search = request.args.get('search', '')
    limit = int(request.args.get('limit', 10))
    offset = int(request.args.get('offset', 0))
    print(f"Query params - search: {search}, limit: {limit}, offset: {offset}")
    
    # Connect to database
    conn = get_db_connection()
    if not conn:
        print("Database connection failed")
        return jsonify({"success": False, "message": "Database connection failed"}), 500
    
    cursor = conn.cursor()
    print("Database connection successful")
    
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
            print("Executing count query...")
            cursor.execute("SELECT COUNT(*) FROM patients")
        
        total_count = cursor.fetchone()[0]
        print(f"Total patients count: {total_count}")
        
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
            print("Executing patient fetch query...")
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
        print(f"Column names: {column_names}")
        patients = []
        
        for row in cursor.fetchall():
            patient = dict(zip(column_names, row))
            
            # Convert date objects to string
            if isinstance(patient['date_of_birth'], (datetime.date, datetime.datetime)):
                patient['date_of_birth'] = patient['date_of_birth'].isoformat()
            
            patients.append(patient)
        
        print(f"Found {len(patients)} patients")
        response = {
            "success": True,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "patients": patients
        }
        print("=== GET PATIENTS REQUEST COMPLETED ===\n")
        return jsonify(response)
        
    except Exception as e:
        print(f"Error fetching patients: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()
        print("Database connection closed")

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

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """API endpoint to retrieve dashboard statistics"""
    print("\n=== DASHBOARD STATS REQUEST STARTED ===")
    # Connect to database
    conn = get_db_connection()
    if not conn:
        print("ERROR: Database connection failed for dashboard stats")
        return jsonify({"success": False, "message": "Database connection failed"}), 500
    
    cursor = conn.cursor()
    
    try:
        stats = {
            "totalPatients": 0,
            "activePatients": 0,
            "appointmentsToday": 0,
            "pendingRecords": 0
        }
        
        print("Attempting to retrieve dashboard statistics...")
        
        # Try to get total patients count
        try:
            print("Querying total patients count...")
            cursor.execute("SELECT COUNT(*) FROM patients")
            stats["totalPatients"] = cursor.fetchone()[0]
            print(f"Total patients count: {stats['totalPatients']}")
            
            # Get active patients count (not marked as inactive)
            print("Querying active patients count...")
            cursor.execute("SELECT COUNT(*) FROM patients WHERE status != 'Inactive' OR status IS NULL")
            stats["activePatients"] = cursor.fetchone()[0]
            print(f"Active patients count: {stats['activePatients']}")
        except psycopg2.Error as e:
            print(f"ERROR fetching patient stats: {e}")
            print(f"Error details: {type(e).__name__}: {str(e)}")
            # Continue with other stats
        
        # Try to get pending records count
        try:
            print("Querying pending records count...")
            cursor.execute("SELECT COUNT(*) FROM records WHERE status = 'Pending' OR status IS NULL")
            stats["pendingRecords"] = cursor.fetchone()[0]
            print(f"Pending records count: {stats['pendingRecords']}")
        except psycopg2.Error as e:
            print(f"ERROR fetching record stats: {e}")
            print(f"Error details: {type(e).__name__}: {str(e)}")
            # Continue with other stats
        
        # Try to get today's appointments
        try:
            print("Querying today's appointments count...")
            cursor.execute("""
                SELECT COUNT(*) FROM appointments 
                WHERE DATE(appointment_date) = CURRENT_DATE
            """)
            stats["appointmentsToday"] = cursor.fetchone()[0]
            print(f"Today's appointments count: {stats['appointmentsToday']}")
        except psycopg2.Error as e:
            print(f"ERROR fetching appointment stats: {e}")
            print(f"Error details: {type(e).__name__}: {str(e)}")
            # Continue with other stats
        
        print("Dashboard stats collected successfully:")
        print(f"Final stats: {stats}")
        print("=== DASHBOARD STATS REQUEST COMPLETED ===\n")
        
        return jsonify({
            "success": True,
            "stats": stats
        })
        
    except Exception as e:
        print(f"CRITICAL ERROR in dashboard stats: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        print("=== DASHBOARD STATS REQUEST FAILED ===\n")
        
        return jsonify({
            "success": True,
            "stats": {
                "totalPatients": 0,
                "activePatients": 0,
                "appointmentsToday": 0,
                "pendingRecords": 0
            }
        })
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

# Add POST route for creating patients
@app.route('/api/patients', methods=['POST'])
def create_patient():
    """API endpoint to create a new patient"""
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
        # Define required fields
        required_fields = ["first_name", "last_name", "date_of_birth"]
        
        # Check if required fields are present
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == '':
                return jsonify({
                    "success": False,
                    "message": f"Missing required field: {field}"
                }), 400
        
        # Define fields that can be inserted
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
        
        # Build insert query and parameters
        fields = []
        placeholders = []
        params = []
        
        # Add created_at and updated_at timestamps
        now = datetime.datetime.now()
        fields.extend(["created_at", "updated_at"])
        placeholders.extend(["%s", "%s"])
        params.extend([now, now])
        
        # Add fields from request
        for field in allowed_fields:
            if field in data and data[field] is not None:
                fields.append(field)
                placeholders.append("%s")
                params.append(data[field])
        
        # Construct and execute insert query
        query = f"""
            INSERT INTO patients ({", ".join(fields)})
            VALUES ({", ".join(placeholders)})
            RETURNING patient_id
        """
        
        cursor.execute(query, params)
        new_id = cursor.fetchone()[0]
        
        # Commit the transaction
        conn.commit()
        
        return jsonify({
            "success": True,
            "message": "Patient created successfully",
            "patient_id": new_id
        })
        
    except Exception as e:
        # Roll back in case of error
        conn.rollback()
        print(f"Error creating patient: {e}")
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

# Add DELETE route for deleting patients
@app.route('/api/patients/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    """API endpoint to delete a patient"""
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
        
        # Delete the patient
        cursor.execute("DELETE FROM patients WHERE patient_id = %s", (patient_id,))
        
        # Commit the transaction
        conn.commit()
        
        return jsonify({
            "success": True,
            "message": "Patient deleted successfully"
        })
        
    except Exception as e:
        # Roll back in case of error
        conn.rollback()
        print(f"Error deleting patient: {e}")
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

# Create ASGI application
asgi_app = WsgiToAsgi(app)

if __name__ == "__main__":
    # Run the server if executed directly
    # uvicorn.run(asgi_app, host="0.0.0.0", port=8002, reload=True)
    app.run(host="0.0.0.0", port=8002, debug=False) 