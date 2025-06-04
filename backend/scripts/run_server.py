import os
import sys
import argparse
import psycopg2
import importlib
import uvicorn
import subprocess
from dotenv import load_dotenv

# Get the absolute path to the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

# Load environment variables
load_dotenv(os.path.join(project_root, '.env'))

def check_database_connection():
    """Check if the PostgreSQL database is accessible"""
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'ehr_db'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres')
    }
    
    try:
        print(f"Checking connection to PostgreSQL database: {db_config['database']} on {db_config['host']}:{db_config['port']}")
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
        )
        conn.close()
        print("Database connection successful!")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

def setup_database():
    """Run the database setup script"""
    setup_script_path = os.path.join(project_root, 'scripts', 'setup_postgres_db.py')
    print(f"Running database setup script: {setup_script_path}")
    
    try:
        # Import and run the setup script
        setup_module = importlib.import_module('scripts.setup_postgres_db')
        setup_module.setup_db()
        return True
    except Exception as e:
        print(f"Error running database setup script: {e}")
        return False

def run_patient_api(port=8002):
    """Run the patient API server"""
    api_module = "api.patient_api:asgi_app"
    print(f"Starting patient API server at http://localhost:{port}")
    uvicorn.run(api_module, host="0.0.0.0", port=port, reload=True)

def run_login_api(port=8001):
    """Run the login API server"""
    api_module = "api.login_api:asgi_app"
    print(f"Starting login API server at http://localhost:{port}")
    uvicorn.run(api_module, host="0.0.0.0", port=port, reload=True)

def run_records_api(port=8003):
    """Run the records API server"""
    api_module = "api.records_api:asgi_app"
    print(f"Starting records API server at http://localhost:{port}")
    uvicorn.run(api_module, host="0.0.0.0", port=port, reload=True)

def main():
    """Main function to parse arguments and run servers"""
    parser = argparse.ArgumentParser(description='Run backend API servers')
    parser.add_argument('--patient-port', type=int, default=8002, help='Port for patient API (default: 8002)')
    parser.add_argument('--login-port', type=int, default=8001, help='Port for login API (default: 8001)')
    parser.add_argument('--records-port', type=int, default=8003, help='Port for records API (default: 8003)')
    parser.add_argument('--setup-db', action='store_true', help='Set up the database before starting servers')
    parser.add_argument('--service', choices=['patient', 'login', 'records', 'all'], default='all', help='Which service to run (default: all)')
    
    args = parser.parse_args()
    
    # Check database connection
    if not check_database_connection():
        if args.setup_db:
            print("Attempting to set up database...")
            if not setup_database():
                print("Database setup failed. Please check PostgreSQL configuration.")
                return 1
        else:
            print("Use --setup-db flag to initialize the database, or check your PostgreSQL configuration.")
            return 1
    
    # Run the selected services
    if args.service == 'patient':
        run_patient_api(args.patient_port)
    elif args.service == 'login':
        run_login_api(args.login_port)
    elif args.service == 'records':
        run_records_api(args.records_port)
    else:  # Run all services
        print("Starting all services...")
        
        # Create a new process for the login API
        login_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "api.login_api:asgi_app", 
            "--host", "0.0.0.0", 
            "--port", str(args.login_port),
            "--reload"
        ], cwd=project_root)
        
        # Create a new process for the records API
        records_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "api.records_api:asgi_app", 
            "--host", "0.0.0.0", 
            "--port", str(args.records_port),
            "--reload"
        ], cwd=project_root)
        
        # Run the patient API in the main process
        try:
            run_patient_api(args.patient_port)
        finally:
            # Terminate the other API processes when the main process exits
            for process, name in [(login_process, "login API"), (records_process, "records API")]:
                if process:
                    print(f"Terminating {name} process...")
                    process.terminate()
                    process.wait()

if __name__ == "__main__":
    sys.exit(main()) 