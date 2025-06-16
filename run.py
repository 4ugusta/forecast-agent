#!/usr/bin/env python3
"""
Direct run script for the Forecast Agent.
This script uses the Python executable from the virtual environment directly.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    # Get project directory and virtual environment Python path
    project_dir = Path(__file__).parent.absolute()
    venv_python = project_dir / "venv" / "bin" / "python"
    
    # Check if venv Python exists
    if not venv_python.exists():
        print(f"Error: Virtual environment Python not found at {venv_python}")
        print("Please run setup.sh first to create the virtual environment.")
        return 1
    
    # Get main.py path
    main_script = project_dir / "main.py"
    if not main_script.exists():
        print(f"Error: Main script not found at {main_script}")
        return 1
    
    # Build the command with all arguments passed to this script
    cmd = [str(venv_python), str(main_script)] + sys.argv[1:]
    
    # Print the command we're going to run
    print(f"Running: {' '.join(cmd)}")
    
    # Execute the command
    return subprocess.call(cmd)

if __name__ == "__main__":
    sys.exit(main())
