#!/bin/bash

# MONSTER MACHINE ORCHESTRATOR
# Runs the entire system: Knowledge -> Content -> Cloud

echo "👹 STARTING MONSTER MACHINE..."

# 1. Harvest Knowledge
echo "🧠 Harvesting Knowledge..."
python3 knowledge_harvester.py

# 2. Generate Content (Run multiple cycles if needed)
echo "📝 Generating X Content..."
python3 x_monster.py

# 3. Offload to Cloud
echo "☁️  Offloading to Cloud..."
bash cloud_manager.sh

echo "✅ MONSTER CYCLE COMPLETE"
