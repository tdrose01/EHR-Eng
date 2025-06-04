#!/usr/bin/env python3
"""
Vaccine API endpoints for the health record system.
Provides access to vaccine schedules and next dose date calculation.
"""

import os
import json
import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from uvicorn.middleware.wsgi import WSGIMiddleware as WsgiToAsgi

# Create Flask app
app = Flask(__name__)
CORS(app)

def get_db_connection():
    """Create a connection to the PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            port=os.environ.get('DB_PORT', '5432'),
            dbname=os.environ.get('DB_NAME', 'healthrecords'),
            user=os.environ.get('DB_USER', 'postgres'),
            password=os.environ.get('DB_PASSWORD', 'postgres')
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

@app.route('/api/vaccines/schedules', methods=['GET'])
def get_vaccine_schedules():
    """API endpoint to get vaccine schedules for a specific vaccine"""
    # Get query parameters
    vaccine_name = request.args.get('vaccine')
    brand_name = request.args.get('brand')
    manufacturer = request.args.get('manufacturer')
    
    if not vaccine_name:
        return jsonify({"success": False, "message": "Vaccine name is required"}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database connection failed"}), 500
    
    # Use RealDictCursor to get results as dictionaries
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Call the get_vaccine_schedule function
        query = "SELECT * FROM get_vaccine_schedule(%s, %s, %s)"
        cursor.execute(query, [vaccine_name, brand_name, manufacturer])
        
        schedules = cursor.fetchall()
        
        # Convert date/datetime objects to string
        for schedule in schedules:
            for key, value in schedule.items():
                if isinstance(value, (datetime.date, datetime.datetime)):
                    schedule[key] = value.isoformat()
        
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

@app.route('/api/vaccines/alternative-schedules', methods=['GET'])
def get_alternative_schedules():
    """API endpoint to get alternative schedules for a specific vaccine dose"""
    # Get query parameters
    vaccine_name = request.args.get('vaccine')
    brand_name = request.args.get('brand')
    manufacturer = request.args.get('manufacturer')
    dose_number = request.args.get('doseNumber')
    
    # Validate required parameters
    if not all([vaccine_name, brand_name, manufacturer, dose_number]):
        return jsonify({
            "success": False, 
            "message": "Required parameters: vaccine, brand, manufacturer, doseNumber"
        }), 400
    
    try:
        dose_number = int(dose_number)
    except ValueError:
        return jsonify({"success": False, "message": "doseNumber must be an integer"}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database connection failed"}), 500
    
    # Use RealDictCursor to get results as dictionaries
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Call the function to get alternative schedules
        query = "SELECT * FROM get_vaccine_alternative_schedules(%s, %s, %s, %s)"
        cursor.execute(query, [vaccine_name, brand_name, manufacturer, dose_number])
        
        alternatives = cursor.fetchall()
        
        return jsonify({
            "success": True,
            "alternatives": alternatives,
            "hasAlternatives": len(alternatives) > 1
        })
    
    except Exception as e:
        print(f"Error fetching alternative schedules: {e}")
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/vaccines/next-dose', methods=['GET'])
def calculate_next_dose():
    """API endpoint to calculate the next dose date for a vaccine"""
    # Get query parameters
    vaccine_name = request.args.get('vaccine')
    brand_name = request.args.get('brand')
    manufacturer = request.args.get('manufacturer')
    dose_number = request.args.get('doseNumber')
    administration_date = request.args.get('date')
    patient_id = request.args.get('patientId')
    custom_interval_weeks = request.args.get('intervalWeeks')  # Optional: allow custom interval
    
    # Validate required parameters
    if not all([vaccine_name, brand_name, manufacturer, dose_number, administration_date, patient_id]):
        return jsonify({
            "success": False, 
            "message": "Required parameters: vaccine, brand, manufacturer, doseNumber, date, patientId"
        }), 400
    
    try:
        # Parse inputs
        dose_number = int(dose_number)
        administration_date = datetime.datetime.fromisoformat(administration_date).date()
        if custom_interval_weeks:
            custom_interval_weeks = int(custom_interval_weeks)
    except ValueError as e:
        return jsonify({"success": False, "message": f"Invalid parameter format: {str(e)}"}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database connection failed"}), 500
    
    cursor = conn.cursor()
    
    try:
        # Get patient birthdate
        cursor.execute("SELECT birth_date FROM patients WHERE patient_id = %s", [patient_id])
        result = cursor.fetchone()
        
        if not result:
            return jsonify({"success": False, "message": "Patient not found"}), 404
            
        patient_birthdate = result[0]
        
        next_dose_date = None
        
        # If custom interval is provided, calculate based on that
        if custom_interval_weeks is not None:
            next_dose_date = administration_date + datetime.timedelta(weeks=custom_interval_weeks)
        else:
            # Otherwise use the standard function
            cursor.execute(
                "SELECT calculate_next_dose_date(%s, %s, %s, %s, %s, %s)",
                [vaccine_name, brand_name, manufacturer, dose_number, administration_date, patient_birthdate]
            )
            next_dose_date = cursor.fetchone()[0]
        
        if next_dose_date:
            next_dose_date = next_dose_date.isoformat()
        
        return jsonify({
            "success": True,
            "nextDoseDate": next_dose_date,
            "vaccine": {
                "name": vaccine_name,
                "brand": brand_name,
                "manufacturer": manufacturer,
                "doseNumber": dose_number,
                "currentDoseDate": administration_date.isoformat()
            },
            "customIntervalUsed": custom_interval_weeks is not None
        })
    
    except Exception as e:
        print(f"Error calculating next dose date: {e}")
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/vaccines/cvx-code', methods=['GET'])
def get_cvx_code():
    """API endpoint to retrieve a CVX code for a given vaccine name"""
    vaccine_name = request.args.get('vaccineName')
    
    if not vaccine_name:
        return jsonify({"success": False, "message": "Vaccine name is required"}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database connection failed"}), 500
    
    cursor = conn.cursor()
    
    try:
        # Call the get_cvx_code function
        cursor.execute("SELECT get_cvx_code(%s)", [vaccine_name])
        cvx_code = cursor.fetchone()[0]
        
        # If a code was found, get full details
        if cvx_code:
            cursor.execute(
                "SELECT * FROM cvx_codes WHERE cvx_code = %s", 
                [cvx_code]
            )
            columns = [desc[0] for desc in cursor.description]
            cvx_details = dict(zip(columns, cursor.fetchone()))
            
            return jsonify({
                "success": True,
                "cvxCode": cvx_code,
                "vaccineName": vaccine_name,
                "details": cvx_details
            })
        else:
            return jsonify({
                "success": True,
                "cvxCode": None,
                "vaccineName": vaccine_name,
                "message": "No matching CVX code found"
            })
    
    except Exception as e:
        print(f"Error fetching CVX code: {e}")
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/vaccines/available', methods=['GET'])
def get_available_vaccines():
    """API endpoint to get a list of available vaccines in the system"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database connection failed"}), 500
    
    # Use RealDictCursor to get results as dictionaries
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Get distinct vaccines from the vaccine_schedules table with CVX codes
        query = """
            SELECT DISTINCT 
                vs.vaccine_name, 
                vs.brand_name, 
                vs.manufacturer,
                MAX(vc.cvx_code) as cvx_code
            FROM vaccine_schedules vs
            LEFT JOIN cvx_codes vc ON vs.vaccine_name LIKE '%' || vc.vaccine_name || '%'
                OR vc.vaccine_name LIKE '%' || vs.vaccine_name || '%'
            GROUP BY vs.vaccine_name, vs.brand_name, vs.manufacturer
            ORDER BY vs.vaccine_name, vs.brand_name
        """
        cursor.execute(query)
        
        vaccines = []
        for row in cursor.fetchall():
            # Get total doses for this vaccine
            cursor.execute(
                "SELECT MAX(dose_number) FROM vaccine_schedules WHERE vaccine_name = %s AND brand_name = %s AND manufacturer = %s",
                [row['vaccine_name'], row['brand_name'], row['manufacturer']]
            )
            total_doses = cursor.fetchone()[0]
            
            # Check if this vaccine has alternative schedules
            has_alternatives = False
            if total_doses > 1:
                cursor.execute(
                    "SELECT COUNT(*) FROM get_vaccine_alternative_schedules(%s, %s, %s, %s)",
                    [row['vaccine_name'], row['brand_name'], row['manufacturer'], 2]
                )
                alt_count = cursor.fetchone()[0]
                has_alternatives = alt_count > 1
            
            # If no CVX code found via the join, try to get it from the function
            if not row['cvx_code']:
                cursor.execute("SELECT get_cvx_code(%s)", [row['vaccine_name']])
                row['cvx_code'] = cursor.fetchone()[0]
                
            vaccines.append({
                "vaccineName": row['vaccine_name'],
                "brandName": row['brand_name'],
                "manufacturer": row['manufacturer'],
                "totalDoses": total_doses,
                "hasAlternativeSchedules": has_alternatives,
                "cvxCode": row['cvx_code']
            })
        
        return jsonify({
            "success": True,
            "vaccines": vaccines
        })
    
    except Exception as e:
        print(f"Error fetching available vaccines: {e}")
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/vaccines/dose-by-age', methods=['GET'])
def get_dose_by_age():
    """API endpoint to get the appropriate dose amount for a vaccine based on patient age"""
    # Get query parameters
    vaccine_name = request.args.get('vaccine')
    brand_name = request.args.get('brand')
    manufacturer = request.args.get('manufacturer')
    patient_id = request.args.get('patientId')
    administration_date = request.args.get('date', datetime.datetime.now().isoformat())
    
    # Validate required parameters
    if not all([vaccine_name, brand_name, manufacturer, patient_id]):
        return jsonify({
            "success": False, 
            "message": "Required parameters: vaccine, brand, manufacturer, patientId"
        }), 400
    
    try:
        administration_date = datetime.datetime.fromisoformat(administration_date).date()
    except ValueError as e:
        return jsonify({"success": False, "message": f"Invalid date format: {str(e)}"}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database connection failed"}), 500
    
    # Use RealDictCursor to get results as dictionaries
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Get patient birthdate
        cursor.execute("SELECT birth_date FROM patients WHERE patient_id = %s", [patient_id])
        result = cursor.fetchone()
        
        if not result:
            return jsonify({"success": False, "message": "Patient not found"}), 404
            
        patient_birthdate = result['birth_date']
        
        # Call the function to get dose information
        query = "SELECT * FROM get_vaccine_dose_by_age(%s, %s, %s, %s, %s)"
        cursor.execute(query, [
            vaccine_name, 
            brand_name, 
            manufacturer, 
            patient_birthdate,
            administration_date
        ])
        
        dose_info = cursor.fetchone()
        
        if not dose_info:
            return jsonify({
                "success": False, 
                "message": "No dose information found for this vaccine and patient age"
            }), 404
        
        # Calculate patient age for reference
        patient_age_years = (administration_date - patient_birthdate).days / 365.25
        
        return jsonify({
            "success": True,
            "doseInfo": dose_info,
            "patientAge": round(patient_age_years, 1)
        })
    
    except Exception as e:
        print(f"Error fetching dose information: {e}")
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/patients', methods=['GET'])
def get_patients():
    """API endpoint to get all patients"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database connection failed"}), 500
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("""
            SELECT patient_id, first_name, last_name, birth_date, gender, 
                   address, phone, email 
            FROM patients
        """)
        patients = cursor.fetchall()
        
        # Convert date objects to string
        for patient in patients:
            if patient['birth_date']:
                patient['birth_date'] = patient['birth_date'].isoformat()
        
        return jsonify(patients)
    except Exception as e:
        print(f"Error fetching patients: {e}")
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/patients', methods=['POST'])
def create_patient():
    """API endpoint to create a new patient"""
    data = request.json
    
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400
    
    required_fields = ['firstName', 'lastName', 'dateOfBirth', 'gender']
    if not all(field in data for field in required_fields):
        return jsonify({
            "success": False, 
            "message": f"Required fields: {', '.join(required_fields)}"
        }), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database connection failed"}), 500
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("""
            INSERT INTO patients (
                first_name, last_name, birth_date, gender, 
                address, phone, email
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s
            ) RETURNING *
        """, [
            data['firstName'],
            data['lastName'],
            data['dateOfBirth'],
            data['gender'],
            data.get('address'),
            data.get('phone'),
            data.get('email')
        ])
        
        conn.commit()
        patient = cursor.fetchone()
        
        # Convert date objects to string
        if patient['birth_date']:
            patient['birth_date'] = patient['birth_date'].isoformat()
        
        return jsonify({
            "success": True,
            "patient": patient
        })
    except Exception as e:
        conn.rollback()
        print(f"Error creating patient: {e}")
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

# Create ASGI application
asgi_app = WsgiToAsgi(app)

# Only run the server if this file is run directly
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8004) 