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
HTTP_PORT = 8080  # HTML/assets server
MAX_PORT_ATTEMPTS = 10  # Maximum number of ports to try

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
            [python_exe, "backend/api/login_api.py"],
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
            [python_exe, "backend/api/patient_api.py"],
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

def kill_process_on_port(port):
    """Kill the process using the specified port."""
    print_info(f"Attempting to kill process using port {port}...")
    
    try:
        if sys.platform == 'win32':
            # Windows
            # Find process ID using the port
            find_pid_cmd = ["netstat", "-ano", "|", "findstr", f":{port}"]
            netstat_result = subprocess.run(find_pid_cmd, capture_output=True, text=True, shell=True)
            
            if netstat_result.stdout:
                # Extract PID from the output
                lines = netstat_result.stdout.strip().split('\n')
                for line in lines:
                    if f":{port}" in line and ("LISTENING" in line or "TIME_WAIT" in line):
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            pid = parts[-1]
                            print_info(f"Found process with PID {pid} using port {port}")
                            
                            # Kill the process
                            kill_cmd = ["taskkill", "/F", "/PID", pid]
                            kill_result = subprocess.run(kill_cmd, capture_output=True, text=True)
                            
                            if kill_result.returncode == 0:
                                print_success(f"Successfully killed process with PID {pid}")
                                return True
                            else:
                                print_error(f"Failed to kill process: {kill_result.stderr}")
        else:
            # Unix-like systems (Linux, macOS)
            # Find process ID using the port
            find_pid_cmd = ["lsof", "-i", f":{port}"]
            lsof_result = subprocess.run(find_pid_cmd, capture_output=True, text=True)
            
            if lsof_result.stdout:
                # Extract PID from the output
                lines = lsof_result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        pid = parts[1]
                        print_info(f"Found process with PID {pid} using port {port}")
                        
                        # Kill the process
                        kill_cmd = ["kill", "-9", pid]
                        kill_result = subprocess.run(kill_cmd, capture_output=True, text=True)
                        
                        if kill_result.returncode == 0:
                            print_success(f"Successfully killed process with PID {pid}")
                            return True
                        else:
                            print_error(f"Failed to kill process: {kill_result.stderr}")
                            
        return False
    except Exception as e:
        print_error(f"Error killing process on port {port}: {e}")
        return False

def start_http_server():
    """Start the HTTP file server."""
    print_header("Starting HTTP Server")
    
    global HTTP_PORT  # Make HTTP_PORT global so we can modify it
    
    for attempt in range(MAX_PORT_ATTEMPTS):
        try:
            port_to_try = HTTP_PORT + attempt
            print_info(f"Attempting to start HTTP server on port {port_to_try}...")
            
            # Use Python executable from current environment
            python_exe = sys.executable
            
            # Start Python's HTTP server
            http_process = subprocess.Popen(
                [python_exe, "-m", "http.server", str(port_to_try)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            processes.append(http_process)
            
            # Wait a bit to ensure server starts
            time.sleep(1)
            
            # Check if process is still running
            if http_process.poll() is None:
                # Update the global HTTP_PORT to the successful port
                HTTP_PORT = port_to_try
                print_success(f"HTTP server running at http://localhost:{HTTP_PORT}")
                return True
            else:
                stdout, stderr = http_process.communicate()
                if "Address already in use" in stderr:
                    print_info(f"Port {port_to_try} is already in use, attempting to kill the process...")
                    processes.remove(http_process)
                    
                    # Try to kill the process using this port
                    if kill_process_on_port(port_to_try):
                        # Try starting the server on this port again
                        print_info(f"Retrying port {port_to_try} after killing the previous process...")
                        http_process = subprocess.Popen(
                            [python_exe, "-m", "http.server", str(port_to_try)],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )
                        
                        processes.append(http_process)
                        
                        # Wait a bit to ensure server starts
                        time.sleep(1)
                        
                        # Check if process is still running
                        if http_process.poll() is None:
                            # Update the global HTTP_PORT to the successful port
                            HTTP_PORT = port_to_try
                            print_success(f"HTTP server running at http://localhost:{HTTP_PORT}")
                            return True
                        else:
                            stdout, stderr = http_process.communicate()
                            print_info(f"Port {port_to_try} is still in use, trying another port...")
                            processes.remove(http_process)
                    else:
                        print_info(f"Failed to kill process on port {port_to_try}, trying another port...")
                else:
                    print_error(f"HTTP server failed to start:")
                    if stdout:
                        print_error(f"Output: {stdout}")
                    if stderr:
                        print_error(f"Error: {stderr}")
                    return False
        except Exception as e:
            print_error(f"Error starting HTTP server: {e}")
            return False
    
    print_error(f"Failed to find an available port after {MAX_PORT_ATTEMPTS} attempts")
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

def kill_existing_http_servers():
    """Kill any existing Python HTTP servers that might be using ports in the range."""
    print_info("Checking for existing HTTP servers...")
    
    try:
        # Use Python executable from current environment
        python_exe = sys.executable
        
        # Find python processes
        if sys.platform == 'win32':
            # Windows
            find_cmd = ["tasklist", "/fi", "imagename eq python.exe", "/fo", "csv"]
            result = subprocess.run(find_cmd, capture_output=True, text=True)
            
            # Parse tasklist output
            if result.stdout:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    if line:
                        parts = line.strip('"').split('","')
                        if len(parts) >= 2:
                            pid = parts[1]
                            # Check if this process has http.server in its command line
                            try:
                                cmd_check = subprocess.run(
                                    ["wmic", "process", "where", f"processid={pid}", "get", "commandline"],
                                    capture_output=True, text=True
                                )
                                if "http.server" in cmd_check.stdout:
                                    print_info(f"Killing Python HTTP server with PID {pid}")
                                    subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
                            except Exception:
                                pass
        else:
            # Unix-like (Linux, macOS)
            try:
                ps_cmd = ["ps", "-ef"]
                ps_result = subprocess.run(ps_cmd, capture_output=True, text=True)
                
                for line in ps_result.stdout.splitlines():
                    if "http.server" in line and "python" in line:
                        parts = line.split()
                        if len(parts) > 1:
                            pid = parts[1]
                            print_info(f"Killing Python HTTP server with PID {pid}")
                            subprocess.run(["kill", "-9", pid], capture_output=True)
            except Exception:
                pass
                
        print_success("Cleaned up existing HTTP servers")
    except Exception as e:
        print_error(f"Error checking for existing HTTP servers: {e}")

def main():
    """Start both servers and open the login page."""
    print_header("EHR System Server Startup")
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    # Kill any existing HTTP servers
    kill_existing_http_servers()
    
    # Start Login API server
    login_api_success = start_api_server()
    
    # Start Patient API server
    patient_api_success = start_patient_api_server()
    
    # Start HTTP server
    http_success = start_http_server()
    
    if login_api_success and patient_api_success and http_success:
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