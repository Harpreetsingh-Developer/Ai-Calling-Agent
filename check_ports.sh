#!/bin/bash
# Script to check ports 8000 and 8080 and kill any processes using them

echo "Checking ports 8000 and 8080..."

# Check port 8000
echo "Port 8000:"
lsof -i :8000

# Check port 8080
echo "Port 8080:"
lsof -i :8080

echo "Would you like to kill processes using these ports? (y/n)"
read response

if [ "$response" = "y" ]; then
    # Kill processes using port 8000
    echo "Killing processes on port 8000..."
    kill $(lsof -t -i:8000) 2>/dev/null || echo "No processes using port 8000"
    
    # Kill processes using port 8080
    echo "Killing processes on port 8080..."
    kill $(lsof -t -i:8080) 2>/dev/null || echo "No processes using port 8080"
    
    echo "Processes killed."
else
    echo "No processes killed."
fi 