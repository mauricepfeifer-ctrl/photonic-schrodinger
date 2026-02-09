#!/bin/bash

# MONSTER MACHINE CLOUD MANAGER
# Moves generated content to iCloud and deletes local copies to save space.

# Config
SOURCE_DIR_X="x_content"
SOURCE_DIR_SWARM="swarm_output"
# Standard iCloud Drive path
ICLOUD_BASE="$HOME/Library/Mobile Documents/com~apple~CloudDocs/AI_Empire_Monster"

echo "========================================"
echo "☁️  MONSTER CLOUD SYNC"
echo "========================================"

# Ensure iCloud dirs exist
mkdir -p "$ICLOUD_BASE/x_content"
mkdir -p "$ICLOUD_BASE/swarm_output"

# Function to move files
move_to_cloud() {
    local src="$1"
    local dest="$2"
    
    if [ -d "$src" ]; then
        echo "🔄 Processing $src..."
        # Rsync with --remove-source-files to delete local after transfer
        # -a: archive mode
        # -v: verbose
        # --remove-source-files: DELETE successfully transferred files from source
        rsync -av --remove-source-files "$src/" "$dest/"
        
        # Clean up empty directories
        find "$src" -type d -empty -delete
        # Recreate source dir for next batch
        mkdir -p "$src"
    else
        echo "⚠️  Source $src not found, skipping."
    fi
}

# Run Sync
move_to_cloud "$SOURCE_DIR_X" "$ICLOUD_BASE/x_content"
move_to_cloud "$SOURCE_DIR_SWARM" "$ICLOUD_BASE/swarm_output"

echo "========================================"
echo "✅ Cloud Offload Complete!"
echo "🗑  Local files removed to save space."
echo "========================================"
