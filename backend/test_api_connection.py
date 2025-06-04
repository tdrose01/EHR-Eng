#!/usr/bin/env python3
"""
Simple script to test API connection to the vaccine server
"""
import requests
import json
import sys

# API URL
API_URL = "http://localhost:8004/api/vaccines/test"

print(f"Testing connection to: {API_URL}")
try:
    response = requests.get(API_URL)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("Response data:")
        print(json.dumps(data, indent=2))
        print("\nConnection successful!")
        sys.exit(0)
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(f"Response text: {response.text}")
        sys.exit(1)
except Exception as e:
    print(f"Error connecting to API: {e}")
    sys.exit(1) 