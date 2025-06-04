import os
import sys
import json
import psycopg2
import datetime
from datetime import timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from asgiref.wsgi import WsgiToAsgi
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Get the absolute path to the project root and load environment variables
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
env_path = os.path.join(project_root, '.env')
logger.info(f"Loading environment variables from: {env_path}")
load_dotenv(env_path)

# Database connection parameters
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'ehr_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

logger.info("Records API - Database configuration loaded:")
logger.info(f"Host: {DB_CONFIG['host']}")
logger.info(f"Port: {DB_CONFIG['port']}")
logger.info(f"Database: {DB_CONFIG['database']}")
logger.info(f"User: {DB_CONFIG['user']}")
logger.info("Password: [REDACTED]")

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Add health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        logger.info("Starting health check...")
        # Test database connection
        logger.debug("Attempting to get database connection...")
        conn = get_db_connection()
        if conn:
            logger.info("Database connection successful")
            
            # Test if required tables exist
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'records'
                    )
                """)
                records_table_exists = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'patients'
                    )
                """)
                patients_table_exists = cursor.fetchone()[0]
                
                logger.info(f"Tables exist - records: {records_table_exists}, patients: {patients_table_exists}")
                
                response = {
                    'status': 'healthy',
                    'database': 'connected',
                    'tables': {
                        'records': records_table_exists,
                        'patients': patients_table_exists
                    },
                    'timestamp': datetime.datetime.now().isoformat()
                }
                
                if not (records_table_exists and patients_table_exists):
                    response['status'] = 'warning'
                    response['message'] = 'Some required tables are missing'
                    return jsonify(response), 503
                
                return jsonify(response), 200
                
            finally:
                cursor.close()
                conn.close()
                logger.info("Database connection closed")
        else:
            logger.error("Database connection failed")
            return jsonify({
                'status': 'unhealthy',
                'database': 'disconnected',
                'timestamp': datetime.datetime.now().isoformat()
            }), 503
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(traceback.format_exc())
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
        logger.debug(f"Attempting to connect to database with config: {DB_CONFIG}")
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        logger.info("Successfully established database connection")
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f"Error connecting to PostgreSQL database: {error}")
        logger.error(f"Error type: {type(error)}")
        import traceback
        logger.error(traceback.format_exc())
        return None

