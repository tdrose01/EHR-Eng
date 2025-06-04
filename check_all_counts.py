#!/usr/bin/env python3
"""
Script to check dashboard statistics against actual database counts
"""

import psycopg2
import sys
import datetime

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'ehr_db',
    'user': 'postgres',
    'password': 'postgres'
}

def get_database_counts():
    """Connect to the database and get actual counts"""
    results = {
        "total_patients": None,
        "active_patients": None,
        "todays_appointments": None,
        "pending_records": None
    }
    
    try:
        print("Connecting to PostgreSQL database...")
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        
        cursor = conn.cursor()
        
        # Get total patients count
        try:
            cursor.execute("SELECT COUNT(*) FROM patients")
            results["total_patients"] = cursor.fetchone()[0]
            print(f"Total patients in database: {results['total_patients']}")
        except Exception as e:
            print(f"Error counting patients: {e}")
        
        # Get active patients count (status='Active')
        try:
            cursor.execute("SELECT COUNT(*) FROM patients WHERE status = 'Active'")
            results["active_patients"] = cursor.fetchone()[0]
            print(f"Active patients in database: {results['active_patients']}")
        except Exception as e:
            print(f"Error counting active patients: {e}")
        
        # Get today's appointments
        try:
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            cursor.execute("SELECT COUNT(*) FROM appointments WHERE DATE(appointment_date) = %s", (today,))
            results["todays_appointments"] = cursor.fetchone()[0]
            print(f"Today's appointments in database: {results['todays_appointments']}")
        except Exception as e:
            print(f"Error counting today's appointments: {e}")
        
        # Get pending records count
        try:
            cursor.execute("SELECT COUNT(*) FROM records WHERE status = 'Pending'")
            results["pending_records"] = cursor.fetchone()[0]
            print(f"Pending records in database: {results['pending_records']}")
        except Exception as e:
            print(f"Error counting pending records: {e}")
        
        # Close connection
        cursor.close()
        conn.close()
        
        return results
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return results

def get_dashboard_hardcoded_values():
    """Get the hardcoded values from backend/start_apis.py"""
    return {
        "total_patients": 156,  # DASHBOARD_STATS["totalPatients"]
        "active_patients": 136,  # DASHBOARD_STATS["totalPatients"] - 20
        "todays_appointments": 8,  # DASHBOARD_STATS["todayAppointments"]
        "pending_records": 12    # Hardcoded in the updated function
    }

if __name__ == "__main__":
    print("Comparing dashboard statistics with actual database counts...\n")
    
    # Get actual counts from database
    actual_counts = get_database_counts()
    
    # Get hardcoded dashboard values
    dashboard_values = get_dashboard_hardcoded_values()
    
    print("\nComparison Results:")
    print("-" * 50)
    print("Statistic             | Dashboard Value | Actual Database Count")
    print("-" * 50)
    
    for key, label in [
        ("total_patients", "Total Patients"),
        ("active_patients", "Active Patients"),
        ("todays_appointments", "Today's Appointments"),
        ("pending_records", "Pending Records")
    ]:
        dashboard_val = dashboard_values[key]
        db_val = actual_counts[key] if actual_counts[key] is not None else "Error"
        match = "✓" if dashboard_val == db_val else "✗"
        
        print(f"{label.ljust(22)} | {str(dashboard_val).center(15)} | {str(db_val).center(20)} {match}")
    
    print("-" * 50)
    print("\nRecommendation: Update the dashboard to use actual database counts instead of hardcoded values.") 