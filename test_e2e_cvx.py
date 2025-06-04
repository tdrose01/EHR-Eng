#!/usr/bin/env python3
"""
End-to-end tests for the CVX code functionality
Tests the complete workflow from creating a vaccine record to viewing it with correct CVX codes
"""

import sys
import time
import json
import argparse
import requests
from datetime import datetime

def log(message):
    """Print log message with timestamp"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

def setup_test_data(base_url, auth_token):
    """Create test patient and record for testing"""
    log("Setting up test data...")
    
    # Create a test patient
    patient_data = {
        "firstName": "E2E",
        "lastName": "CVXTest",
        "birthDate": "2000-01-01",
        "gender": "Other",
        "email": "e2e_test@example.com"
    }
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    # Create patient
    response = requests.post(
        f"{base_url}/api/patients",
        headers=headers,
        json=patient_data
    )
    
    if response.status_code != 200:
        log(f"Error creating patient: {response.text}")
        sys.exit(1)
    
    patient_id = response.json()["patientId"]
    log(f"Created test patient with ID: {patient_id}")
    
    # Create a vaccination record
    record_data = {
        "patientId": patient_id,
        "type": "Vaccination",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "provider": "E2E Test Provider",
        "status": "Draft"
    }
    
    response = requests.post(
        f"{base_url}/api/records",
        headers=headers,
        json=record_data
    )
    
    if response.status_code != 200:
        log(f"Error creating record: {response.text}")
        sys.exit(1)
    
    record_id = response.json()["recordId"]
    log(f"Created test record with ID: {record_id}")
    
    return patient_id, record_id

def cleanup_test_data(base_url, auth_token, patient_id, record_id):
    """Clean up test data after tests"""
    log("Cleaning up test data...")
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    # Delete record
    response = requests.delete(
        f"{base_url}/api/records/{record_id}",
        headers=headers
    )
    
    if response.status_code != 200:
        log(f"Warning: Failed to delete record: {response.text}")
    
    # Delete patient
    response = requests.delete(
        f"{base_url}/api/patients/{patient_id}",
        headers=headers
    )
    
    if response.status_code != 200:
        log(f"Warning: Failed to delete patient: {response.text}")

def test_cvx_code_workflow(base_url, auth_token, patient_id, record_id):
    """Test the complete CVX code workflow"""
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    # 1. Get available vaccines
    log("Testing available vaccines API...")
    response = requests.get(
        f"{base_url}/api/vaccines/available",
        headers=headers
    )
    
    if response.status_code != 200:
        log(f"Error getting available vaccines: {response.text}")
        return False
    
    data = response.json()
    if not data.get("success"):
        log(f"API returned error: {data}")
        return False
    
    # Find a DTaP vaccine
    dtap_vaccine = None
    for vaccine in data["vaccines"]:
        if "DTaP" in vaccine["vaccineName"]:
            dtap_vaccine = vaccine
            break
    
    if not dtap_vaccine:
        log("Error: Could not find DTaP vaccine in available vaccines")
        return False
    
    # Check that it has a CVX code
    if not dtap_vaccine.get("cvxCode"):
        log(f"Error: DTaP vaccine has no CVX code: {dtap_vaccine}")
        return False
    
    log(f"Found DTaP vaccine with CVX code: {dtap_vaccine['cvxCode']}")
    
    # 2. Update the record with vaccine data
    vaccine_data = {
        "vaccineName": dtap_vaccine["vaccineName"],
        "brandName": dtap_vaccine["brandName"],
        "manufacturer": dtap_vaccine["manufacturer"],
        "doseNumber": 1,
        "totalDoses": dtap_vaccine.get("totalDoses", 5),
        # Deliberately not setting CVX code to test auto-population
    }
    
    update_data = {
        "type": "Vaccination",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "provider": "E2E Test Provider",
        "status": "Completed",
        "vaccineData": vaccine_data
    }
    
    log("Updating record with vaccine data...")
    response = requests.put(
        f"{base_url}/api/records/{record_id}",
        headers=headers,
        json=update_data
    )
    
    if response.status_code != 200:
        log(f"Error updating record: {response.text}")
        return False
    
    update_response = response.json()
    if not update_response.get("success"):
        log(f"API returned error: {update_response}")
        return False
    
    # 3. Get the record back and check CVX code
    log("Getting record to verify CVX code...")
    response = requests.get(
        f"{base_url}/api/records/{record_id}",
        headers=headers
    )
    
    if response.status_code != 200:
        log(f"Error getting record: {response.text}")
        return False
    
    record_data = response.json()
    if not record_data.get("success"):
        log(f"API returned error: {record_data}")
        return False
    
    vaccine_data = record_data.get("record", {}).get("vaccineData", {})
    
    # Verify CVX code was auto-populated
    if not vaccine_data.get("cvxCode"):
        log(f"Error: CVX code was not auto-populated: {vaccine_data}")
        return False
    
    log(f"Success! CVX code was auto-populated: {vaccine_data['cvxCode']}")
    return True

def main():
    """Run the end-to-end test"""
    parser = argparse.ArgumentParser(description="Run E2E tests for CVX code functionality")
    parser.add_argument("--url", default="http://localhost:3000", help="Base URL for the application")
    parser.add_argument("--token", required=True, help="Authentication token")
    args = parser.parse_args()
    
    log("Starting E2E test for CVX code functionality...")
    
    try:
        # Setup
        patient_id, record_id = setup_test_data(args.url, args.token)
        
        # Run tests
        success = test_cvx_code_workflow(args.url, args.token, patient_id, record_id)
        
        # Cleanup
        cleanup_test_data(args.url, args.token, patient_id, record_id)
        
        # Report results
        if success:
            log("✅ ALL TESTS PASSED!")
            return 0
        else:
            log("❌ TESTS FAILED!")
            return 1
    
    except Exception as e:
        log(f"Error during testing: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 