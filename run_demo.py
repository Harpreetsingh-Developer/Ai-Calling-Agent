#!/usr/bin/env python3
"""
Demo run script for the AI Calling Agent.

This script runs the application in demo mode, without requiring MongoDB.
"""

import sys
import subprocess

def main():
    """Run the AI Calling Agent in demo mode."""
    print("Starting AI Calling Agent in DEMO mode (no database required)")
    
    # Build the uvicorn command
    cmd = [
        sys.executable, "-m", "uvicorn", "app.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload",
        "--log-level", "info"
    ]
    
    # Add --no-db flag to be processed by our app
    sys.argv.append("--no-db")
    
    # Run the command
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nShutting down AI Calling Agent...")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 