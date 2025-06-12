import os
import sys
import subprocess
import time
import threading
import signal
import webbrowser
from colorama import init, Fore, Style

# Initialize colorama for colored output
init()

# Server ports
API_PORT = 8001  # Login API
PATIENT_API_PORT = 8002  # Patient API
APPOINTMENTS_API_PORT = 8003  # Appointments API
HTTP_PORT = 8080  # HTML/assets server

# Track subprocess objects
processes = []

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

def start_api_server():
    """Start the Flask API server."""
    print_header("Starting Login API Server")
    
    try:
        print_info(f"Starting login API server on port {API_PORT}...")
        
        # Use Python executable from current environment
        python_exe = sys.executable
        
        # Start Flask API server
        api_process = subprocess.Popen(
            [python_exe, "login_api.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        processes.append(api_process)
        
        # Wait a bit to ensure server starts
        time.sleep(2)
        
        # Check if process is still running
        if api_process.poll() is None:
            print_success(f"Login API server running at http://localhost:{API_PORT}")
            return True
        else:
            stdout, stderr = api_process.communicate()
            print_error(f"Login API server failed to start:")
            if stdout:
                print_error(f"Output: {stdout}")
            if stderr:
                print_error(f"Error: {stderr}")
            return False
            
    except Exception as e:
        print_error(f"Error starting login API server: {e}")
        return False

def start_patient_api_server():
    """Start the Patient API server."""
    print_header("Starting Patient API Server")
    
    try:
        print_info(f"Starting patient API server on port {PATIENT_API_PORT}...")
        
        # Use Python executable from current environment
        python_exe = sys.executable
        
        # Start Flask API server
        api_process = subprocess.Popen(
            [python_exe, "patient_api.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        processes.append(api_process)
        
        # Wait a bit to ensure server starts
        time.sleep(2)
        
        # Check if process is still running
        if api_process.poll() is None:
            print_success(f"Patient API server running at http://localhost:{PATIENT_API_PORT}")
            return True
        else:
            stdout, stderr = api_process.communicate()
            print_error(f"Patient API server failed to start:")
            if stdout:
                print_error(f"Output: {stdout}")
            if stderr:
                print_error(f"Error: {stderr}")
            return False
            
    except Exception as e:
        print_error(f"Error starting patient API server: {e}")
        return False

def start_appointments_api_server():
    """Start the Appointments API server."""
    print_header("Starting Appointments API Server")

    try:
        print_info(f"Starting appointments API server on port {APPOINTMENTS_API_PORT}...")

        python_exe = sys.executable

        api_process = subprocess.Popen(
            [python_exe, "appointments_api.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        processes.append(api_process)

        time.sleep(2)

        if api_process.poll() is None:
            print_success(f"Appointments API server running at http://localhost:{APPOINTMENTS_API_PORT}")
            return True
        else:
            stdout, stderr = api_process.communicate()
            print_error("Appointments API server failed to start:")
            if stdout:
                print_error(f"Output: {stdout}")
            if stderr:
                print_error(f"Error: {stderr}")
            return False

    except Exception as e:
        print_error(f"Error starting appointments API server: {e}")
        return False

def start_http_server():
    """Start the HTTP file server."""
    print_header("Starting HTTP Server")
    
    try:
        print_info(f"Starting HTTP server on port {HTTP_PORT}...")
        
        # Use Python executable from current environment
        python_exe = sys.executable
        
        # Start Python's HTTP server
        http_process = subprocess.Popen(
            [python_exe, "-m", "http.server", str(HTTP_PORT)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        processes.append(http_process)
        
        # Wait a bit to ensure server starts
        time.sleep(1)
        
        # Check if process is still running
        if http_process.poll() is None:
            print_success(f"HTTP server running at http://localhost:{HTTP_PORT}")
            return True
        else:
            stdout, stderr = http_process.communicate()
            print_error(f"HTTP server failed to start:")
            if stdout:
                print_error(f"Output: {stdout}")
            if stderr:
                print_error(f"Error: {stderr}")
            return False
            
    except Exception as e:
        print_error(f"Error starting HTTP server: {e}")
        return False

def open_login_page():
    """Open the login page in the default web browser."""
    login_url = f"http://localhost:{HTTP_PORT}/login.html"
    print_info(f"Opening login page at {login_url}")
    webbrowser.open(login_url)

def cleanup(signum=None, frame=None):
    """Clean up by terminating all child processes."""
    print_header("Shutting Down Servers")
    
    for process in processes:
        if process.poll() is None:  # If process is still running
            print_info(f"Terminating process PID {process.pid}")
            try:
                process.terminate()
                # Wait a bit for graceful termination
                time.sleep(0.5)
                # Force kill if still running
                if process.poll() is None:
                    process.kill()
            except Exception as e:
                print_error(f"Error terminating process: {e}")
    
    print_success("All servers stopped")
    
    # Exit if called as signal handler
    if signum is not None:
        sys.exit(0)

def main():
    """Start both servers and open the login page."""
    print_header("EHR System Server Startup")
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    # Start Login API server
    login_api_success = start_api_server()
    
    # Start Patient API server
    patient_api_success = start_patient_api_server()

    # Start Appointments API server
    appointments_api_success = start_appointments_api_server()
    
    # Start HTTP server
    http_success = start_http_server()
    
    if login_api_success and patient_api_success and appointments_api_success and http_success:
        print_success("All servers started successfully!")
        
        # Open login page
        print_info("Opening login page in browser...")
        threading.Timer(2, open_login_page).start()
        
        print_info("Press Ctrl+C to stop all servers")
        
        # Keep the script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            cleanup()
    else:
        print_error("Failed to start one or more servers")
        cleanup()

if __name__ == "__main__":
    main() 