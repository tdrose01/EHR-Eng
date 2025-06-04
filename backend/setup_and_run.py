import os
import sys
import subprocess
import time
import psycopg2
from psycopg2 import sql
import webbrowser
import signal
import atexit

# Configuration
DB_NAME = "test_vaccines"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"
SERVER_PORT = 8004
SERVER_HOST = "localhost"

# File paths
MIGRATIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "migrations")
TEST_HTML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vaccine_api_test.html")

# Server process
server_process = None

def get_connection_string():
    return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def create_database():
    """Create database if it doesn't exist"""
    print("Setting up database...")
    
    # Connect to PostgreSQL server
    conn = psycopg2.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database="postgres"
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Check if database exists
    cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (DB_NAME,))
    exists = cursor.fetchone()
    
    if not exists:
        print(f"Creating database {DB_NAME}...")
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
        print("Database created successfully")
    else:
        print(f"Database {DB_NAME} already exists")
    
    cursor.close()
    conn.close()

def run_migrations():
    """Run database migrations"""
    print("Running migrations...")
    
    # Get list of migration files
    migration_files = []
    for file in os.listdir(MIGRATIONS_DIR):
        if file.endswith(".sql"):
            migration_files.append(os.path.join(MIGRATIONS_DIR, file))
    
    # Sort migration files by name
    migration_files.sort()
    
    # Connect to the database
    conn = psycopg2.connect(get_connection_string())
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Track applied migrations
    applied_migrations = []
    failed_migrations = []
    
    # Run each migration in a separate transaction
    for migration_file in migration_files:
        file_name = os.path.basename(migration_file)
        print(f"Applying migration: {file_name}")
        
        try:
            # Read migration file
            with open(migration_file, 'r') as f:
                sql_script = f.read()
            
            # Execute in its own transaction
            cursor.execute("BEGIN;")
            cursor.execute(sql_script)
            cursor.execute("COMMIT;")
            
            applied_migrations.append(file_name)
            print(f"✓ Applied: {file_name}")
        except Exception as e:
            # Roll back transaction on error
            cursor.execute("ROLLBACK;")
            failed_migrations.append((file_name, str(e)))
            print(f"✗ Failed to apply {file_name}: {e}")
    
    # Summary
    if applied_migrations:
        print(f"\nSuccessfully applied {len(applied_migrations)} migrations:")
        for m in applied_migrations:
            print(f"  - {m}")
    
    if failed_migrations:
        print(f"\nWARNING: {len(failed_migrations)} migrations failed:")
        for m, err in failed_migrations:
            print(f"  - {m}: {err}")
    
    cursor.close()
    conn.close()
    
    return len(failed_migrations) == 0

def setup_test_vaccines_table():
    """Ensure the test_vaccines table exists with data"""
    print("Setting up test_vaccines table...")
    
    # Connect to the database
    conn = psycopg2.connect(get_connection_string())
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'test_vaccines')")
    table_exists = cursor.fetchone()[0]
    
    if not table_exists:
        print("Creating test_vaccines table directly...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_vaccines (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            manufacturer VARCHAR(255),
            description TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Insert sample data
        cursor.execute("""
        INSERT INTO test_vaccines (name, manufacturer, description)
        VALUES 
            ('Flu Vaccine', 'BioPharm', 'Annual influenza vaccine for seasonal flu protection'),
            ('COVID-19 Vaccine', 'ModernTech', 'mRNA-based vaccine against SARS-CoV-2'),
            ('Tdap Vaccine', 'ImmuneCorp', 'Tetanus, diphtheria, and pertussis vaccine for adults'),
            ('Hepatitis B Vaccine', 'LiverShield', 'Vaccine to prevent hepatitis B viral infection'),
            ('HPV Vaccine', 'CancerGuard', 'Human papillomavirus vaccine to prevent certain cancers')
        """)
        print("Test vaccines table created with sample data")
    else:
        print("test_vaccines table already exists")
    
    cursor.close()
    conn.close()

def start_server():
    """Start the vaccine server"""
    global server_process
    
    print("Starting vaccine server...")
    server_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "start_vaccine_server.py")
    
    # Start server as a separate process
    server_process = subprocess.Popen([sys.executable, server_script], 
                                      env=dict(os.environ, 
                                              DB_CONNECTION_STRING=get_connection_string(),
                                              PORT=str(SERVER_PORT)))
    
    # Register cleanup function
    atexit.register(cleanup)
    
    # Wait for server to start
    time.sleep(2)
    print(f"Server started on http://{SERVER_HOST}:{SERVER_PORT}")

def test_server_connection():
    """Test connection to the server"""
    import requests
    
    print("Testing server connection...")
    for attempt in range(3):
        try:
            response = requests.get(f"http://{SERVER_HOST}:{SERVER_PORT}/api/vaccines/test")
            if response.status_code == 200:
                print("Server is running correctly!")
                return True
            else:
                print(f"Server returned status code {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print(f"Connection attempt {attempt+1}/3 failed. Waiting to retry...")
            time.sleep(2)
    
    print("Failed to connect to server after multiple attempts")
    return False

def open_test_page():
    """Open the test HTML page in a browser"""
    print(f"Opening test page: {TEST_HTML_PATH}")
    webbrowser.open(f"file://{os.path.abspath(TEST_HTML_PATH)}")

def cleanup(sig=None, frame=None):
    """Clean up resources before exiting"""
    global server_process
    
    if server_process:
        print("Stopping server...")
        if sys.platform == 'win32':
            # Windows
            server_process.terminate()
        else:
            # Unix
            os.killpg(os.getpgid(server_process.pid), signal.SIGTERM)
        server_process = None

def main():
    """Main function"""
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    try:
        # Setup database
        create_database()
        
        # Run migrations
        migrations_ok = run_migrations()
        
        # Always ensure test_vaccines table exists
        setup_test_vaccines_table()
        
        # Start server
        start_server()
        
        # Test connection
        if test_server_connection():
            # Open test page
            open_test_page()
            
            print("\nServer is running. Press Ctrl+C to stop.")
            
            # Keep process running
            while True:
                time.sleep(1)
                
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cleanup()

if __name__ == "__main__":
    main() 