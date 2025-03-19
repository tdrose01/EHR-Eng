import os
import sys
import psycopg2
import random
import hashlib
import datetime
import json
import argparse
from dotenv import load_dotenv
from faker import Faker
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

# Initialize Faker with English locale
fake = Faker('en_US')

# Constants for realistic data generation
BLOOD_TYPES = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
RANKS = ['E-1', 'E-2', 'E-3', 'E-4', 'E-5', 'E-6', 'E-7', 'E-8', 'E-9', 
         'O-1', 'O-2', 'O-3', 'O-4', 'O-5', 'O-6', 'O-7', 'O-8', 'O-9', 'O-10',
         'W-1', 'W-2', 'W-3', 'W-4', 'W-5', 'CIV']
SERVICES = ['Army', 'Navy', 'Air Force', 'Marine Corps', 'Coast Guard', 'Space Force']
COMMON_CONDITIONS = [
    'Hypertension', 'Type 2 Diabetes', 'Asthma', 'Osteoarthritis', 
    'Coronary Artery Disease', 'COPD', 'Depression', 'Anxiety Disorder',
    'Hyperlipidemia', 'Hypothyroidism', 'Gastroesophageal Reflux Disease'
]
MEDICATIONS = [
    'Lisinopril', 'Metformin', 'Albuterol', 'Atorvastatin', 'Levothyroxine',
    'Amlodipine', 'Metoprolol', 'Omeprazole', 'Simvastatin', 'Losartan',
    'Gabapentin', 'Sertraline', 'Hydrochlorothiazide', 'Acetaminophen', 'Ibuprofen'
]
ALLERGIES = [
    'Penicillin', 'Sulfa Drugs', 'Peanuts', 'Tree Nuts', 'Shellfish',
    'Latex', 'Bee Stings', 'Ibuprofen', 'Aspirin', 'Dairy', 'Eggs', 'Wheat'
]

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

def hash_password(password):
    """Hash a password using SHA-256."""
    salt = "ehr_salt"  # A real system would use a unique salt per user
    password_salt = password + salt
    hashed = hashlib.sha256(password_salt.encode()).hexdigest()
    return hashed

def check_tables_exist(conn):
    """Check if necessary tables exist in the database."""
    print_header("Checking Database Tables")
    
    cursor = conn.cursor()
    
    try:
        # Get list of all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        table_names = [t[0] for t in tables]
        
        print_info(f"Found tables: {', '.join(table_names)}")
        
        # Define expected tables
        expected_tables = ['login_history', 'patients', 'users', 'ranks', 'services', 'fmpcs']
        
        # Check if all expected tables exist
        missing_tables = [t for t in expected_tables if t not in table_names]
        
        if missing_tables:
            print_error(f"Missing required tables: {', '.join(missing_tables)}")
            return False
        
        print_success("All required tables exist!")
        return True
        
    except Exception as e:
        print_error(f"Error checking tables: {e}")
        return False
    finally:
        cursor.close()

