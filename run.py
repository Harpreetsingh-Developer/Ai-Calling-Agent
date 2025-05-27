#!/usr/bin/env python3
"""
Run script for the AI Calling Agent.

This script makes it easy to start the application with the correct settings.
"""

import os
import sys
import argparse
import subprocess

def main():
    """Run the AI Calling Agent."""
    parser = argparse.ArgumentParser(description="Run the AI Calling Agent")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--log-level", type=str, default="info", help="Logging level")
    
    args = parser.parse_args()
    
    print(f"Starting AI Calling Agent on {args.host}:{args.port}")
    
    # Build the command
    cmd = [
        sys.executable, "-m", "uvicorn", "app.main:app",
        "--host", args.host,
        "--port", str(args.port),
        "--log-level", args.log_level
    ]
    
    if args.reload:
        cmd.append("--reload")
    
    # Run the command
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nShutting down AI Calling Agent...")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 