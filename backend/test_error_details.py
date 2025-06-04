#!/usr/bin/env python3
"""
Script to get detailed error information from the API
"""
import requests
import json
import sys

# API URL
API_URL = "http://localhost:8004/api/vaccines/simple"

print(f"Testing endpoint: {API_URL}")
try:
    response = requests.get(API_URL)
    print(f"Status code: {response.status_code}")
    
    # Try to parse as JSON
    try:
        data = response.json()
        print("Response data (JSON):")
        print(json.dumps(data, indent=2))
    except:
        # If not JSON, print as text
        print("Response text:")
        print(response.text)
    
    # Check specific error messages
    if response.status_code == 500:
        if "message" in response.text:
            try:
                error_data = json.loads(response.text)
                if "message" in error_data:
                    print("\nError message:", error_data["message"])
            except:
                pass
        
        print("\nThis is a server error (500). Check the server logs for more details.")
    
    if response.status_code == 200:
        print("\nEndpoint request successful!")
        sys.exit(0)
    else:
        sys.exit(1)
except Exception as e:
    print(f"Error connecting to API: {e}")
    sys.exit(1) 