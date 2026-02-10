#!/bin/bash

# Mission Control Logs Script
# Usage: ./mc_logs.sh <service_name>

SERVICE=$1
BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REGISTRY="$BASE_DIR/registry/services.yaml"

if [ -z "$SERVICE" ]; then
    echo "Usage: $0 <service_name>"
    exit 1
fi

# Find log command
# Quick and dirty parser to find the block for the service
# We search for 'name: "SERVICE"', then look for 'logs:' in subsequent lines

found=0
log_cmd=""

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
        if [[ $clean_line == logs:* ]]; then
            log_cmd=$(echo "$clean_line" | cut -d'"' -f2)
            break
        fi
    fi
done < "$REGISTRY"

if [ -n "$log_cmd" ]; then
    echo "Tailing logs for $SERVICE..."
    echo "Command: $log_cmd"
    eval "$log_cmd"
else
    echo "No log command found for service: $SERVICE (or service not found)"
    exit 1
fi
