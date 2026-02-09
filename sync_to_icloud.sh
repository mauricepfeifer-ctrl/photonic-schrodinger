#!/bin/bash

# Configuration
SOURCE_DIR="swarm_output"
# Standard iCloud Drive path
ICLOUD_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/AI_Empire_Swarm"

echo "========================================"
echo "☁️  ICLOUD SYNC"
echo "========================================"

# ensure output dir exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ Source directory $SOURCE_DIR not found!"
    exit 1
fi

# Create iCloud destination
mkdir -p "$ICLOUD_DIR"

echo "📂 Source: $SOURCE_DIR"
echo "📂 Dest:   $ICLOUD_DIR"

# Sync
# using rsync for efficiency
rsync -av --progress "$SOURCE_DIR/" "$ICLOUD_DIR/"

echo "========================================"
echo "✅ Sync Complete!"
echo "📱 Check your iPhone 'Files' app -> iCloud Drive -> AI_Empire_Swarm"
echo "========================================"
