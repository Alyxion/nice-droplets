#!/usr/bin/env python3
import os
import sys
import time
import signal
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"example_tests_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

def find_example_apps():
    """Find all example apps in the examples directory."""
    examples_dir = Path("examples")
    example_apps = []
    
    for app_dir in examples_dir.iterdir():
        if app_dir.is_dir():
            main_file = app_dir / "main.py"
            if main_file.exists():
                example_apps.append(app_dir)
    
    return sorted(example_apps)

def kill_process(process):
    """Kill a process and its children."""
    if process:
        try:
            # Send SIGTERM to process group
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        except ProcessLookupError:
            pass  # Process already terminated
        except Exception as e:
            logging.error(f"Error killing process: {e}")

def run_example(app_dir: Path, timeout: int = 10):
    """Run an example app and log any errors."""
    logging.info(f"\n{'='*80}\nTesting {app_dir.name}")
    
    try:
        # Start the process in a new process group
        process = subprocess.Popen(
            ["poetry", "run", "python", "main.py"],
            cwd=app_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid  # Create new process group
        )
        
        # Wait briefly to catch immediate startup errors
        try:
            stdout, stderr = process.communicate(timeout=2)
            if process.returncode != 0:
                logging.error(f"Error running {app_dir.name}:")
                if stdout:
                    logging.error(f"stdout: {stdout.decode()}")
                if stderr:
                    logging.error(f"stderr: {stderr.decode()}")
                return None
        except subprocess.TimeoutExpired:
            # Process is still running (expected for GUI apps)
            pass
        
        logging.info(f"{app_dir.name} started successfully")
        
        # Wait for specified timeout
        time.sleep(timeout)
        return process
        
    except Exception as e:
        logging.error(f"Error running {app_dir.name}: {e}")
        return None

def main():
    example_apps = find_example_apps()
    if not example_apps:
        logging.error("No example apps found!")
        return
    
    current_process = None
    try:
        for app_dir in example_apps:
            # Kill previous process if it exists
            if current_process:
                logging.info(f"Stopping previous example")
                kill_process(current_process)
                current_process = None
            
            # Run new example
            current_process = run_example(app_dir)
    
    finally:
        # Cleanup on exit
        if current_process:
            logging.info("Cleaning up processes")
            kill_process(current_process)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("\nTest run interrupted by user")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        logging.info(f"\nLogs written to: {log_file}")
