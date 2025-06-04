import requests
import sys

print("Testing access to login page...")
try:
    response = requests.get("http://localhost:8080/login.html")
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        print("Login page accessible!")
        # Print the first 100 characters to verify it's the correct page
        print("Content preview:")
        print(response.text[:500])
    else:
        print("Failed to access login page")
except Exception as e:
    print(f"Error: {e}")

# Test API login directly
print("\nTesting login API...")
try:
    response = requests.post(
        "http://localhost:8001/api/login",
        json={"username": "admin", "password": "adminpass123"}
    )
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}") 