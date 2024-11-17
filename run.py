#!/usr/bin/env python3
"""
SeekerLight launcher script - starts Voilà server and opens the web application
"""
import os
import sys
import subprocess
import webbrowser
from time import sleep

def main():
    try:
        print("Starting SeekerLight...")
        
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"Working directory: {script_dir}")
        
        # Path to the notebook
        notebook_path = os.path.join(script_dir, 'app.ipynb')
        if not os.path.exists(notebook_path):
            raise FileNotFoundError(f"Notebook not found at: {notebook_path}")
            
        print(f"Found notebook at: {notebook_path}")
        
        # Get the voila executable
        voila_cmd = os.path.join(script_dir, 'venv', 'bin', 'voila')
        if not os.path.exists(voila_cmd):
            raise FileNotFoundError(f"Voilà not found at: {voila_cmd}")
        
        # Start Voilà server
        cmd = [
            voila_cmd,
            notebook_path,
            '--no-browser',
            '--port=8866'
        ]
        
        print(f"Starting Voilà server...")
        process = subprocess.Popen(cmd)
        
        # Give the server time to start
        print("Waiting for server to start...")
        sleep(3)
        
        # Open browser
        url = "http://localhost:8866"
        print(f"Opening {url}")
        webbrowser.open(url)
        
        print("\nPress Ctrl+C to stop the server")
        process.wait()
        
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
