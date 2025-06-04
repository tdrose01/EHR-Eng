#!/usr/bin/env python
"""
Utility script to kill processes using specific ports
"""

import os
import sys
import subprocess
from colorama import init, Fore, Style

# Initialize colorama for colored output
init()

# Ports to check
PORTS = list(range(8000, 8090))  # Ports 8000-8089

def print_success(message):
    """Print a success message."""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def print_error(message):
    """Print an error message."""
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")

def print_info(message):
    """Print an info message."""
    print(f"{Fore.YELLOW}ℹ {message}{Style.RESET_ALL}")

def kill_process_on_port(port):
    """Kill the process using the specified port."""
    print_info(f"Checking port {port}...")
    
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
                return False
            else:
                print_info(f"No process found using port {port}")
                return False
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
            else:
                print_info(f"No process found using port {port}")
                return False
    except Exception as e:
        print_error(f"Error checking port {port}: {e}")
        return False

def kill_python_http_servers():
    """Kill any Python HTTP server processes."""
    print_info("Checking for Python HTTP servers...")
    
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
    except Exception as e:
        print_error(f"Error checking for Python HTTP servers: {e}")

def main():
    """Check and kill processes on specified ports."""
    print(f"{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'Kill Server Processes'.center(70)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}\n")
    
    # Kill Python HTTP servers first
    kill_python_http_servers()
    
    # Check each port
    for port in PORTS:
        kill_process_on_port(port)
    
    print(f"\n{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'Completed'.center(70)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}\n")

if __name__ == "__main__":
    main() 