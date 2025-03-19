import os
import sys
import psycopg2
import json
from dotenv import load_dotenv
from colorama import init, Fore, Style

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

def get_db_connection():
    """Connect to the PostgreSQL database server."""
    try:
        print_info("Connecting to database...")
        print_info(f"Host: {DB_CONFIG['host']}")
        print_info(f"Port: {DB_CONFIG['port']}")
        print_info(f"Database: {DB_CONFIG['database']}")
        print_info(f"User: {DB_CONFIG['user']}")
        
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        
        print_success("Database connection successful!")
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print_error(f"Error: {error}")
        sys.exit(1)

def get_tables(conn):
    """Get all tables in the database."""
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        return [table[0] for table in tables]
    except Exception as e:
        print_error(f"Error getting tables: {e}")
        return []
    finally:
        cursor.close()

def get_columns(conn, table_name):
    """Get all columns in a table."""
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                column_name, 
                data_type, 
                character_maximum_length,
                is_nullable,
                column_default
            FROM information_schema.columns 
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position;
        """, (table_name,))
        columns = cursor.fetchall()
        return columns
    except Exception as e:
        print_error(f"Error getting columns for {table_name}: {e}")
        return []
    finally:
        cursor.close()

def check_schema():
    """Check the schema of the database."""
    print_header("Checking Database Schema")
    
    # Connect to database
    conn = get_db_connection()
    
    try:
        # Get all tables
        tables = get_tables(conn)
        
        if tables:
            print_info(f"Found {len(tables)} tables:")
            for table in tables:
                print_info(f"  - {table}")
            
            print_header("Table Schemas")
            
            # Check schema for each table
            for table in tables:
                print(f"\n{Fore.MAGENTA}Table: {table}{Style.RESET_ALL}")
                
                columns = get_columns(conn, table)
                for col in columns:
                    col_name, data_type, max_length, nullable, default = col
                    
                    # Format column type
                    col_type = data_type
                    if max_length is not None:
                        col_type = f"{data_type}({max_length})"
                    
                    # Format nullable
                    null_status = "NULL" if nullable == 'YES' else "NOT NULL"
                    
                    # Format default
                    default_str = f"DEFAULT {default}" if default else ""
                    
                    print(f"  {Fore.BLUE}{col_name}{Style.RESET_ALL}: {col_type} {null_status} {default_str}".strip())
        else:
            print_error("No tables found in the database.")
    finally:
        conn.close()

def check_records():
    """Check the number of records in each table."""
    print_header("Checking Record Counts")
    
    # Connect to database
    conn = get_db_connection()
    
    try:
        # Get all tables
        tables = get_tables(conn)
        
        if tables:
            cursor = conn.cursor()
            
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    
                    if count > 0:
                        print_success(f"{table}: {count} records")
                    else:
                        print_info(f"{table}: {count} records")
                        
                except Exception as e:
                    print_error(f"Error counting records in {table}: {e}")
            
            cursor.close()
        else:
            print_error("No tables found in the database.")
    finally:
        conn.close()

def main():
    """Main function."""
    print_header("Database Schema Analysis")
    
    # Check schema
    check_schema()
    
    # Check record counts
    check_records()

if __name__ == "__main__":
    main() 