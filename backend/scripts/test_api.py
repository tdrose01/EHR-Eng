import os
import sys
import json
import requests
import argparse
from datetime import datetime

def test_login(base_url, username="testuser", password="password"):
    """Test login API endpoint"""
    print("\nTesting login endpoint...")
    url = f"{base_url}/api/login"
    
    try:
        response = requests.post(url, json={"username": username, "password": password})
        response_data = response.json()
        
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response_data, indent=2)}")
        
        if response.status_code == 200 and response_data.get("success"):
            print("Login test: SUCCESS ✅")
            return response_data.get("token")
        else:
            print("Login test: FAILED ❌")
            return None
            
    except Exception as e:
        print(f"Error testing login: {e}")
        return None

def test_get_patients(base_url, token=None):
    """Test patients list API endpoint"""
    print("\nTesting get patients endpoint...")
    url = f"{base_url}/api/patients"
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = requests.get(url, headers=headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            total_patients = response_data.get('total', 0)
            patients = response_data.get('patients', [])
            
            print(f"Total patients: {total_patients}")
            print(f"First 2 patients:")
            
            for i, patient in enumerate(patients[:2]):
                print(f"  {i+1}. {patient.get('first_name')} {patient.get('last_name')} ({patient.get('patient_id')})")
            
            print("Get patients test: SUCCESS ✅")
            return patients
        else:
            print(f"Response: {response.text}")
            print("Get patients test: FAILED ❌")
            return []
            
    except Exception as e:
        print(f"Error testing get patients: {e}")
        return []

def test_get_patient(base_url, patient_id, token=None):
    """Test get single patient API endpoint"""
    print(f"\nTesting get patient endpoint for ID {patient_id}...")
    url = f"{base_url}/api/patients/{patient_id}"
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = requests.get(url, headers=headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            patient = response_data.get('patient', {})
            
            print(f"Patient: {patient.get('first_name')} {patient.get('last_name')}")
            print(f"DOB: {patient.get('date_of_birth')}")
            print(f"Service: {patient.get('service')}")
            
            print("Get patient test: SUCCESS ✅")
            return patient
        else:
            print(f"Response: {response.text}")
            print("Get patient test: FAILED ❌")
            return None
            
    except Exception as e:
        print(f"Error testing get patient: {e}")
        return None

def test_create_patient(base_url, token=None):
    """Test create patient API endpoint"""
    print("\nTesting create patient endpoint...")
    url = f"{base_url}/api/patients"
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    # Create test patient data with timestamp to ensure uniqueness
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    test_patient = {
        "first_name": f"Test{timestamp[:4]}",
        "last_name": f"User{timestamp[4:8]}",
        "date_of_birth": "1990-01-01",
        "gender": "Other",
        "service": "Test Service",
        "rank": "E-1",
        "blood_type": "O+",
        "contact_number": "555-123-4567",
        "email": f"test{timestamp}@example.com"
    }
    
    try:
        response = requests.post(url, json=test_patient, headers=headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            
            print(f"Response: {json.dumps(response_data, indent=2)}")
            
            if response_data.get("success"):
                print("Create patient test: SUCCESS ✅")
                return response_data.get("patient_id")
            else:
                print("Create patient test: FAILED ❌")
                return None
        else:
            print(f"Response: {response.text}")
            print("Create patient test: FAILED ❌")
            return None
            
    except Exception as e:
        print(f"Error testing create patient: {e}")
        return None

def main():
    """Main function to run API tests"""
    parser = argparse.ArgumentParser(description='Test EHR API endpoints')
    parser.add_argument('--url', default='http://localhost:8002', help='Base URL for API (default: http://localhost:8002)')
    parser.add_argument('--login-url', default=None, help='Base URL for login API (default: same as main URL)')
    
    args = parser.parse_args()
    
    base_url = args.url
    login_url = args.login_url or base_url
    
    print(f"Testing API at {base_url}")
    print(f"Using login API at {login_url}")
    
    # Test login
    token = test_login(login_url)
    
    # Test get patients
    patients = test_get_patients(base_url, token)
    
    # Test get single patient if we have patients
    if patients:
        patient_id = patients[0].get('patient_id')
        if patient_id:
            test_get_patient(base_url, patient_id, token)
    
    # Test create patient
    new_patient_id = test_create_patient(base_url, token)
    
    # If creating a patient worked, test retrieving it
    if new_patient_id:
        test_get_patient(base_url, new_patient_id, token)
    
    print("\nAPI Testing Complete!")

if __name__ == "__main__":
    main() 