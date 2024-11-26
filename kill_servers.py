#!/usr/bin/env python3
import os
import subprocess
import signal

def kill_voila_servers():
    try:
        # Get all Python processes
        ps = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE).communicate()[0]
        processes = ps.decode().split('\n')
        
        # Find and kill Voilà processes
        killed = False
        for process in processes:
            if 'voila' in process.lower():
                try:
                    pid = int(process.split()[1])
                    os.kill(pid, signal.SIGTERM)
                    print(f"Killed Voilà process with PID: {pid}")
                    killed = True
                except (IndexError, ValueError, ProcessLookupError) as e:
                    continue
        
        if not killed:
            print("No Voilà servers found running")
            
    except Exception as e:
        print(f"Error killing servers: {str(e)}")

if __name__ == "__main__":
    kill_voila_servers()
