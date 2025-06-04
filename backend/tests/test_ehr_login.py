import os
import sys
import requests
import json
import psycopg2
import hashlib
import time
from colorama import init, Fore, Style
from dotenv import load_dotenv

# Initialize colorama for colored output
init()

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

# API Endpoints
API_BASE_URL = "http://localhost:8001/api"

def print_header(message):
    """Print a formatted header message."""
    print(f"\n{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{message.center(70)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}\n")

def print_success(message):
    """Print a success message."""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def print_error(message):
    """Print an error message."""
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")

def print_info(message):
    """Print an info message."""
    print(f"{Fore.YELLOW}ℹ {message}{Style.RESET_ALL}")

def pretty_print_json(data):
    """Pretty print JSON data."""
    print(f"{Fore.BLUE}{json.dumps(data, indent=2)}{Style.RESET_ALL}")

def get_db_connection():
    """Get a database connection."""
    try:
        print_info("Connecting to database...")
        print_info(f"Host: {DB_CONFIG['host']}")
        print_info(f"Port: {DB_CONFIG['port']}")
        print_info(f"Database: {DB_CONFIG['database']}")
        print_info(f"User: {DB_CONFIG['user']}")
        
        connection = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        print_success("Database connection established!")
        return connection
    except Exception as e:
        print_error(f"Database connection error: {e}")
        return None

def hash_password(password):
    """Hash a password using SHA-256."""
    salt = "ehr_salt"  # A real system would use a unique salt per user
    password_salt = password + salt
    hashed = hashlib.sha256(password_salt.encode()).hexdigest()
    return hashed

def verify_db_connection():
    """Verify database connection and required tables exist."""
    print_header("Verifying Database Connection")
    
    connection = get_db_connection()
    if not connection:
        return False
    
    cursor = connection.cursor()
    
    try:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        print_info(f"Found {len(tables)} tables:")
        for table in tables:
            print_info(f"  - {table[0]}")
        
        # Check for user-related tables
        required_tables = ['users', 'login_history']
        missing_tables = []
        
        for table in required_tables:
            if not any(t[0] == table for t in tables):
                missing_tables.append(table)
        
        if missing_tables:
            print_error(f"Missing required tables: {', '.join(missing_tables)}")
            return False
        else:
            print_success("All required tables exist!")
            return True
            
    except Exception as e:
        print_error(f"Error listing tables: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

def verify_test_user_exists():
    """Verify that the test user exists in the database."""
    print_header("Verifying Test User")
    
    TEST_USERNAME = "ehrtest"
    
    connection = get_db_connection()
    if not connection:
        return False
    
    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT id, username, hashed_password FROM users WHERE username = %s", (TEST_USERNAME,))
        user = cursor.fetchone()
        
        if not user:
            print_error(f"Test user '{TEST_USERNAME}' does not exist")
            return False
        
        user_id, username, hashed_password = user
        print_success(f"Test user '{username}' exists with ID: {user_id}")
        print_info(f"Password hash: {hashed_password[:10]}...")
        
        return True
    except Exception as e:
        print_error(f"Error verifying test user: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

def test_login_api():
    """Test the login API endpoint."""
    print_header("Testing Login API")
    
    # Test credentials
    TEST_USERNAME = "ehrtest"
    TEST_PASSWORD = "testpassword123"
    
    print_info(f"Attempting to login as '{TEST_USERNAME}'")
    
    try:
        # Check if API server is running
        response = requests.post(
            f"{API_BASE_URL}/login",
            json={"username": TEST_USERNAME, "password": TEST_PASSWORD},
            timeout=5
        )
        
        print_info(f"API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Login API request successful")
            pretty_print_json(data)
            
            # Check for success in our custom API format
            if data.get("success") == True:
                print_success("Login successful with API")
                print_info(f"Token: {data.get('token', '')[:20]}...")
                return True
            else:
                print_error(f"Login failed: {data.get('message', 'Unknown error')}")
                return False
        else:
            print_error(f"API request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print_error(f"Error: {error_data.get('message', 'Unknown error')}")
            except:
                print_error(f"Raw response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_error("Could not connect to API server. Is it running?")
        print_info("Remember to start the API server with: python login_api.py")
        return False
    except Exception as e:
        print_error(f"Error testing login API: {e}")
        return False

def test_database_login():
    """Test login directly with the database."""
    print_header("Testing Database Login")
    
    # Test credentials
    TEST_USERNAME = "ehrtest"
    TEST_PASSWORD = "testpassword123"
    
    connection = get_db_connection()
    if not connection:
        return False
    
    cursor = connection.cursor()
    
    try:
        # Check if user exists and password is correct
        cursor.execute(
            "SELECT id, username, hashed_password FROM users WHERE username = %s",
            (TEST_USERNAME,)
        )
        user_data = cursor.fetchone()
        
        if not user_data:
            print_error(f"User '{TEST_USERNAME}' does not exist")
            return False
        
        user_id, db_username, hashed_password = user_data
        
        # Hash the provided password
        password_hash = hash_password(TEST_PASSWORD)
        print_info("Login attempt:")
        pretty_print_json({
            "username": TEST_USERNAME,
            "password_hash": password_hash[:10] + "..."
        })
        
        # Check if password hashes match
        if password_hash != hashed_password:
            print_error("Invalid password")
            return False
        
        print_success(f"Login successful for user '{db_username}' (ID: {user_id})")
        
        # Record successful login
        try:
            cursor.execute(
                """
                INSERT INTO login_history (user_id, timestamp, "ipAddress", success)
                VALUES (%s, %s, %s, %s)
                """,
                (user_id, time.strftime('%Y-%m-%d %H:%M:%S'), '127.0.0.1', True)
            )
            connection.commit()
            print_success("Login history recorded")
        except Exception as e:
            print_error(f"Error recording login history: {e}")
        
        return True
        
    except Exception as e:
        print_error(f"Error testing database login: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

def print_summary(results):
    """Print a summary of test results."""
    print_header("Test Summary")
    
    total = len(results)
    passed = sum(1 for _, status in results if status)
    failed = total - passed
    
    print_info(f"Total tests: {total}")
    print_success(f"Tests passed: {passed}")
    if failed > 0:
        print_error(f"Tests failed: {failed}")
    else:
        print_success("All tests passed!")
    
    print("\nDetailed results:")
    for name, status in results:
        if status:
            print_success(f"✓ {name}")
        else:
            print_error(f"✗ {name}")

def main():
    """Run all tests."""
    results = []
    
    # Test database connection
    db_connection = verify_db_connection()
    results.append(("Database Connection", db_connection))
    
    # Test test user exists
    test_user = verify_test_user_exists()
    results.append(("Test User Exists", test_user))
    
    # Test database login
    db_login = test_database_login()
    results.append(("Database Login", db_login))
    
    # Test login API
    api_login = test_login_api()
    results.append(("API Login", api_login))
    
    # Print summary
    print_summary(results)

if __name__ == "__main__":
    main() 