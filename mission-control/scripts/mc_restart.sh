#!/bin/bash

# Mission Control Restart Script
# Usage: ./mc_restart.sh <service_name>

SERVICE=$1
BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REGISTRY="$BASE_DIR/registry/services.yaml"

if [ -z "$SERVICE" ]; then
    echo "Usage: $0 <service_name>"
    exit 1
fi

found=0
start_cmd=""
stop_cmd=""

while IFS= read -r line; do
    clean_line=$(echo "$line" | sed 's/^[ \t]*//')
    
    if [[ $clean_line == name:* ]]; then
        current_name=$(echo "$clean_line" | cut -d'"' -f2)
        if [ "$current_name" == "$SERVICE" ]; then
            found=1
        else
            found=0
        fi
    fi
    
    if [ $found -eq 1 ]; then
        if [[ $clean_line == start_cmd:* ]]; then
            start_cmd=$(echo "$clean_line" | cut -d'"' -f2)
        elif [[ $clean_line == stop_cmd:* ]]; then
            stop_cmd=$(echo "$clean_line" | cut -d'"' -f2)
        fi
        
        # If we have both, we can break early if we assume order, but let's be safe and read until next name or EOF
        # Actually yaml might not be ordered. But for this simple parser we assume the block is contiguous.
    fi
done < "$REGISTRY"

if [ -n "$stop_cmd" ] && [ -n "$start_cmd" ]; then
    echo "Restarting $SERVICE..."
    echo "Stopping: $stop_cmd"
    eval "$stop_cmd"
    
    echo "Waiting 2 seconds..."
    sleep 2
    
    echo "Starting: $start_cmd"
    eval "$start_cmd"
    
    echo "Done."
else
    echo "Could not find start/stop commands for $SERVICE"
    exit 1
fi
