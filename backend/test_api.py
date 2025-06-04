#!/usr/bin/env python3
"""
Simple script to test the vaccine API
"""
import requests
import json
import sys
import time

BASE_URL = "http://localhost:8004"

def test_api_connection():
    """Test basic API connection"""
    print("\n🔍 Testing API connection...")
    try:
        response = requests.get(f"{BASE_URL}/api/vaccines/test")
        
        if response.status_code == 200:
            print(f"✅ API is accessible. Status code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print(f"❌ API returned error. Status code: {response.status_code}")
            print("Response: ", response.text)
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Failed to connect to API. Is the server running?")
        return False

def test_simple_endpoint():
    """Test the simple endpoint"""
    print("\n🔍 Testing /api/vaccines/simple endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/vaccines/simple")
        
        if response.status_code == 200:
            print(f"✅ Endpoint successful. Status code: {response.status_code}")
            data = response.json()
            num_vaccines = len(data.get("vaccines", []))
            print(f"Received {num_vaccines} vaccines")
            # Print first vaccine if exists
            if num_vaccines > 0:
                print(f"First vaccine: {json.dumps(data['vaccines'][0], indent=2)}")
            return True
        else:
            print(f"❌ Endpoint returned error. Status code: {response.status_code}")
            print("Response: ", response.text)
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Failed to connect to API. Is the server running?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_schedules_endpoint():
    """Test the schedules endpoint"""
    print("\n🔍 Testing /api/vaccines/schedules endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/vaccines/schedules")
        
        if response.status_code == 200:
            print(f"✅ Endpoint successful. Status code: {response.status_code}")
            data = response.json()
            num_schedules = len(data.get("schedules", []))
            print(f"Received {num_schedules} schedules")
            # Print first schedule if exists
            if num_schedules > 0:
                print(f"First schedule: {json.dumps(data['schedules'][0], indent=2)}")
            return True
        else:
            print(f"❌ Endpoint returned error. Status code: {response.status_code}")
            print("Response: ", response.text)
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Failed to connect to API. Is the server running?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_next_dose_endpoint():
    """Test the next dose endpoint"""
    print("\n🔍 Testing /api/vaccines/next-dose endpoint...")
    
    vaccine_name = "Tdap"
    dose_number = 1
    age_group = "adult"
    
    try:
        response = requests.get(f"{BASE_URL}/api/vaccines/next-dose/{vaccine_name}/{dose_number}/{age_group}")
        
        if response.status_code == 200:
            print(f"✅ Endpoint successful. Status code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print(f"❌ Endpoint returned error. Status code: {response.status_code}")
            print("Response: ", response.text)
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Failed to connect to API. Is the server running?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function"""
    print("===== Vaccine API Test =====")
    
    # Wait for server to be fully started
    for attempt in range(3):
        if test_api_connection():
            break
        else:
            print(f"Waiting for API to be available (attempt {attempt+1}/3)...")
            time.sleep(2)
    
    # Run tests
    test_simple_endpoint()
    test_schedules_endpoint()
    test_next_dose_endpoint()
    
    print("\n===== Test Complete =====")

if __name__ == "__main__":
    main() 