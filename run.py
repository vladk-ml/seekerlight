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
        
        # Get the directory containing this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Get the notebook path
        notebook_path = os.path.join(script_dir, 'app.ipynb')
        
        # Check if notebook exists
        if not os.path.exists(notebook_path):
            raise FileNotFoundError(f"Notebook not found at: {notebook_path}")
            
        print(f"Found notebook at: {notebook_path}")
        
        # Create static directory if it doesn't exist
        static_dir = os.path.join(script_dir, 'static')
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
        
        # Get the voila executable from virtual environment
        voila_cmd = os.path.join(script_dir, 'venv', 'bin', 'voila')
        if not os.path.exists(voila_cmd):
            raise FileNotFoundError(f"Voilà not found at: {voila_cmd}")
        
        # Start Voilà server
        cmd = [
            voila_cmd,
            notebook_path,
            '--Voila.ip=0.0.0.0',
            '--Voila.port=8866',
            '--no-browser',
            '--enable_nbextensions=True',
            f'--Voila.static_root={static_dir}'
        ]
        
        print(f"Starting Voilà server...")
        process = subprocess.Popen(cmd)
        
        # Wait a bit for the server to start
        sleep(2)
        
        # Open the browser
        webbrowser.open('http://localhost:8866')
        
        print("Server started! Opening browser...")
        print("Press Ctrl+C to stop the server.")
        
        # Keep the script running
        process.wait()
        
    except KeyboardInterrupt:
        print("\nShutting down server...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
