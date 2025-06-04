#!/usr/bin/env python3
"""
Start all required API services for the EHR Vue application

This script:
1. Starts the login API on port 8001
2. Starts the patient API (which includes dashboard) on port 8002
3. Starts the records API on port 8003
4. Starts the vaccine API on port 8004
"""

import os
import sys
import subprocess
import time
import signal
import atexit

# Configuration
API_SERVICES = {
    'login_api': {
        'port': 8001,
        'module': 'api.login_api',
        'process': None
    },
    'patient_api': {
        'port': 8002,
        'module': 'api.patient_api',
        'process': None
    },
    'records_api': {
        'port': 8003,
        'module': 'api.records_api',
        'process': None
    },
    'vaccine_api': {
        'port': 8004,
        'module': 'api.vaccine_api',
        'process': None
    }
}

# Global variables
running_processes = []

def cleanup():
    print("\nShutting down all API services...")
    for proc in running_processes:
        if proc and proc.poll() is None:
            try:
                proc.terminate()
                time.sleep(1)
                if proc.poll() is None:
                    proc.kill()
            except:
                pass

def signal_handler(sig, frame):
    cleanup()
    sys.exit(0)

def start_api_service(service_name, config):
    """Start a specific API service"""
    print(f"Starting {service_name} on port {config['port']}...")
    
    # Set up environment variables
    env = os.environ.copy()
    env['PORT'] = str(config['port'])
    
    # Start the API module
    process = subprocess.Popen(
        [sys.executable, '-m', config['module']],
        env=env
    )
    
    running_processes.append(process)
    config['process'] = process
    
    print(f"{service_name} started with PID {process.pid}")
    
    # Wait briefly to allow startup
    time.sleep(1)
    
    # Check if process is still running
    if process.poll() is not None:
        print(f"ERROR: {service_name} failed to start (exit code {process.poll()})!")
        return False
    
    return True

def main():
    """Main function to start all API services"""
    print("EHR API Service Starter")
    print("======================")
    
    # Register signal handlers and cleanup
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    atexit.register(cleanup)
    
    # Start each API service
    for service_name, config in API_SERVICES.items():
        success = start_api_service(service_name, config)
        if not success:
            print(f"Warning: {service_name} could not be started")
    
    print("\nAll API services started. Press Ctrl+C to shutdown.")
    
    # Keep main thread alive while child processes run
    try:
        while any(proc and proc.poll() is None for proc in running_processes):
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()

if __name__ == "__main__":
    main() 