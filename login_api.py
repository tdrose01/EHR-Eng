import os
import sys
import json
import psycopg2
import hashlib
from passlib.hash import bcrypt
import base64
from datetime import datetime
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

def hash_password(password):
    """Hash a password using SHA-256."""
    # This is a simple hash function - production systems should use bcrypt or Argon2
    salt = "ehr_salt"  # A real system would use a unique salt per user
    password_salt = password + salt
    hashed = hashlib.sha256(password_salt.encode()).hexdigest()
    return hashed

def secure_hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hash(password)

def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored hash supporting legacy SHA-256."""
    if stored_hash.startswith('$2a$') or stored_hash.startswith('$2b$'):
        return bcrypt.verify(password, stored_hash)
    return hash_password(password) == stored_hash

@app.route('/api/login', methods=['POST'])
def login():
    """API endpoint to handle user login"""
    # Get JSON data from request
    data = request.json
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"success": False, "message": "Username and password are required"}), 400
    
    username = data['username']
    password = data['password']
    
    # Connect to database
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database connection failed"}), 500
    
    cursor = conn.cursor()
    
    try:
        # Check if user exists and password is correct
        cursor.execute(
            "SELECT id, username, hashed_password FROM users WHERE username = %s",
            (username,)
        )
        user_data = cursor.fetchone()
        
        if not user_data:
            return jsonify({"success": False, "message": "Invalid username or password"}), 401
        
        user_id, db_username, hashed_password = user_data

        # Verify password
        if not verify_password(password, hashed_password):
            # Record failed login attempt
            try:
                cursor.execute(
                    """
                    INSERT INTO login_history (user_id, timestamp, "ipAddress", success)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (user_id, datetime.now(), request.remote_addr, False)
                )
                conn.commit()
            except Exception as e:
                print(f"Error recording failed login: {e}")
            
            return jsonify({"success": False, "message": "Invalid username or password"}), 401
        
        # Login successful, create token
        timestamp = datetime.now().isoformat()
        token = base64.b64encode(f"{username}:{timestamp}".encode()).decode()
        
        # Record successful login
        try:
            cursor.execute(
                """
                INSERT INTO login_history (user_id, timestamp, "ipAddress", success)
                VALUES (%s, %s, %s, %s)
                """,
                (user_id, datetime.now(), request.remote_addr, True)
            )
            conn.commit()
        except Exception as e:
            print(f"Error recording successful login: {e}")
        
        return jsonify({
            "success": True,
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user_id,
                "username": db_username
            }
        })
        
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"success": False, "message": "Server error"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/create_user', methods=['GET', 'POST'])
def create_user():
    """Allow admins to create new users"""
    token = request.headers.get('Authorization') or request.args.get('token')
    if not token:
        return "Unauthorized", 401

    try:
        decoded = base64.b64decode(token).decode()
        requesting_user = decoded.split(':', 1)[0]
    except Exception:
        return "Invalid token", 401

    conn = get_db_connection()
    if not conn:
        return "Database connection failed", 500
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT role FROM users WHERE username = %s", (requesting_user,))
        row = cursor.fetchone()
        if not row or row[0] != 'admin':
            return "Forbidden", 403

        if request.method == 'GET':
            cursor.close()
            conn.close()
            from flask import send_from_directory
            return send_from_directory('.', 'create_user.html')

        data = request.get_json() or request.form
        required = {'username', 'email', 'password', 'role'}
        if not data or not required.issubset(data.keys()):
            return jsonify({"success": False, "message": "Missing fields"}), 400

        new_username = data['username']
        new_email = data['email']
        new_password = data['password']
        new_role = data['role']

        cursor.execute(
            "SELECT id FROM users WHERE username = %s OR email = %s",
            (new_username, new_email)
        )
        if cursor.fetchone():
            return jsonify({"success": False, "message": "Username or email already exists"}), 400

        hashed = secure_hash_password(new_password)
        now = datetime.now()
        cursor.execute(
            """
            INSERT INTO users (username, email, hashed_password, role, created_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            (new_username, new_email, hashed, new_role, now)
        )
        new_id = cursor.fetchone()[0]
        conn.commit()
        return jsonify({"success": True, "user_id": new_id})
    except Exception as e:
        conn.rollback()
        print(f"Create user error: {e}")
        return jsonify({"success": False, "message": "Server error"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/change-password', methods=['POST'])
def change_password():
    """Allow a user to change their password"""
    data = request.json

    required_fields = {'username', 'old_password', 'new_password'}
    if not data or not required_fields.issubset(data):
        return jsonify({"success": False, "message": "Username, old password and new password are required"}), 400

    username = data['username']
    old_password = data['old_password']
    new_password = data['new_password']

    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database connection failed"}), 500

    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT id, hashed_password FROM users WHERE username = %s",
            (username,)
        )
        user = cursor.fetchone()

        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        user_id, current_hash = user
        if not verify_password(old_password, current_hash):
            return jsonify({"success": False, "message": "Current password is incorrect"}), 401

        new_hash = secure_hash_password(new_password)
        cursor.execute(
            "UPDATE users SET hashed_password = %s WHERE id = %s",
            (new_hash, user_id)
        )
        conn.commit()

        return jsonify({"success": True, "message": "Password updated"})

    except Exception as e:
        print(f"Change password error: {e}")
        conn.rollback()
        return jsonify({"success": False, "message": "Server error"}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8001, debug=True) 
