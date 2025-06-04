#!/usr/bin/env python3
"""
Vaccine API server with enhanced logging for debugging
"""
import os
import sys
import logging
import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('vaccine_api')

# Create Flask app
app = Flask(__name__)
CORS(app)

def get_db_connection():
    """Create a connection to the PostgreSQL database"""
    try:
        # First try to use the connection string if provided
        conn_string = os.environ.get('DB_CONNECTION_STRING')
        if conn_string:
            logger.info(f"Connecting using connection string")
            conn = psycopg2.connect(conn_string)
            return conn
        
        # Otherwise use individual parameters
        host = os.environ.get('DB_HOST', 'localhost')
        port = os.environ.get('DB_PORT', '5432')
        dbname = os.environ.get('DB_NAME', 'test_vaccines')
        user = os.environ.get('DB_USER', 'postgres')
        password = os.environ.get('DB_PASSWORD', 'postgres')
        
        logger.info(f"Connecting to {dbname} on {host}:{port} as {user}")
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

def setup_database():
    """Set up a simple database for testing if migrations haven't been run"""
    logger.info("Setting up test database...")
    conn = get_db_connection()
    if not conn:
        logger.error("Failed to connect to database")
        return False
    
    conn.autocommit = True
    cursor = conn.cursor()
    
    try:
        # Check if the test_vaccines table exists
        cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'test_vaccines'
        )
        """)
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            logger.info("Creating test_vaccines table...")
            # Create test table for vaccines with schema matching the migration
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_vaccines (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                manufacturer VARCHAR(255),
                description TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Insert sample data matching the migration
            cursor.execute("""
            INSERT INTO test_vaccines (name, manufacturer, description)
            VALUES 
                ('Flu Vaccine', 'BioPharm', 'Annual influenza vaccine for seasonal flu protection'),
                ('COVID-19 Vaccine', 'ModernTech', 'mRNA-based vaccine against SARS-CoV-2'),
                ('Tdap Vaccine', 'ImmuneCorp', 'Tetanus, diphtheria, and pertussis vaccine for adults'),
                ('Hepatitis B Vaccine', 'LiverShield', 'Vaccine to prevent hepatitis B viral infection'),
                ('HPV Vaccine', 'CancerGuard', 'Human papillomavirus vaccine to prevent certain cancers')
            """)
            
            logger.info("Sample data inserted successfully")
        else:
            logger.info("test_vaccines table already exists")
        
        # List all tables in the database for debugging
        cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        """)
        tables = [table[0] for table in cursor.fetchall()]
        logger.info(f"Tables in database: {', '.join(tables)}")
        
        conn.commit()
        cursor.close()
        return True
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

@app.route('/api/vaccines/test', methods=['GET'])
def test_endpoint():
    """Simple test endpoint that doesn't require complex DB setup"""
    logger.info("Test endpoint called")
    return jsonify({
        "success": True,
        "message": "Vaccine API is working",
        "timestamp": datetime.datetime.now().isoformat()
    })

@app.route('/api/vaccines/simple', methods=['GET'])
def get_simple_vaccines():
    """Simple endpoint to get vaccines from test table"""
    logger.info("Simple vaccines endpoint called")
    conn = get_db_connection()
    if not conn:
        logger.error("Database connection failed")
        return jsonify({"success": False, "message": "Database connection failed"}), 500
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        logger.debug("Executing query: SELECT * FROM test_vaccines")
        cursor.execute("SELECT * FROM test_vaccines")
        vaccines = cursor.fetchall()
        logger.info(f"Retrieved {len(vaccines)} vaccines")
        
        return jsonify({
            "success": True,
            "vaccines": vaccines
        })
    except Exception as e:
        logger.error(f"Error fetching vaccines: {e}")
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/vaccines/schedules', methods=['GET'])
def get_vaccine_schedules():
    """Get vaccine schedules from the vaccine_schedules table"""
    logger.info("Vaccine schedules endpoint called")
    conn = get_db_connection()
    if not conn:
        logger.error("Database connection failed")
        return jsonify({"success": False, "message": "Database connection failed"}), 500
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        logger.debug("Executing query: SELECT * FROM vaccine_schedules")
        cursor.execute("""
        SELECT * FROM vaccine_schedules ORDER BY vaccine_name, dose_number
        """)
        schedules = cursor.fetchall()
        logger.info(f"Retrieved {len(schedules)} schedules")
        
        return jsonify({
            "success": True,
            "schedules": schedules
        })
    except Exception as e:
        logger.error(f"Error fetching vaccine schedules: {e}")
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/vaccines/next-dose/<vaccine_name>/<int:dose_number>/<age_group>', methods=['GET'])
def get_next_dose_date(vaccine_name, dose_number, age_group):
    """Calculate next dose date based on the current dose"""
    logger.info(f"Next dose endpoint called for {vaccine_name}, dose {dose_number}, age {age_group}")
    conn = get_db_connection()
    if not conn:
        logger.error("Database connection failed")
        return jsonify({"success": False, "message": "Database connection failed"}), 500
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Call the PostgreSQL function to calculate next dose date
        logger.debug(f"Calling calculate_next_dose('{vaccine_name}', {dose_number}, '{age_group}')")
        cursor.execute("""
        SELECT calculate_next_dose(%s, %s, %s) AS next_dose
        """, (vaccine_name, dose_number, age_group))
        
        result = cursor.fetchone()
        logger.info(f"Next dose result: {result}")
        
        return jsonify({
            "success": True,
            "next_dose": result
        })
    except Exception as e:
        logger.error(f"Error calculating next dose date: {e}")
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get server status and database information"""
    logger.info("Status endpoint called")
    conn = get_db_connection()
    
    status = {
        "server": "running",
        "timestamp": datetime.datetime.now().isoformat(),
        "environment": {
            "python_version": sys.version,
            "flask_version": Flask.__version__,
            "platform": sys.platform
        },
        "database": {
            "connected": conn is not None,
        }
    }
    
    if conn:
        cursor = conn.cursor()
        try:
            # Get PostgreSQL version
            cursor.execute("SELECT version()")
            pg_version = cursor.fetchone()[0]
            
            # Count tables
            cursor.execute("""
            SELECT count(*) FROM information_schema.tables 
            WHERE table_schema = 'public'
            """)
            table_count = cursor.fetchone()[0]
            
            # List tables
            cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
            """)
            tables = [table[0] for table in cursor.fetchall()]
            
            status["database"]["version"] = pg_version
            status["database"]["table_count"] = table_count
            status["database"]["tables"] = tables
            
        except Exception as e:
            logger.error(f"Error getting database info: {e}")
            status["database"]["error"] = str(e)
        finally:
            cursor.close()
            conn.close()
    
    return jsonify(status)

if __name__ == "__main__":
    logger.info("Starting vaccine API server")
    if setup_database():
        logger.info("Database setup complete")
    else:
        logger.warning("Database setup failed, but continuing anyway...")
    
    port = int(os.environ.get("PORT", 8004))
    logger.info(f"Starting server on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True) 