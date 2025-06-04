#!/usr/bin/env python3
"""
Browser automation test for the vaccine API server
This script uses requests to test the API endpoints and browser automation.
"""

import os
import sys
import json
import time
import requests
from urllib.parse import urljoin
import webbrowser
import datetime

# Constants
API_BASE_URL = "http://localhost:8004"
ENDPOINTS = [
    "/api/vaccines/test",
    "/api/vaccines/simple"
]

def print_header(message):
    """Print a formatted header for better readability"""
    print("\n" + "="*80)
    print(f"  {message}")
    print("="*80)

def test_api_connection():
    """Test basic connection to the API server"""
    print_header("Testing API Connection")
    try:
        response = requests.get(urljoin(API_BASE_URL, "/api/vaccines/test"))
        if response.status_code == 200:
            data = response.json()
            print(f"API Connection Successful: {data.get('message', '')}")
            print(f"   Timestamp: {data.get('timestamp', '')}")
            return True
        else:
            print(f"API Connection Failed: Status code {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"API Connection Failed: {e}")
        return False

def test_api_endpoints():
    """Test all API endpoints"""
    print_header("Testing API Endpoints")
    all_passed = True
    
    for endpoint in ENDPOINTS:
        print(f"\nTesting endpoint: {endpoint}")
        try:
            response = requests.get(urljoin(API_BASE_URL, endpoint))
            status_code = response.status_code
            print(f"Status code: {status_code}")
            
            if status_code == 200:
                data = response.json()
                print("Response data:")
                print(json.dumps(data, indent=2))
                print(f"Endpoint {endpoint} test passed")
            else:
                print(f"Endpoint {endpoint} returned status code {status_code}")
                all_passed = False
        except requests.RequestException as e:
            print(f"Endpoint {endpoint} test failed: {e}")
            all_passed = False
            
    return all_passed

def generate_html_report(test_results):
    """Generate an HTML report and open it in the browser"""
    print_header("Generating HTML Report")
    
    # Create a simple HTML report using ASCII symbols instead of Unicode
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Vaccine API Automation Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .success {{ color: green; }}
        .failure {{ color: red; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .result-box {{ 
            border: 1px solid #ddd; 
            padding: 15px; 
            margin-bottom: 20px; 
            border-radius: 5px;
            background-color: #f9f9f9;
        }}
        .timestamp {{ color: #666; font-size: 0.8em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Vaccine API Automation Test Report</h1>
        <p class="timestamp">Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="result-box">
            <h2>Test Summary</h2>
            <p>
                <span class="{'success' if test_results['connection'] else 'failure'}">
                    {'+' if test_results['connection'] else 'X'} API Connection: 
                    {'Successful' if test_results['connection'] else 'Failed'}
                </span>
            </p>
            <p>
                <span class="{'success' if test_results['endpoints'] else 'failure'}">
                    {'+' if test_results['endpoints'] else 'X'} API Endpoints: 
                    {'All Passed' if test_results['endpoints'] else 'Some Failed'}
                </span>
            </p>
            <h3>Overall Result:</h3>
            <p>
                <span class="{'success' if all(test_results.values()) else 'failure'}">
                    <strong>{'PASSED' if all(test_results.values()) else 'FAILED'}</strong>
                </span>
            </p>
        </div>
        
        <div class="result-box">
            <h2>Test Details</h2>
            <p>API Base URL: {API_BASE_URL}</p>
            <p>Endpoints Tested:</p>
            <ul>
                {''.join([f'<li>{endpoint}</li>' for endpoint in ENDPOINTS])}
            </ul>
        </div>
    </div>
</body>
</html>
"""
    
    # Save the HTML report with explicit UTF-8 encoding
    report_file = "vaccine_api_test_report.html"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    # Open the report in the browser
    try:
        print(f"Opening HTML report in browser: {report_file}")
        webbrowser.open(f"file://{os.path.abspath(report_file)}")
    except Exception as e:
        print(f"Failed to open browser: {e}")
        print(f"Report saved to: {os.path.abspath(report_file)}")
    
    return os.path.abspath(report_file)

def run_tests():
    """Run all tests and generate a report"""
    test_results = {
        "connection": False,
        "endpoints": False
    }
    
    print_header("Starting Vaccine API Automation Tests")
    print(f"API Base URL: {API_BASE_URL}")
    
    # Test connection
    test_results["connection"] = test_api_connection()
    
    # Only proceed with endpoint tests if connection succeeded
    if test_results["connection"]:
        test_results["endpoints"] = test_api_endpoints()
    
    # Generate and open report
    report_path = generate_html_report(test_results)
    
    # Print summary
    print_header("Test Summary")
    print(f"API Connection: {'PASSED' if test_results['connection'] else 'FAILED'}")
    print(f"API Endpoints: {'PASSED' if test_results['endpoints'] else 'FAILED'}")
    print(f"Overall Result: {'PASSED' if all(test_results.values()) else 'FAILED'}")
    print(f"\nReport saved to: {report_path}")
    
    return all(test_results.values())

if __name__ == "__main__":
    try:
        success = run_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\nUnexpected error during test: {e}")
        sys.exit(1) 