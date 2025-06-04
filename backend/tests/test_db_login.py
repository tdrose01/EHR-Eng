import os
import sys
import psycopg2
import json
import time
import hashlib
import base64
import datetime
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

def test_db_tables():
    """Test database tables existence."""
    print_header("Testing Database Tables")
    
    connection = get_db_connection()
    if not connection:
        return False
    
    cursor = connection.cursor()
    
    # Get list of tables
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

def check_user_exists(username):
    """Check if a user exists in the database."""
    connection = get_db_connection()
    if not connection:
        return False
    
    cursor = connection.cursor()
    
    try:
        # Using the actual database schema
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
        count = cursor.fetchone()[0]
        return count > 0
    except Exception as e:
        print_error(f"Error checking user: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

def test_register(username, password, email=""):
    """Test user registration directly with the database."""
    print_header(f"Testing Registration for {username}")
    
    # Skip if user already exists
    if check_user_exists(username):
        print_info(f"User '{username}' already exists. Skipping registration.")
        return True
    
    connection = get_db_connection()
    if not connection:
        return False
    
    cursor = connection.cursor()
    
    # Prepare user data
    hashed_password = hash_password(password)
    created_at = datetime.datetime.now()
    updated_at = created_at
    
    print_info("Registering new user:")
    user_data = {
        "username": username,
        "hashed_password": hashed_password[:10] + "...",  # Show partial hash for security
        "created_at": created_at.isoformat(),
        "updated_at": updated_at.isoformat(),
        "is_active": True
    }
    pretty_print_json(user_data)
    
    try:
        # Using the actual database schema
        cursor.execute("""
            INSERT INTO users (username, hashed_password, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """, (username, hashed_password, True, created_at, updated_at))
        
        user_id = cursor.fetchone()[0]
        connection.commit()
        
        print_success(f"User registered successfully with ID: {user_id}")
        return True
        
    except Exception as e:
        connection.rollback()
        print_error(f"Error registering user: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

def test_login(username, password):
    """Test login functionality."""
    print_header(f"Testing Login for {username}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if user exists and password is correct
        cursor.execute(
            "SELECT id, username, hashed_password FROM users WHERE username = %s",
            (username,)
        )
        user_data = cursor.fetchone()
        
        if not user_data:
            print_error(f"User '{username}' does not exist")
            return None
        
        user_id, db_username, hashed_password = user_data
        
        # Hash the provided password
        password_hash = hash_password(password)
        print_info("Attempting login:")
        pretty_print_json({
            "username": username,
            "password_hash": password_hash[:10] + "..."
        })
        
        # Check if password hashes match
        if password_hash != hashed_password:
            print_error("Invalid password")
            
            # Record failed login attempt
            try:
                cursor.execute(
                    """
                    INSERT INTO login_history (user_id, timestamp, "ipAddress", success)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (user_id, datetime.datetime.now(), "127.0.0.1", False)
                )
                conn.commit()
            except Exception as e:
                print_error(f"Error recording failed login: {e}")
            
            return None
        
        # Login successful, create token
        timestamp = datetime.datetime.now().isoformat()
        token = base64.b64encode(f"{username}:{timestamp}".encode()).decode()
        
        # Update last login time
        try:
            cursor.execute(
                """
                UPDATE users 
                SET last_login = %s, updated_at = %s
                WHERE id = %s
                """,
                (datetime.datetime.now(), datetime.datetime.now(), user_id)
            )
            conn.commit()
        except Exception as e:
            print_error(f"Error updating last login time: {e}")
        
        # Record successful login attempt
        try:
            cursor.execute(
                """
                INSERT INTO login_history (user_id, timestamp, "ipAddress", success)
                VALUES (%s, %s, %s, %s)
                """,
                (user_id, datetime.datetime.now(), "127.0.0.1", True)
            )
            conn.commit()
        except Exception as e:
            print_error(f"Error recording login: {e}")
            # Continue execution even if we can't record login
        
        print_success("Authentication successful!")
        
        # Return user data
        user_info = {
            "id": user_id,
            "username": db_username,
            "token": token
        }
        
        print_info("User data:")
        pretty_print_json(user_info)
        
        return user_info
        
    except Exception as e:
        print_error(f"Error during login: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def test_get_login_history(user_id):
    """Test getting login history for a user."""
    print_header(f"Testing Login History for User ID {user_id}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """
            SELECT timestamp, "ipAddress", success
            FROM login_history
            WHERE user_id = %s
            ORDER BY timestamp DESC
            LIMIT 5
            """,
            (user_id,)
        )
        
        history = cursor.fetchall()
        
        if not history:
            print_info("No login history found")
            return False
        
        print_info("Login History:")
        for entry in history:
            timestamp, ip, success = entry
            status = "Success" if success else "Failed"
            print_info(f"  {timestamp} | IP: {ip} | {status}")
        
        return True
        
    except Exception as e:
        print_error(f"Error getting login history: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def run_all_tests():
    """Run all database tests."""
    print_header("Starting EHR Database Login/Registration Tests")
    
    # Test database tables
    tables_ok = test_db_tables()
    if not tables_ok:
        print_error("Database tables check failed. Stopping tests.")
        return
    
    # Add some delay
    time.sleep(1)
    
    # Use our known test user
    test_user = "ehrtest"
    test_password = "testpassword123"
    
    # Test login with wrong password
    print_header("Testing Login with Wrong Password")
    wrong_login = test_login(username=test_user, password="wrongpassword")
    
    # Add some delay
    time.sleep(1)
    
    # Test login with correct password
    user_data = test_login(username=test_user, password=test_password)
    login_success = user_data is not None
    
    # Test login history if login successful
    history_success = False
    if login_success:
        history_success = test_get_login_history(user_data["id"])
    
    # Print summary
    print_header("Test Summary")
    print_info("Database tables check: " + (f"{Fore.GREEN}PASSED{Style.RESET_ALL}" if tables_ok else f"{Fore.RED}FAILED{Style.RESET_ALL}"))
    print_info("Login test: " + (f"{Fore.GREEN}PASSED{Style.RESET_ALL}" if login_success else f"{Fore.RED}FAILED{Style.RESET_ALL}"))
    print_info("History test: " + (f"{Fore.GREEN}PASSED{Style.RESET_ALL}" if history_success else f"{Fore.RED}FAILED{Style.RESET_ALL}"))
    
    if tables_ok and login_success and history_success:
        print_success("All tests passed!")
    else:
        print_error("Some tests failed. See details above.")

if __name__ == "__main__":
    run_all_tests() 