import os
import sys
import psycopg2
import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('ehr-project/backend/.env')

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'ehr_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

app = Flask(__name__)
CORS(app)


def get_db_connection():
    """Create a database connection."""
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None


@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    """Return a list of appointments."""
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))

    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500

    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT a.id, a.appointment_time, a.reason, a.status,
                   COALESCE(p.last_name || ', ' || p.first_name, '') AS patient,
                   COALESCE(u.full_name, u.username) AS provider
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.id
            LEFT JOIN users u ON a.provider_id = u.id
            ORDER BY a.appointment_time DESC
            LIMIT %s OFFSET %s
            """,
            (limit, offset)
        )
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        appointments = []
        for row in rows:
            record = dict(zip(columns, row))
            for k, v in record.items():
                if isinstance(v, (datetime.date, datetime.datetime)):
                    record[k] = v.isoformat()
            appointments.append(record)
        return jsonify({'success': True, 'appointments': appointments})
    except Exception as e:
        print(f"Error fetching appointments: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cur.close()
        conn.close()


@app.route('/api/appointments/<int:appt_id>', methods=['GET'])
def get_appointment(appt_id):
    """Return a specific appointment."""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT a.id, a.appointment_time, a.reason, a.status,
                   a.patient_id, a.provider_id,
                   COALESCE(p.last_name || ', ' || p.first_name, '') AS patient,
                   COALESCE(u.full_name, u.username) AS provider
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.id
            LEFT JOIN users u ON a.provider_id = u.id
            WHERE a.id = %s
            """,
            (appt_id,)
        )
        row = cur.fetchone()
        if not row:
            return jsonify({'success': False, 'message': 'Appointment not found'}), 404
        columns = [desc[0] for desc in cur.description]
        appt = dict(zip(columns, row))
        for k, v in appt.items():
            if isinstance(v, (datetime.date, datetime.datetime)):
                appt[k] = v.isoformat()
        return jsonify({'success': True, 'appointment': appt})
    except Exception as e:
        print(f"Error fetching appointment: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cur.close()
        conn.close()


@app.route('/api/appointments', methods=['POST'])
def create_appointment():
    """Create a new appointment."""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO appointments (patient_id, provider_id, appointment_time, reason, status, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
            RETURNING id
            """,
            (
                data.get('patient_id'),
                data.get('provider_id'),
                data.get('appointment_time'),
                data.get('reason'),
                data.get('status', 'Scheduled')
            )
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        return jsonify({'success': True, 'appointment_id': new_id})
    except Exception as e:
        conn.rollback()
        print(f"Error creating appointment: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cur.close()
        conn.close()


@app.route('/api/appointments/<int:appt_id>', methods=['PUT'])
def update_appointment(appt_id):
    """Update an appointment."""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM appointments WHERE id = %s", (appt_id,))
        if not cur.fetchone():
            return jsonify({'success': False, 'message': 'Appointment not found'}), 404

        fields = []
        params = []
        allowed = ['patient_id', 'provider_id', 'appointment_time', 'reason', 'status']
        for key in allowed:
            if key in data:
                fields.append(f"{key} = %s")
                params.append(data[key])
        fields.append("updated_at = NOW()")
        params.append(appt_id)

        cur.execute(
            f"UPDATE appointments SET {', '.join(fields)} WHERE id = %s RETURNING id",
            params
        )
        cur.fetchone()
        conn.commit()
        return jsonify({'success': True, 'message': 'Appointment updated'})
    except Exception as e:
        conn.rollback()
        print(f"Error updating appointment: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cur.close()
        conn.close()


@app.route('/api/appointments/<int:appt_id>', methods=['DELETE'])
def delete_appointment(appt_id):
    """Delete an appointment."""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM appointments WHERE id = %s RETURNING id", (appt_id,))
        row = cur.fetchone()
        if not row:
            return jsonify({'success': False, 'message': 'Appointment not found'}), 404
        conn.commit()
        return jsonify({'success': True, 'message': 'Appointment deleted'})
    except Exception as e:
        conn.rollback()
        print(f"Error deleting appointment: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8003, debug=True)