@app.route('/api/records', methods=['GET'])
def get_records():
    """Get all records"""
    logger.info("Received request to get all records")
    conn = get_db_connection()
    if not conn:
        logger.error("Failed to establish database connection in get_records")
        return jsonify({"success": False, "message": "Database connection failed"}), 503

    try:
        cursor = conn.cursor()
        logger.debug("Executing query to fetch all records")
        cursor.execute("""
            SELECT r.*, p.first_name, p.last_name 
            FROM records r 
            JOIN patients p ON r.patient_id = p.id
            ORDER BY r.created_at DESC
        """)
        records = cursor.fetchall()
        logger.info(f"Successfully fetched {len(records)} records")

        # Convert records to list of dictionaries
        records_list = []
        for record in records:
            record_dict = {
                'id': record[0],
                'patient_id': record[1],
                'diagnosis': record[2],
                'prescription': record[3],
                'notes': record[4],
                'created_at': record[5].isoformat() if record[5] else None,
                'updated_at': record[6].isoformat() if record[6] else None,
                'patient_name': f"{record[7]} {record[8]}"
            }
            records_list.append(record_dict)

        return jsonify({"success": True, "records": records_list}), 200

    except psycopg2.Error as e:
        logger.error(f"Database error in get_records: {str(e)}")
        logger.error(f"Error code: {e.pgcode}")
        logger.error(f"Error details: {e.diag.message_detail if e.diag else 'No details available'}")
        return jsonify({"success": False, "message": "Database error occurred"}), 500
    except Exception as e:
        logger.error(f"Error fetching records: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            logger.debug("Database connection closed in get_records")

@app.route('/api/records/<int:record_id>', methods=['GET'])
def get_record(record_id):
    """Get a specific record by ID"""
    logger.info(f"Received request to get record with ID: {record_id}")
    conn = get_db_connection()
    if not conn:
        logger.error(f"Failed to establish database connection in get_record for ID: {record_id}")
        return jsonify({"success": False, "message": "Database connection failed"}), 503

    try:
        cursor = conn.cursor()
        logger.debug(f"Executing query to fetch record {record_id}")
        cursor.execute("""
            SELECT r.*, p.first_name, p.last_name 
            FROM records r 
            JOIN patients p ON r.patient_id = p.id 
            WHERE r.id = %s
        """, (record_id,))
        record = cursor.fetchone()

        if record is None:
            logger.warning(f"Record not found with ID: {record_id}")
            return jsonify({"success": False, "message": "Record not found"}), 404

        logger.info(f"Successfully fetched record {record_id}")
        record_dict = {
            'id': record[0],
            'patient_id': record[1],
            'diagnosis': record[2],
            'prescription': record[3],
            'notes': record[4],
            'created_at': record[5].isoformat() if record[5] else None,
            'updated_at': record[6].isoformat() if record[6] else None,
            'patient_name': f"{record[7]} {record[8]}"
        }
        return jsonify({"success": True, "record": record_dict}), 200

    except psycopg2.Error as e:
        logger.error(f"Database error in get_record: {str(e)}")
        logger.error(f"Error code: {e.pgcode}")
        logger.error(f"Error details: {e.diag.message_detail if e.diag else 'No details available'}")
        return jsonify({"success": False, "message": "Database error occurred"}), 500
    except Exception as e:
        logger.error(f"Error fetching record: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            logger.debug(f"Database connection closed in get_record for ID: {record_id}")

@app.route('/api/records', methods=['POST'])
def create_record():
    """Create a new record"""
    logger.info("Received request to create new record")
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['patient_id', 'diagnosis', 'prescription']
    for field in required_fields:
        if field not in data:
            logger.warning(f"Missing required field in create_record: {field}")
            return jsonify({"success": False, "message": f"Missing required field: {field}"}), 400

    conn = get_db_connection()
    if not conn:
        logger.error("Failed to establish database connection in create_record")
        return jsonify({"success": False, "message": "Database connection failed"}), 503

    try:
        cursor = conn.cursor()
        
        # Verify patient exists
        logger.debug(f"Verifying patient exists with ID: {data['patient_id']}")
        cursor.execute("SELECT id FROM patients WHERE id = %s", (data['patient_id'],))
        if not cursor.fetchone():
            logger.warning(f"Patient not found with ID: {data['patient_id']}")
            return jsonify({"success": False, "message": "Patient not found"}), 404

        # Create record
        logger.debug("Executing query to create new record")
        cursor.execute("""
            INSERT INTO records (patient_id, diagnosis, prescription, notes)
            VALUES (%s, %s, %s, %s)
            RETURNING id, created_at, updated_at
        """, (
            data['patient_id'],
            data['diagnosis'],
            data['prescription'],
            data.get('notes', '')
        ))
        
        new_record = cursor.fetchone()
        conn.commit()
        logger.info(f"Successfully created record with ID: {new_record[0]}")

        return jsonify({
            "success": True,
            "message": "Record created successfully",
            "record": {
                "id": new_record[0],
                "patient_id": data['patient_id'],
                "diagnosis": data['diagnosis'],
                "prescription": data['prescription'],
                "notes": data.get('notes', ''),
                "created_at": new_record[1].isoformat(),
                "updated_at": new_record[2].isoformat() if new_record[2] else None
            }
        }), 201

    except psycopg2.Error as e:
        conn.rollback()
        logger.error(f"Database error in create_record: {str(e)}")
        logger.error(f"Error code: {e.pgcode}")
        logger.error(f"Error details: {e.diag.message_detail if e.diag else 'No details available'}")
        return jsonify({"success": False, "message": "Database error occurred"}), 500
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating record: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            logger.debug("Database connection closed in create_record")

@app.route('/api/records/<int:record_id>', methods=['PUT'])
def update_record(record_id):
    """Update an existing record"""
    logger.info(f"Received request to update record with ID: {record_id}")
    data = request.get_json()
    
    # Validate that at least one field is being updated
    updateable_fields = ['patient_id', 'diagnosis', 'prescription', 'notes']
    update_data = {k: v for k, v in data.items() if k in updateable_fields}
    
    if not update_data:
        logger.warning("No valid fields provided for update")
        return jsonify({
            "success": False,
            "message": "No valid fields provided for update"
        }), 400

    conn = get_db_connection()
    if not conn:
        logger.error(f"Failed to establish database connection in update_record for ID: {record_id}")
        return jsonify({"success": False, "message": "Database connection failed"}), 503

    try:
        cursor = conn.cursor()
        
        # Check if record exists
        logger.debug(f"Verifying record exists with ID: {record_id}")
        cursor.execute("SELECT id FROM records WHERE id = %s", (record_id,))
        if not cursor.fetchone():
            logger.warning(f"Record not found with ID: {record_id}")
            return jsonify({"success": False, "message": "Record not found"}), 404
            
        # If patient_id is being updated, verify the new patient exists
        if 'patient_id' in update_data:
            logger.debug(f"Verifying new patient exists with ID: {update_data['patient_id']}")
            cursor.execute("SELECT id FROM patients WHERE id = %s", (update_data['patient_id'],))
            if not cursor.fetchone():
                logger.warning(f"Patient not found with ID: {update_data['patient_id']}")
                return jsonify({"success": False, "message": "New patient not found"}), 404

        # Build update query
        set_clause = ", ".join([f"{k} = %s" for k in update_data.keys()])
        query = f"""
            UPDATE records 
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP 
            WHERE id = %s 
            RETURNING id, patient_id, diagnosis, prescription, notes, created_at, updated_at
        """
        
        # Execute update query
        logger.debug(f"Executing update query for record {record_id}")
        params = list(update_data.values()) + [record_id]
        cursor.execute(query, params)
        
        if cursor.rowcount == 0:
            logger.error(f"No rows affected when updating record {record_id}")
            return jsonify({"success": False, "message": "Update failed"}), 500
            
        updated_record = cursor.fetchone()
        conn.commit()
        logger.info(f"Successfully updated record {record_id}")

        # Get patient name for the updated record
        cursor.execute("""
            SELECT first_name, last_name 
            FROM patients 
            WHERE id = %s
        """, (updated_record[1],))
        patient = cursor.fetchone()
        
        return jsonify({
            "success": True,
            "message": "Record updated successfully",
            "record": {
                "id": updated_record[0],
                "patient_id": updated_record[1],
                "diagnosis": updated_record[2],
                "prescription": updated_record[3],
                "notes": updated_record[4],
                "created_at": updated_record[5].isoformat(),
                "updated_at": updated_record[6].isoformat(),
                "patient_name": f"{patient[0]} {patient[1]}" if patient else None
            }
        }), 200

    except psycopg2.Error as e:
        conn.rollback()
        logger.error(f"Database error in update_record: {str(e)}")
        logger.error(f"Error code: {e.pgcode}")
        logger.error(f"Error details: {e.diag.message_detail if e.diag else 'No details available'}")
        return jsonify({"success": False, "message": "Database error occurred"}), 500
    except Exception as e:
        conn.rollback()
        logger.error(f"Error updating record: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            logger.debug(f"Database connection closed in update_record for ID: {record_id}")

@app.route('/api/records/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    """Delete a record"""
    logger.info(f"Received request to delete record with ID: {record_id}")
    conn = get_db_connection()
    if not conn:
        logger.error(f"Failed to establish database connection in delete_record for ID: {record_id}")
        return jsonify({"success": False, "message": "Database connection failed"}), 503

    try:
        cursor = conn.cursor()
        
        # Check if record exists
        logger.debug(f"Verifying record exists with ID: {record_id}")
        cursor.execute("SELECT id FROM records WHERE id = %s", (record_id,))
        if not cursor.fetchone():
            logger.warning(f"Record not found with ID: {record_id}")
            return jsonify({"success": False, "message": "Record not found"}), 404

        # Delete the record
        logger.debug(f"Executing delete query for record {record_id}")
        cursor.execute("DELETE FROM records WHERE id = %s", (record_id,))
        
        if cursor.rowcount == 0:
            logger.error(f"No rows affected when deleting record {record_id}")
            return jsonify({"success": False, "message": "Delete failed"}), 500
            
        conn.commit()
        logger.info(f"Successfully deleted record {record_id}")
        
        return jsonify({
            "success": True,
            "message": "Record deleted successfully"
        }), 200

    except psycopg2.Error as e:
        conn.rollback()
        logger.error(f"Database error in delete_record: {str(e)}")
        logger.error(f"Error code: {e.pgcode}")
        logger.error(f"Error details: {e.diag.message_detail if e.diag else 'No details available'}")
        return jsonify({"success": False, "message": "Database error occurred"}), 500
    except Exception as e:
        conn.rollback()
        logger.error(f"Error deleting record: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            logger.debug(f"Database connection closed in delete_record for ID: {record_id}")

# Patient-specific records route
@app.route('/api/patients/<int:patient_id>/records', methods=['GET'])
def get_patient_records(patient_id):
    """Get all records for a specific patient"""
    logger.info(f"Received request to get records for patient with ID: {patient_id}")
    conn = get_db_connection()
    if not conn:
        logger.error(f"Failed to establish database connection in get_patient_records for patient ID: {patient_id}")
        return jsonify({"success": False, "message": "Database connection failed"}), 503

    try:
        cursor = conn.cursor()
        
        # Check if patient exists
        logger.debug(f"Verifying patient exists with ID: {patient_id}")
        cursor.execute("""
            SELECT first_name, last_name 
            FROM patients 
            WHERE id = %s
        """, (patient_id,))
        patient = cursor.fetchone()
        
        if not patient:
            logger.warning(f"Patient not found with ID: {patient_id}")
            return jsonify({"success": False, "message": "Patient not found"}), 404

        # Get all records for the patient
        logger.debug(f"Fetching records for patient {patient_id}")
        cursor.execute("""
            SELECT id, patient_id, diagnosis, prescription, notes, created_at, updated_at
            FROM records 
            WHERE patient_id = %s 
            ORDER BY created_at DESC
        """, (patient_id,))
        
        records = cursor.fetchall()
        logger.info(f"Successfully fetched {len(records)} records for patient {patient_id}")

        records_list = []
        for record in records:
            record_dict = {
                'id': record[0],
                'patient_id': record[1],
                'diagnosis': record[2],
                'prescription': record[3],
                'notes': record[4],
                'created_at': record[5].isoformat() if record[5] else None,
                'updated_at': record[6].isoformat() if record[6] else None,
                'patient_name': f"{patient[0]} {patient[1]}"
            }
            records_list.append(record_dict)

        return jsonify({
            "success": True,
            "patient_name": f"{patient[0]} {patient[1]}",
            "records": records_list
        }), 200

    except psycopg2.Error as e:
        logger.error(f"Database error in get_patient_records: {str(e)}")
        logger.error(f"Error code: {e.pgcode}")
        logger.error(f"Error details: {e.diag.message_detail if e.diag else 'No details available'}")
        return jsonify({"success": False, "message": "Database error occurred"}), 500
    except Exception as e:
        logger.error(f"Error fetching patient records: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            logger.debug(f"Database connection closed in get_patient_records for patient ID: {patient_id}")

# Create ASGI application
if __name__ == "__main__":
    # Use fixed port 8003 to ensure consistency
    port = 8003
    logger.info(f"Starting server on port {port}...")
    asgi_app = WsgiToAsgi(app)
    uvicorn.run(asgi_app, host="0.0.0.0", port=port) 