def generate_users(conn, num_users=10):
    """Generate user accounts with realistic data."""
    print_header(f"Generating {num_users} User Accounts")
    
    cursor = conn.cursor()
    
    try:
        # Prepare for users
        users = []
        admin_created = False
        doctor_created = False
        nurse_created = False
        
        for i in range(num_users):
            # Generate profile
            first_name = fake.first_name()
            last_name = fake.last_name()
            
            # Determine role
            if not admin_created:
                username = 'admin'
                role = 'admin'
                admin_created = True
            elif not doctor_created:
                username = 'doctor'
                role = 'doctor'
                doctor_created = True
            elif not nurse_created:
                username = 'nurse'
                role = 'nurse'
                nurse_created = True
            else:
                username = fake.user_name() + str(random.randint(100, 999))
                role = random.choice(['doctor', 'nurse', 'staff'])
            
            # Set password (simple for test accounts)
            if username in ['admin', 'doctor', 'nurse']:
                password = f"{username}pass123"
            else:
                password = fake.password(length=10)
                
            hashed_password = hash_password(password)
            
            # Set creation and update times
            now = datetime.datetime.now()
            created_at = fake.date_time_between(start_date='-1y', end_date='now')
            updated_at = fake.date_time_between(start_date=created_at, end_date='now')
            
            # Set active status (most users are active)
            is_active = random.random() < 0.9
            
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                print_info(f"User '{username}' already exists, skipping...")
                continue
            
            # Store user data
            users.append({
                'username': username,
                'password': password,  # Store plain password for output only
                'hashed_password': hashed_password,
                'role': role,
                'is_active': is_active,
                'created_at': created_at,
                'updated_at': updated_at
            })
            
            # Insert into database
            cursor.execute("""
                INSERT INTO users (username, hashed_password, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (
                username, 
                hashed_password, 
                is_active,
                created_at,
                updated_at
            ))
            
            user_id = cursor.fetchone()[0]
            print_success(f"Created user: {username} (ID: {user_id}, Role: {role})")
            
        # Commit changes
        conn.commit()
        
        # Print summary of created users
        print_header("Created User Accounts (Save these credentials)")
        for user in users:
            print(f"Username: {user['username']}")
            print(f"Password: {user['password']}")
            print(f"Role: {user['role']}")
            print("---")
        
        return users
        
    except Exception as e:
        conn.rollback()
        print_error(f"Error generating users: {e}")
        return []
    finally:
        cursor.close()

def generate_ranks_and_services(conn):
    """Generate military ranks and services."""
    print_header("Generating Ranks and Services")
    
    cursor = conn.cursor()
    
    try:
        # Insert ranks
        for rank in RANKS:
            try:
                # Check if rank exists
                cursor.execute("SELECT id FROM ranks WHERE name = %s", (rank,))
                if cursor.fetchone() is None:
                    cursor.execute(
                        "INSERT INTO ranks (name) VALUES (%s)",
                        (rank,)
                    )
                    print_success(f"Added rank: {rank}")
                else:
                    print_info(f"Rank {rank} already exists")
            except Exception as e:
                print_error(f"Error inserting rank {rank}: {e}")
        
        # Insert services
        for service in SERVICES:
            try:
                # Check if service exists
                cursor.execute("SELECT id FROM services WHERE name = %s", (service,))
                if cursor.fetchone() is None:
                    cursor.execute(
                        "INSERT INTO services (name) VALUES (%s)",
                        (service,)
                    )
                    print_success(f"Added service: {service}")
                else:
                    print_info(f"Service {service} already exists")
            except Exception as e:
                print_error(f"Error inserting service {service}: {e}")
        
        conn.commit()
        print_success("Ranks and services generated successfully")
        return True
    except Exception as e:
        conn.rollback()
        print_error(f"Error generating ranks and services: {e}")
        return False
    finally:
        cursor.close()

def generate_patients(conn, num_patients=50):
    """Generate patient records with realistic medical data."""
    print_header(f"Generating {num_patients} Patient Records")
    
    cursor = conn.cursor()
    
    try:
        # Get rank IDs (to reference in patients)
        cursor.execute("SELECT id, name FROM ranks")
        ranks = cursor.fetchall()
        rank_dict = {rank[1]: rank[0] for rank in ranks}
        
        # Get service IDs (to reference in patients)
        cursor.execute("SELECT id, name FROM services")
        services = cursor.fetchall()
        service_dict = {service[1]: service[0] for service in services}
        
        # Generate patients
        patients_created = 0
        
        for i in range(num_patients):
            # Basic demographics
            first_name = fake.first_name()
            last_name = fake.last_name()
            dob = fake.date_of_birth(minimum_age=18, maximum_age=85)
            gender = random.choice(['Male', 'Female'])
            
            # Contact information
            contact_number = fake.phone_number()
            email = fake.email()
            address = f"{fake.street_address()}, {fake.city()}, {fake.state_abbr()} {fake.zipcode()}"
            
            # Emergency contact
            emergency_contact = fake.name()
            emergency_contact_number = fake.phone_number()
            
            # Medical data
            blood_type = random.choice(BLOOD_TYPES)
            
            # Generate some random allergies (0-3)
            num_allergies = random.randint(0, 3)
            selected_allergies = random.sample(ALLERGIES, num_allergies)
            allergies = ', '.join(selected_allergies) if selected_allergies else 'None'
            
            # Generate some random medical conditions (0-3)
            num_conditions = random.randint(0, 3)
            selected_conditions = random.sample(COMMON_CONDITIONS, num_conditions)
            medical_conditions = ', '.join(selected_conditions) if selected_conditions else 'None'
            
            # Military data - randomly select rank and service
            rank = random.choice(list(rank_dict.keys()))
            service = random.choice(list(service_dict.keys()))
            
            # Set creation and update times
            now = datetime.datetime.now()
            created_at = fake.date_time_between(start_date='-1y', end_date='now')
            updated_at = fake.date_time_between(start_date=created_at, end_date='now')
            
            # Generate a random FMPC ID (Family Member Primary Care)
            fmpc = f"F{random.randint(10000, 99999)}"
            
            # Insert patient record
            try:
                cursor.execute("""
                    INSERT INTO patients (
                        first_name, last_name, date_of_birth, gender,
                        contact_number, email, address,
                        emergency_contact, emergency_contact_number,
                        blood_type, allergies, medical_conditions,
                        rank, service, fmpc,
                        created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING patient_id
                """, (
                    first_name, last_name, dob, gender,
                    contact_number, email, address,
                    emergency_contact, emergency_contact_number,
                    blood_type, allergies, medical_conditions,
                    rank, service, fmpc,
                    created_at, updated_at
                ))
                
                patient_id = cursor.fetchone()[0]
                patients_created += 1
                
                if i % 10 == 0 or i < 5:  # Print some examples but not all
                    print_success(f"Created patient: {first_name} {last_name} (ID: {patient_id})")
                
            except Exception as e:
                print_error(f"Error creating patient: {e}")
        
        conn.commit()
        print_success(f"{patients_created} patients created successfully")
        return patients_created
        
    except Exception as e:
        conn.rollback()
        print_error(f"Error generating patients: {e}")
        return 0
    finally:
        cursor.close()

def generate_login_history(conn):
    """Generate realistic login history for users."""
    print_header("Generating Login History")
    
    cursor = conn.cursor()
    
    try:
        # Get all user IDs
        cursor.execute("SELECT id, username FROM users")
        users = cursor.fetchall()
        
        login_history_created = 0
        
        # Generate login events for each user
        for user_id, username in users:
            # Number of login events varies by user
            num_logins = random.randint(5, 30)
            
            # Users log in from a few regular IP addresses
            user_ips = [
                fake.ipv4(),
                fake.ipv4(),
                '127.0.0.1'  # Local development
            ]
            
            for _ in range(num_logins):
                # Generate timestamp within last 90 days
                timestamp = fake.date_time_between(start_date='-90d', end_date='now')
                
                # Usually successful, occasionally failed
                success = random.random() < 0.9  # 90% success rate
                
                # Mostly use regular IPs, occasionally others
                ip_address = random.choice(user_ips) if random.random() < 0.8 else fake.ipv4()
                
                cursor.execute("""
                    INSERT INTO login_history (user_id, timestamp, "ipAddress", success)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, timestamp, ip_address, success))
                
                login_history_created += 1
        
        conn.commit()
        print_success(f"Generated {login_history_created} login history records")
        return login_history_created
        
    except Exception as e:
        conn.rollback()
        print_error(f"Error generating login history: {e}")
        return 0
    finally:
        cursor.close()

