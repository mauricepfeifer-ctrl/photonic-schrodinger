#!/bin/bash

# Mission Control Status Script
# Reads from ../registry/services.yaml
# Usage: ./mc_status.sh [--json]

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REGISTRY="$BASE_DIR/registry/services.yaml"
JSON_MODE=0

if [ "$1" == "--json" ]; then
    JSON_MODE=1
fi

if [ $JSON_MODE -eq 0 ]; then
    echo "=== MISSION CONTROL STATUS ==="
    echo "Registry: $REGISTRY"
    echo "------------------------------"
    printf "%-15s | %-8s | %-20s\n" "SERVICE" "STATUS" "PORT"
    echo "--------------------------------------------------------"
else
    echo "["
fi

current_name=""
current_port=""
current_check=""
first_json_entry=1

while IFS= read -r line; do
    # Trim whitespace
    line=$(echo "$line" | sed 's/^[ \t]*//')
    
    if [[ $line == name:* ]]; then
        current_name=$(echo "$line" | cut -d'"' -f2)
    elif [[ $line == port:* ]]; then
        current_port=$(echo "$line" | awk '{print $2}')
    elif [[ $line == healthcheck:* ]]; then
        current_check=$(echo "$line" | cut -d'"' -f2)
        
        # We have a block, execute check
        if [ -n "$current_name" ]; then
            if [ -n "$current_check" ]; then
                eval "$current_check" > /dev/null 2>&1
                if [ $? -eq 0 ]; then
                    status="UP"
                    color="\033[32m" # Green
                else
                    status="DOWN"
                    color="\033[31m" # Red
                fi
            else
                status="UNKNOWN"
                color="\033[33m" # Yellow
            fi
            
            if [ $JSON_MODE -eq 0 ]; then
                nc="\033[0m" # No Color
                printf "${color}%-15s${nc} | ${color}%-8s${nc} | %-20s\n" "$current_name" "$status" "$current_port"
            else
                if [ $first_json_entry -eq 1 ]; then
                    first_json_entry=0
                else
                    echo ","
                fi
                echo "  {"
                echo "    \"name\": \"$current_name\","
                echo "    \"status\": \"$status\","
                echo "    \"port\": \"$current_port\""
                echo "  }"
            fi
        fi
        
        # Reset for next
        current_name=""
        current_port=""
        current_check=""
    fi
done < "$REGISTRY"

if [ $JSON_MODE -eq 0 ]; then
    echo "--------------------------------------------------------"
else
    echo "]"
fi
