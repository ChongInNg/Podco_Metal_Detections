#!/bin/bash


SERVER_PID=$(ps aux | grep "[p]ython.*server/main.py" | awk '{print $2}')
if [ -n "$SERVER_PID" ]; then
    echo "Found existing Metal Detection server (PID: $SERVER_PID). Killing it..."
    kill -TERM "$SERVER_PID" 2>/dev/null
    sleep 0.5
else
    echo "No Metal Detection existing server running." 
fi