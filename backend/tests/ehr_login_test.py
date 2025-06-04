import requests
import json
import time
from colorama import init, Fore, Style

# Initialize colorama for colored output
init()

# Base URL for API
API_BASE_URL = "http://localhost:8000/api"

def print_header(message):
    """Print a formatted header message."""
    print(f"\n{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{message.center(70)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}\n")

def print_success(message):
    """Print a success message."""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def print_error(message):
    """Print an error message."""
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")

def print_info(message):
    """Print an info message."""
    print(f"{Fore.YELLOW}ℹ {message}{Style.RESET_ALL}")

def pretty_print_json(data):
    """Pretty print JSON data."""
    print(f"{Fore.BLUE}{json.dumps(data, indent=2)}{Style.RESET_ALL}")

def test_login(username, password):
    """Test the login API endpoint."""
    print_header(f"Testing Login for {username}")
    
    # Prepare request data
    request_data = {
        "username": username,
        "password": password
    }
    
    print_info("Sending login request:")
    pretty_print_json(request_data)
    
    try:
        # Send request
        response = requests.post(
            f"{API_BASE_URL}/login",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Get response data
        status_code = response.status_code
        response_data = response.json()
        
        print_info(f"Response status: {status_code}")
        print_info("Response data:")
        pretty_print_json(response_data)
        
        # Validate response
        if status_code == 200:
            print_success("Login successful!")
            # Check expected fields in response
            if "access_token" in response_data:
                print_success("Access token received")
            else:
                print_error("No access token in response")
                
            if "user" in response_data:
                print_success("User data received")
            else:
                print_error("No user data in response")
                
            return response_data.get("access_token")
        else:
            print_error(f"Login failed with status code: {status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print_error(f"Error during login request: {e}")
        return None
    except json.JSONDecodeError:
        print_error("Invalid JSON response")
        return None

def test_register(username, password, email, name):
    """Test the registration API endpoint."""
    print_header(f"Testing Registration for {username}")
    
    # Prepare request data
    request_data = {
        "username": username,
        "password": password,
        "email": email,
        "name": name
    }
    
    print_info("Sending registration request:")
    pretty_print_json(request_data)
    
    try:
        # Send request
        response = requests.post(
            f"{API_BASE_URL}/register",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Get response data
        status_code = response.status_code
        response_data = response.json()
        
        print_info(f"Response status: {status_code}")
        print_info("Response data:")
        pretty_print_json(response_data)
        
        # Validate response
        if status_code == 200:
            print_success("Registration successful!")
            # Check expected fields in response
            if "user" in response_data:
                print_success("User data received")
            else:
                print_error("No user data in response")
            
            return True
        else:
            print_error(f"Registration failed with status code: {status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Error during registration request: {e}")
        return False
    except json.JSONDecodeError:
        print_error("Invalid JSON response")
        return False

def test_get_profile(token):
    """Test getting the user profile."""
    print_header("Testing Get User Profile")
    
    if not token:
        print_error("No token provided. Skipping test.")
        return False
    
    print_info(f"Using token: {token[:15]}...")
    
    try:
        # Send request
        response = requests.get(
            f"{API_BASE_URL}/user/profile",
            headers={
                "Authorization": f"Bearer {token}"
            }
        )
        
        # Get response data
        status_code = response.status_code
        
        print_info(f"Response status: {status_code}")
        
        if status_code == 200:
            response_data = response.json()
            print_info("Response data:")
            pretty_print_json(response_data)
            print_success("Profile retrieval successful!")
            return True
        else:
            print_error(f"Profile retrieval failed with status code: {status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Error during profile request: {e}")
        return False
    except json.JSONDecodeError:
        print_error("Invalid JSON response")
        return False

def test_get_login_history(token):
    """Test getting the login history."""
    print_header("Testing Get Login History")
    
    if not token:
        print_error("No token provided. Skipping test.")
        return False
    
    print_info(f"Using token: {token[:15]}...")
    
    try:
        # Send request
        response = requests.get(
            f"{API_BASE_URL}/user/login-history",
            headers={
                "Authorization": f"Bearer {token}"
            }
        )
        
        # Get response data
        status_code = response.status_code
        
        print_info(f"Response status: {status_code}")
        
        if status_code == 200:
            response_data = response.json()
            print_info("Response data:")
            pretty_print_json(response_data)
            print_success("Login history retrieval successful!")
            return True
        else:
            print_error(f"Login history retrieval failed with status code: {status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Error during history request: {e}")
        return False
    except json.JSONDecodeError:
        print_error("Invalid JSON response")
        return False

def run_all_tests():
    """Run all API tests."""
    print_header("Starting EHR Login/Registration API Tests")
    
    # Test registration
    registration_success = test_register(
        username="newuser", 
        password="password123", 
        email="newuser@example.com", 
        name="New Test User"
    )
    
    # Add a delay between requests
    time.sleep(1)
    
    # Test login
    token = test_login(username="admin", password="admin123")
    
    # Add a delay between requests
    time.sleep(1)
    
    # Test profile retrieval
    if token:
        profile_success = test_get_profile(token)
        
        # Add a delay between requests
        time.sleep(1)
        
        # Test login history retrieval
        history_success = test_get_login_history(token)
    else:
        profile_success = False
        history_success = False
    
    # Print summary
    print_header("Test Summary")
    print_info("Registration test: " + (f"{Fore.GREEN}PASSED{Style.RESET_ALL}" if registration_success else f"{Fore.RED}FAILED{Style.RESET_ALL}"))
    print_info("Login test: " + (f"{Fore.GREEN}PASSED{Style.RESET_ALL}" if token else f"{Fore.RED}FAILED{Style.RESET_ALL}"))
    print_info("Profile test: " + (f"{Fore.GREEN}PASSED{Style.RESET_ALL}" if profile_success else f"{Fore.RED}FAILED{Style.RESET_ALL}"))
    print_info("History test: " + (f"{Fore.GREEN}PASSED{Style.RESET_ALL}" if history_success else f"{Fore.RED}FAILED{Style.RESET_ALL}"))
    
    if registration_success and token and profile_success and history_success:
        print_success("All tests passed!")
    else:
        print_error("Some tests failed. See details above.")

if __name__ == "__main__":
    run_all_tests() 