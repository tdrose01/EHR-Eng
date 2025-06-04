import sqlite3
import os

def check_patients():
    print("Checking patients in the database...")
    
    # Connect to the database
    conn = sqlite3.connect("ehr.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Get all patients
        cursor.execute("SELECT * FROM patients")
        patients = cursor.fetchall()
        
        print(f"Total patients: {len(patients)}")
        for patient in patients:
            print(f"ID: {patient['id']}")
            print(f"  Name: {patient['first_name']} {patient['last_name']}")
            print(f"  Gender: {patient['gender']}")
            print(f"  DOB: {patient['date_of_birth']}")
            print(f"  Contact: {patient['phone_number']}")
            print(f"  Insurance: {patient['insurance_provider']} ({patient['insurance_id']})")
            print(f"  Active: {patient['is_active']}")
            print("---")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    check_patients() 