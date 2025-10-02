#!/usr/bin/env python3
"""
Launcher script for A1111 Prompt Generator
This ensures the application finds all its resources correctly.
"""
import os
import sys
from pathlib import Path

def add_app_to_path():
    """Add the application directory to the Python path."""
    app_dir = str(Path(__file__).parent.absolute())
    if app_dir not in sys.path:
        sys.path.insert(0, app_dir)

def ensure_directories():
    """Ensure all required directories exist."""
    directories = ['data', 'profiles', 'output']
    for dir_name in directories:
        os.makedirs(dir_name, exist_ok=True)

def main():
    # Set up paths and environment
    add_app_to_path()
    ensure_directories()
    
    # Set the working directory to the script's directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Import and run the main application
    try:
        from main import main as app_main
        app_main()
    except ImportError as e:
        print(f"Error: {e}")
        print("\nPlease make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
