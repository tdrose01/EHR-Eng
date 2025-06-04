import psycopg2
import os
import sys
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join('ehr-project', 'backend', '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

# Database configuration
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', 5432)),
    'database': os.environ.get('DB_NAME', 'ehr_db'),
    'user': os.environ.get('DB_USER', 'postgres'),
    'password': os.environ.get('DB_PASSWORD', 'postgres')
}

def get_db_connection():
    """Establish a connection to the PostgreSQL database."""
    try:
        print(f"Connecting to database...")
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
        print("Database connection established!")
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        sys.exit(1)

def check_login_history_table():
    """Check the structure of the login_history table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get column information
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'login_history'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        
        print("\nLogin History Table Columns:")
        for col in columns:
            print(f"- {col[0]} ({col[1]})")
        
        # Get sample data
        cursor.execute("SELECT * FROM login_history LIMIT 5")
        rows = cursor.fetchall()
        
        if rows:
            print("\nSample Login History Data:")
            column_names = [desc[0] for desc in cursor.description]
            for row in rows:
                print("\nEntry:")
                for i, value in enumerate(row):
                    print(f"  {column_names[i]}: {value}")
        else:
            print("\nNo login history data found.")
            
    except Exception as e:
        print(f"Error checking login_history table: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    check_login_history_table() 