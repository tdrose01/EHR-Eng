import os
import sys
import psycopg2
import hashlib
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('ehr-project/backend/.env')

# Database connection parameters
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'ehr_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

def get_db_connection():
    """Connect to the PostgreSQL database server"""
    conn = None
    try:
        # Connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        print(f"Host: {DB_CONFIG['host']}")
        print(f"Port: {DB_CONFIG['port']}")
        print(f"Database: {DB_CONFIG['database']}")
        print(f"User: {DB_CONFIG['user']}")
        
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        
        print("Database connection successful!")
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        if conn is not None:
            conn.close()
        sys.exit(1)

def hash_password(password):
    """Hash a password using SHA-256."""
    # This is a simple hash function - production systems should use bcrypt or Argon2
    salt = "ehr_salt"  # A real system would use a unique salt per user
    password_salt = password + salt
    hashed = hashlib.sha256(password_salt.encode()).hexdigest()
    return hashed

def create_test_user(username, password, delete_existing=False):
    """Create a test user for login testing"""
    print(f"Creating test user: {username}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if user and delete_existing:
            print(f"Deleting existing user {username}...")
            user_id = user[0]
            
            # Delete login history first
            cursor.execute("DELETE FROM login_history WHERE user_id = %s", (user_id,))
            
            # Delete user
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            print(f"User {username} deleted.")
        elif user:
            print(f"User {username} already exists with ID: {user[0]}")
            
            # Update password
            hashed_password = hash_password(password)
            now = datetime.now()
            
            cursor.execute("""
                UPDATE users 
                SET hashed_password = %s, updated_at = %s 
                WHERE username = %s
                RETURNING id
            """, (hashed_password, now, username))
            
            user_id = cursor.fetchone()[0]
            conn.commit()
            
            print(f"Password updated for user {username} (ID: {user_id})")
            print(f"Password hash: {hashed_password}")
            return user_id
        
        # Create new user
        hashed_password = hash_password(password)
        now = datetime.now()
        
        cursor.execute("""
            INSERT INTO users (username, hashed_password, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (username, hashed_password, True, now, now))
        
        user_id = cursor.fetchone()[0]
        conn.commit()
        
        print(f"Created user {username} with ID: {user_id}")
        print(f"Password hash: {hashed_password}")
        return user_id
        
    except Exception as e:
        conn.rollback()
        print(f"Error creating test user: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    # Set up test user with known credentials
    TEST_USERNAME = "ehrtest"
    TEST_PASSWORD = "testpassword123"
    
    print("Creating EHR test user for login testing")
    print("======================================")
    
    user_id = create_test_user(TEST_USERNAME, TEST_PASSWORD, delete_existing=True)
    
    if user_id:
        print("\nTest user created successfully!")
        print(f"Username: {TEST_USERNAME}")
        print(f"Password: {TEST_PASSWORD}")
        print(f"User ID: {user_id}")
    else:
        print("\nFailed to create test user.") 