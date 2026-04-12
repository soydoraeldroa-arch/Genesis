#!/usr/bin/env python3
"""
Terminal Agent: A quick and effective command executor that runs in the terminal.
It reads commands from stdin (can be piped from chat), executes them, and handles errors.
"""

import subprocess
import sys
import shlex

def run_command(cmd):
    """Execute a shell command and return success."""
    try:
        result = subprocess.run(shlex.split(cmd), capture_output=True, text=True, timeout=30)
        print("Output:", result.stdout)
        if result.stderr:
            print("Error:", result.stderr)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("Command timed out.")
        return False
    except Exception as e:
        print(f"Error executing command: {e}")
        return False

def main():
    print("Terminal Agent started. Enter commands (one per line). Type 'exit' to quit.")
    for line in sys.stdin:
        cmd = line.strip()
        if cmd.lower() == 'exit':
            break
        if cmd:
            print(f"Executing: {cmd}")
            success = run_command(cmd)
            if not success:
                print("Command failed. Adjusting... (retrying with sudo if appropriate)")
                # Simple adjustment: if failed, try with sudo
                if not cmd.startswith('sudo '):
                    run_command(f"sudo {cmd}")
                else:
                    print("Still failed. Please check the command.")

if __name__ == "__main__":
    main()