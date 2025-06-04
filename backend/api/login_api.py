import os
import sys
import json
import psycopg2
import hashlib
import base64
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from asgiref.wsgi import WsgiToAsgi

# Get the absolute path to the project root and load environment variables
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(project_root, '.env'))

# Database connection parameters
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'ehr_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Add health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        conn = get_db_connection()
        if conn:
            conn.close()
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'status': 'unhealthy',
                'database': 'disconnected',
                'timestamp': datetime.now().isoformat()
            }), 503
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/health', methods=['GET'])
def api_health_check():
    """API-specific health check endpoint"""
    return health_check()

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
        print(f"Error connecting to PostgreSQL database: {error}")
        return None

def hash_password(password):
    """Hash a password using SHA-256."""
    # This is a simple hash function - production systems should use bcrypt or Argon2
    salt = "ehr_salt"  # A real system would use a unique salt per user
    password_salt = password + salt
    hashed = hashlib.sha256(password_salt.encode()).hexdigest()
    return hashed

@app.route('/api/login', methods=['POST'])
def login():
    """API endpoint to handle user login"""
    # Get JSON data from request
    data = request.json
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"success": False, "message": "Username and password are required"}), 400
    
    username = data['username']
    password = data['password']
    
    # For development, allow test logins
    if os.getenv('ENVIRONMENT') == 'dev':
        if (username == 'testuser' and password == 'password') or (username == 'admin' and password == 'adminpass123'):
            # Create a test token
            timestamp = datetime.now().isoformat()
            token = f"test_token_{int(datetime.now().timestamp() * 1000)}"
            
            return jsonify({
                "success": True,
                "message": "Login successful (Development Mode)",
                "token": token,
                "user": {
                    "id": 1,
                    "username": username,
                    "role": "admin" if username == "admin" else "user"
                }
            })
    
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
        
        # Hash the provided password
        password_hash = hash_password(password)
        
        # Check if password hashes match
        if password_hash != hashed_password:
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

@app.route('/api/verify-token', methods=['GET'])
def verify_token():
    """API endpoint to verify a user's token"""
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "Invalid token format"}), 401
    
    token = auth_header.replace('Bearer ', '')
    
    # Test token check for development
    if token.startswith('test_token_') and os.getenv('ENVIRONMENT') == 'dev':
        try:
            # Extract timestamp and verify it's not expired (1 hour)
            timestamp = int(token.replace('test_token_', ''))
            now = int(datetime.now().timestamp() * 1000)
            if now - timestamp > 3600000:  # 1 hour in milliseconds
                return jsonify({"success": False, "message": "Token expired"}), 401
            
            return jsonify({"success": True, "message": "Token valid"})
        except:
            return jsonify({"success": False, "message": "Invalid token"}), 401
    
    # For real tokens, implement your verification logic here
    
    return jsonify({"success": False, "message": "Token verification not implemented"}), 501

# Create ASGI application
asgi_app = WsgiToAsgi(app)

# Only run the server if this file is run directly
if __name__ == "__main__":
    # Use fixed port 8001 to ensure consistency
    port = 8001
    print(f"Starting login API on port {port}...")
    app.run(host='0.0.0.0', port=port) 