#!/usr/bin/env python3
"""
EHR Server Manager - Manages all EHR services with proper port allocation

This script:
1. Kills any processes using the required ports
2. Starts all required servers with proper port allocation
3. Provides clean shutdown of all services
"""

import os
import sys
import subprocess
import signal
import time
import psutil
import socket
import logging
from datetime import datetime

# Configure logging
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, f'ehr_servers_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('ehr_server_manager')

# Server configuration
SERVER_CONFIG = {
    'main_api': {
        'port': 8000,
        'script': 'start_server_with_logging.py',
        'process': None,
        'required': True
    },
    'vaccine_api': {
        'port': 8004,
        'script': 'start_vaccine_server.py',
        'process': None,
        'required': True
    },
    'frontend': {
        'port': 8081,
        'command': ['npm', 'run', 'dev'],
        'cwd': '../ehr-vue-app',
        'process': None,
        'required': True
    }
}

# Global variables
running = True
servers_started = False

def is_port_in_use(port):
    """Check if a port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def kill_process_on_port(port):
    """Kill any process using the specified port."""
    if not is_port_in_use(port):
        logger.info(f"Port {port} is not in use.")
        return True
    
    logger.info(f"Port {port} is in use. Attempting to kill the process...")
    
    try:
        if sys.platform.startswith('win'):
            # Windows
            result = subprocess.run(
                ['netstat', '-ano', '|', 'findstr', f':{port}'],
                capture_output=True,
                text=True,
                shell=True
            )
            
            if result.stdout:
                # Parse the output to get the PID
                for line in result.stdout.splitlines():
                    if f':{port}' in line:
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            pid = int(parts[-1])
                            try:
                                process = psutil.Process(pid)
                                process_name = process.name()
                                logger.info(f"Killing process {process_name} (PID: {pid}) using port {port}")
                                process.terminate()
                                # Give it time to terminate
                                time.sleep(1)
                                if process.is_running():
                                    process.kill()
                                return True
                            except psutil.NoSuchProcess:
                                logger.warning(f"Process with PID {pid} not found")
            
            logger.warning(f"Could not find process using port {port}")
            return False
            
        else:
            # Unix-like systems
            result = subprocess.run(
                ['lsof', '-i', f':{port}', '-t'],
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                for pid_str in result.stdout.splitlines():
                    try:
                        pid = int(pid_str)
                        process = psutil.Process(pid)
                        process_name = process.name()
                        logger.info(f"Killing process {process_name} (PID: {pid}) using port {port}")
                        process.terminate()
                        # Give it time to terminate
                        time.sleep(1)
                        if process.is_running():
                            process.kill()
                    except (ValueError, psutil.NoSuchProcess):
                        logger.warning(f"Could not kill process with PID {pid_str}")
                
                return True
            
            logger.warning(f"Could not find process using port {port}")
            return False
            
    except Exception as e:
        logger.error(f"Error killing process on port {port}: {e}")
        return False

def cleanup_ports():
    """Free up all required ports."""
    all_ports_cleared = True
    
    for server_name, config in SERVER_CONFIG.items():
        port = config['port']
        if not kill_process_on_port(port):
            all_ports_cleared = False
            if config['required']:
                logger.error(f"Could not free required port {port} for {server_name}")
    
    return all_ports_cleared

def start_servers():
    """Start all required servers."""
    global servers_started
    
    # Start backend servers
    for server_name, config in SERVER_CONFIG.items():
        if server_name == 'frontend':
            continue  # We'll start the frontend last
            
        port = config['port']
        if is_port_in_use(port):
            logger.error(f"Port {port} for {server_name} is still in use. Skipping server start.")
            if config['required']:
                return False
            continue
        
        try:
            logger.info(f"Starting {server_name} on port {port}")
            
            # Start the server as a subprocess
            process = subprocess.Popen(
                [sys.executable, config['script']],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            config['process'] = process
            
            # Wait a moment to ensure the server starts
            time.sleep(2)
            
            # Check if the process is still running
            if process.poll() is not None:
                logger.error(f"Failed to start {server_name}. Process exited with code {process.poll()}")
                if config['required']:
                    return False
            else:
                logger.info(f"{server_name} started successfully on port {port}")
                
        except Exception as e:
            logger.error(f"Error starting {server_name}: {e}")
            if config['required']:
                return False
    
    # Start frontend server
    frontend_config = SERVER_CONFIG['frontend']
    try:
        logger.info(f"Starting frontend on port {frontend_config['port']}")
        
        env = os.environ.copy()
        # Set environment variables for the Vue app to use the correct ports
        env['VITE_API_BASE_URL'] = f"http://localhost:{SERVER_CONFIG['main_api']['port']}"
        env['VITE_VACCINE_API_URL'] = f"http://localhost:{SERVER_CONFIG['vaccine_api']['port']}"
        
        # Start the Vue development server
        process = subprocess.Popen(
            frontend_config['command'],
            cwd=os.path.abspath(frontend_config['cwd']),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=env
        )
        
        frontend_config['process'] = process
        
        # Wait a moment to ensure the server starts
        time.sleep(3)
        
        # Check if the process is still running
        if process.poll() is not None:
            logger.error(f"Failed to start frontend. Process exited with code {process.poll()}")
            if frontend_config['required']:
                return False
        else:
            logger.info(f"Frontend started successfully on port {frontend_config['port']}")
            
    except Exception as e:
        logger.error(f"Error starting frontend: {e}")
        if frontend_config['required']:
            return False
    
    servers_started = True
    return True

def monitor_processes():
    """Monitor running processes and log their output."""
    while running:
        for server_name, config in SERVER_CONFIG.items():
            process = config.get('process')
            if process and process.poll() is None:
                try:
                    # Read output without blocking
                    while True:
                        output = process.stdout.readline()
                        if not output:
                            break
                        logger.info(f"{server_name}: {output.strip()}")
                except Exception as e:
                    logger.error(f"Error reading output from {server_name}: {e}")
        
        # Check if any required processes have died
        for server_name, config in SERVER_CONFIG.items():
            process = config.get('process')
            if config['required'] and process and process.poll() is not None:
                logger.error(f"Required process {server_name} has died with exit code {process.poll()}")
                return False
        
        time.sleep(0.1)
    
    return True

def stop_servers():
    """Stop all running servers."""
    for server_name, config in SERVER_CONFIG.items():
        process = config.get('process')
        if process and process.poll() is None:
            logger.info(f"Stopping {server_name}...")
            try:
                process.terminate()
                # Give it a moment to terminate gracefully
                time.sleep(1)
                
                # If it's still running, force kill
                if process.poll() is None:
                    logger.info(f"Forcing {server_name} to stop...")
                    process.kill()
            except Exception as e:
                logger.error(f"Error stopping {server_name}: {e}")

def signal_handler(sig, frame):
    """Handle interrupt signals."""
    global running
    logger.info("Shutdown signal received. Stopping servers...")
    running = False
    stop_servers()
    sys.exit(0)

def main():
    """Main function to run the server manager."""
    logger.info("EHR Server Manager starting...")
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Clean up ports
    logger.info("Cleaning up ports...")
    if not cleanup_ports():
        logger.error("Failed to clean up all required ports. Please check manually.")
        return 1
    
    # Start servers
    logger.info("Starting servers...")
    if not start_servers():
        logger.error("Failed to start all required servers.")
        stop_servers()
        return 1
    
    # Print access information
    logger.info("\n" + "="*60)
    logger.info("EHR SYSTEM RUNNING")
    logger.info("="*60)
    logger.info(f"Frontend: http://localhost:{SERVER_CONFIG['frontend']['port']}")
    logger.info(f"Main API: http://localhost:{SERVER_CONFIG['main_api']['port']}")
    logger.info(f"Vaccine API: http://localhost:{SERVER_CONFIG['vaccine_api']['port']}")
    logger.info("Press Ctrl+C to stop all servers")
    logger.info("="*60 + "\n")
    
    # Monitor processes
    try:
        monitor_processes()
    except KeyboardInterrupt:
        logger.info("Interrupted by user. Shutting down...")
    finally:
        stop_servers()
    
    logger.info("EHR Server Manager stopped.")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 