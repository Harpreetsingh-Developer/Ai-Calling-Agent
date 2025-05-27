#!/usr/bin/env python3
"""
Setup script for the AI Calling Agent.

This script helps users prepare the environment and test the TTS functionality.
It:
1. Creates necessary directories it importnat for the application
2. Tests the TTS functionality
3. Reports any issues
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

def create_directories():
    """Create necessary directories for the application."""
    print("Creating necessary directories...")
    
    # Create directories
    dirs = [
        "app/services/tts/models",
        "app/services/tts/models/hindi_female",
        "app/services/tts/models/marathi_female",
        "app/services/tts/models/telugu_female",
        "logs"
    ]
    
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)
        print(f"  Created: {directory}")
    
    print("Directory setup complete.")

def install_dependencies(extra_deps=False):
    """Install Python dependencies."""
    print("Installing Python dependencies...")
    
    cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Error installing dependencies:")
        print(result.stderr)
        return False
    
    print("Base dependencies installed successfully.")
    
    # Install extra dependencies if requested
    if extra_deps:
        print("Installing extra dependencies for better TTS support...")
        extra_pkgs = ["modelscope"]
        cmd = [sys.executable, "-m", "pip", "install"] + extra_pkgs
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print("Warning: Error installing extra dependencies:")
            print(result.stderr)
            print("The application will still function but with limited TTS capabilities.")
            return True
        
        print("Extra dependencies installed successfully.")
    
    return True

def test_tts():
    """Test the TTS functionality."""
    print("Testing TTS functionality...")
    
    # Run the TTS test script
    cmd = [sys.executable, "tests/test_tts.py", "--languages", "en", "--engines", "google"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Error testing TTS:")
        print(result.stderr)
        return False
    
    print("TTS basic test completed. Check the test_outputs directory for the generated audio files.")
    return True

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Setup script for AI Calling Agent")
    parser.add_argument("--skip-deps", action="store_true", help="Skip installing dependencies")
    parser.add_argument("--extra-deps", action="store_true", help="Install extra dependencies for better TTS support")
    parser.add_argument("--skip-test", action="store_true", help="Skip TTS testing")
    
    args = parser.parse_args()
    
    print("=== AI Calling Agent Setup ===")
    
    # Create directories
    create_directories()
    
    # Install dependencies if not skipped
    if not args.skip_deps:
        if not install_dependencies(args.extra_deps):
            print("Setup failed due to dependency installation issues.")
            return 1
    
    # Test TTS if not skipped
    if not args.skip_test:
        if not test_tts():
            print("Setup completed with warnings (TTS test failed).")
            return 1
    
    print("\nSetup completed successfully!")
    print("\nTo run the application:")
    print("  uvicorn app.main:app --reload")
    print("\nThe application will be available at http://localhost:8000")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 