def generate_fmpcs(conn):
    """Generate family member patient care system records."""
    print_header("Generating FMPC Records")
    
    cursor = conn.cursor()
    
    try:
        # Add a few FMPC entries (Family Member Primary Care)
        fmpc_entries = [
            "Pentagon Health Clinic",
            "Naval Hospital San Diego",
            "Walter Reed Medical Center",
            "Brooks Army Medical Center"
        ]
        
        fmpc_created = 0
        
        for name in fmpc_entries:
            # Check if entry already exists
            cursor.execute("SELECT id FROM fmpcs WHERE name = %s", (name,))
            if cursor.fetchone() is None:
                cursor.execute(
                    "INSERT INTO fmpcs (name) VALUES (%s) RETURNING id",
                    (name,)
                )
                fmpc_id = cursor.fetchone()[0]
                print_success(f"Added FMPC: {name} (ID: {fmpc_id})")
                fmpc_created += 1
            else:
                print_info(f"FMPC {name} already exists")
        
        conn.commit()
        print_success(f"Added {fmpc_created} FMPC entries")
        return fmpc_created
        
    except Exception as e:
        conn.rollback()
        print_error(f"Error generating FMPC entries: {e}")
        return 0
    finally:
        cursor.close()

def main():
    """Main function to generate realistic EHR data."""
    print_header("EHR System - Realistic Data Generator")
    
    parser = argparse.ArgumentParser(description='Generate realistic data for EHR system')
    parser.add_argument('--users', type=int, default=10, help='Number of user accounts to generate')
    parser.add_argument('--patients', type=int, default=50, help='Number of patient records to generate')
    parser.add_argument('--no-ranks', action='store_true', help='Skip ranks and services')
    parser.add_argument('--no-fmpc', action='store_true', help='Skip FMPC entries')
    parser.add_argument('--no-login-history', action='store_true', help='Skip login history')
    args = parser.parse_args()
    
    # Connect to database
    conn = get_db_connection()
    
    # Check if tables exist
    tables_exist = check_tables_exist(conn)
    if not tables_exist:
        print_error("Required tables are missing. Please set up the database schema first.")
        conn.close()
        return
    
    # Generate ranks and services
    if not args.no_ranks:
        generate_ranks_and_services(conn)
    
    # Generate FMPC entries
    if not args.no_fmpc:
        generate_fmpcs(conn)
    
    # Generate users
    users = generate_users(conn, args.users)
    
    # Generate patient records
    patients_created = generate_patients(conn, args.patients)
    
    # Generate login history
    if len(users) > 0 and not args.no_login_history:
        generate_login_history(conn)
    
    # Close connection
    conn.close()
    
    print_header("Data Generation Complete")
    print_info("You can now log in with the generated user accounts.")
    print_info("Default accounts:")
    print_info("  admin / adminpass123")
    print_info("  doctor / doctorpass123")
    print_info("  nurse / nursepass123")

if __name__ == "__main__":
    main() 