#!/usr/bin/env python3
"""
Script to run all vaccine-related tests and restart the server
"""
import os
import sys
import unittest
import subprocess
import time
import signal
import requests

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_unit_tests():
    """Run unit tests for vaccine functions"""
    print("\n===== Running Unit Tests =====")
    
    # Load and run the tests
    from test_vaccine_functions import VaccineFunctionsTest
    unit_suite = unittest.TestLoader().loadTestsFromTestCase(VaccineFunctionsTest)
    unit_result = unittest.TextTestRunner(verbosity=2).run(unit_suite)
    
    if unit_result.wasSuccessful():
        print("Unit tests: All tests passed!")
        return True
    else:
        print(f"Unit tests: {len(unit_result.errors)} errors, {len(unit_result.failures)} failures")
        return False

def run_api_tests():
    """Run API tests for vaccine endpoints"""
    print("\n===== Running API Tests =====")
    
    # Load and run the tests
    from test_vaccine_api import VaccineApiTest
    api_suite = unittest.TestLoader().loadTestsFromTestCase(VaccineApiTest)
    api_result = unittest.TextTestRunner(verbosity=2).run(api_suite)
    
    if api_result.wasSuccessful():
        print("API tests: All tests passed!")
        return True
    else:
        print(f"API tests: {len(api_result.errors)} errors, {len(api_result.failures)} failures")
        return False

def run_regression_tests():
    """Run regression tests against a live server"""
    print("\n===== Running Regression Tests =====")
    
    # Start the API server
    server_process = None
    try:
        # Check if server is already running
        try:
            response = requests.get("http://localhost:8004/api/vaccines/available")
            print("Server already running, skipping server startup")
        except requests.RequestException:
            # Start the server
            print("Starting API server...")
            server_process = subprocess.Popen(
                ["python", "../api/vaccine_api.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for server to start
            time.sleep(3)
            
            # Verify server is running
            retries = 5
            while retries > 0:
                try:
                    response = requests.get("http://localhost:8004/api/vaccines/available")
                    if response.status_code == 200:
                        print("Server started successfully")
                        break
                except requests.RequestException:
                    time.sleep(2)
                    retries -= 1
            
            if retries == 0:
                print("Failed to start server for regression tests")
                return False
        
        # Run regression tests
        from test_vaccine_api import RegressionTest
        regression_suite = unittest.TestLoader().loadTestsFromTestCase(RegressionTest)
        regression_result = unittest.TextTestRunner(verbosity=2).run(regression_suite)
        
        if regression_result.wasSuccessful():
            print("Regression tests: All tests passed!")
            return True
        else:
            print(f"Regression tests: {len(regression_result.errors)} errors, {len(regression_result.failures)} failures")
            return False
    
    finally:
        # Clean up server process if we started it
        if server_process is not None:
            print("Stopping test server...")
            # Try graceful shutdown first
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't respond
                server_process.kill()

def restart_main_server():
    """Restart the main API server"""
    print("\n===== Restarting Main Server =====")
    
    # Check for running server processes
    try:
        # Find running API processes
        result = subprocess.run(
            ["ps", "-ef"],
            capture_output=True,
            text=True
        )
        
        # Look for running vaccine_api processes
        for line in result.stdout.split('\n'):
            if "python" in line and "vaccine_api.py" in line and "grep" not in line:
                pid = int(line.split()[1])
                print(f"Found running API server (PID: {pid}), stopping it...")
                try:
                    os.kill(pid, signal.SIGTERM)
                    time.sleep(2)  # Give it time to shut down
                except ProcessLookupError:
                    print(f"Process {pid} not found - may have already terminated")
    except Exception as e:
        print(f"Error checking for running servers: {e}")
    
    # Start the server
    try:
        print("Starting main API server...")
        # Start in a new process group so it doesn't terminate when this script ends
        api_process = subprocess.Popen(
            ["python", "../api/vaccine_api.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True
        )
        
        # Wait for server to start
        time.sleep(3)
        
        # Verify server is running
        retries = 5
        while retries > 0:
            try:
                response = requests.get("http://localhost:8004/api/vaccines/available")
                if response.status_code == 200:
                    print("Server started successfully")
                    print("API URL: http://localhost:8004")
                    return True
            except requests.RequestException:
                time.sleep(2)
                retries -= 1
        
        print("Failed to start server")
        return False
    except Exception as e:
        print(f"Error starting server: {e}")
        return False

if __name__ == "__main__":
    print("Starting vaccine tests and server restart")
    
    # Run the tests
    unit_success = run_unit_tests()
    api_success = run_api_tests()
    regression_success = run_regression_tests()
    
    # Print test summary
    print("\n===== Test Summary =====")
    print(f"Unit Tests: {'PASSED' if unit_success else 'FAILED'}")
    print(f"API Tests: {'PASSED' if api_success else 'FAILED'}")
    print(f"Regression Tests: {'PASSED' if regression_success else 'FAILED'}")
    
    # Only restart the server if all tests pass
    if unit_success and api_success and regression_success:
        print("\nAll tests passed! Restarting server...")
        restart_success = restart_main_server()
        
        if restart_success:
            print("\n===== System Ready =====")
            print("The vaccine scheduling API is running at: http://localhost:8004")
            print("Available endpoints:")
            print("- GET /api/vaccines/available")
            print("- GET /api/vaccines/schedules")
            print("- GET /api/vaccines/alternative-schedules")
            print("- GET /api/vaccines/next-dose")
            print("- GET /api/vaccines/dose-by-age")
        else:
            print("\nServer restart failed. Please restart manually.")
    else:
        print("\nSome tests failed. Please fix issues before restarting server.")
        sys.exit(1) 