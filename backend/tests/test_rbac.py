import requests
import json
from app.database import execute_query, hash_password

def create_test_users():
    """Create test users with different roles."""
    roles = ["admin", "doctor", "nurse", "user"]
    created_users = []
    
    for role in roles:
        email = f"{role}@example.com"
        password = "password123" if role != "admin" else "admin123"
        full_name = f"{role.capitalize()} User"
        
        # Check if user already exists
        existing_user = execute_query(
            "SELECT id FROM users WHERE email = %s",
            (email,)
        )
        
        if existing_user:
            print(f"User {email} already exists with ID: {existing_user[0]['id']}")
            created_users.append({
                "email": email,
                "password": password,
                "role": role,
                "id": existing_user[0]['id']
            })
            continue
        
        # Create new user with bcrypt hashed password
        hashed_password = hash_password(password)
        
        result = execute_query(
            """INSERT INTO users (email, hashed_password, full_name, role) 
               VALUES (%s, %s, %s, %s) RETURNING id""",
            (email, hashed_password, full_name, role)
        )
        
        if result:
            user_id = result[0]['id']
            print(f"Created {role} user with ID: {user_id}")
            created_users.append({
                "email": email,
                "password": password,
                "role": role,
                "id": user_id
            })
        else:
            print(f"Failed to create {role} user")
    
    return created_users

def login(email, password):
    """Login and return session ID."""
    response = requests.post(
        "http://localhost:8000/api/auth/login",
        data={"username": email, "password": password}
    )
    
    if response.status_code == 200:
        data = response.json()
        return data["access_token"]
    else:
        print(f"Login failed for {email}: {response.text}")
        return None

def test_endpoint(session_id, endpoint, method="GET", data=None):
    """Test access to an endpoint."""
    headers = {"Cookie": f"session_id={session_id}"}
    
    if method == "GET":
        response = requests.get(f"http://localhost:8000{endpoint}", headers=headers)
    elif method == "POST":
        response = requests.post(f"http://localhost:8000{endpoint}", headers=headers, json=data)
    elif method == "PUT":
        response = requests.put(f"http://localhost:8000{endpoint}", headers=headers, json=data)
    elif method == "DELETE":
        response = requests.delete(f"http://localhost:8000{endpoint}", headers=headers)
    
    return response.status_code, response.text

def run_rbac_tests():
    """Run role-based access control tests."""
    # Create test users
    users = create_test_users()
    
    # Define endpoints to test
    endpoints = [
        {"path": "/api/patients", "method": "GET", "description": "List patients"},
        {"path": "/api/patients/1", "method": "GET", "description": "Get patient details"},
        {"path": "/api/patients", "method": "POST", "description": "Create patient", 
         "data": {
             "first_name": "Test",
             "last_name": "Patient",
             "date_of_birth": "1990-01-01",
             "gender": "Male"
         }},
        {"path": "/api/patients/1", "method": "PUT", "description": "Update patient",
         "data": {
             "first_name": "Updated",
             "last_name": "Patient"
         }},
        {"path": "/api/patients/1", "method": "DELETE", "description": "Delete patient"}
    ]
    
    # Run tests for each user
    results = {}
    
    for user in users:
        print(f"\nTesting as {user['role']} ({user['email']})...")
        session_id = login(user['email'], user['password'])
        
        if not session_id:
            continue
        
        user_results = {}
        
        for endpoint in endpoints:
            status_code, response_text = test_endpoint(
                session_id, 
                endpoint["path"], 
                endpoint["method"],
                endpoint.get("data")
            )
            
            success = status_code < 400
            user_results[endpoint["description"]] = {
                "success": success,
                "status_code": status_code
            }
            
            print(f"  {endpoint['method']} {endpoint['path']} ({endpoint['description']}): {status_code} {'✓' if success else '✗'}")
        
        results[user['role']] = user_results
    
    # Print summary
    print("\nRBAC Test Summary:")
    print("==================")
    
    for role, role_results in results.items():
        print(f"\n{role.upper()}:")
        for action, result in role_results.items():
            print(f"  {action}: {'✓' if result['success'] else '✗'} ({result['status_code']})")

if __name__ == "__main__":
    run_rbac_tests() 