#!/bin/bash
###############################################################################
# MAURICE'S AI EMPIRE - ULTIMATE LAUNCHER
# 
# Connects:
# - Antigravity (local optimization)
# - Kimi 2.5 (cloud reasoning)
# - Dirk Kreuter Sales Engine
# - 1M Agent Empire
# - Revenue Pipeline
# - Grafana Cloud Monitoring
#
# Run: bash launch.sh [test|full]
###############################################################################

set -e

echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                          ║"
echo "║           🚀 MAURICE'S AI EMPIRE - LAUNCHING                            ║"
echo "║                                                                          ║"
echo "║   Antigravity + Kimi 2.5 + 1M Agents + Grafana                          ║"
echo "║                                                                          ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check for Kimi API Key
if [ -z "$MOONSHOT_API_KEY" ]; then
    echo "⚠️  MOONSHOT_API_KEY not set, loading from .zshrc..."
    export MOONSHOT_API_KEY="sk-e57Q5aDfcpXpHkYfgeWCU3xjuqf2ZPoYxhuRH0kEZXGBeoMF"
fi

echo "✅ Kimi API Key: ${MOONSHOT_API_KEY:0:10}..."
echo ""

# Directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"

echo "📁 Working directory: $SCRIPT_DIR"
echo "📝 Logs directory: $LOG_DIR"
echo ""

# Test mode or full mode
MODE="${1:-test}"

if [ "$MODE" == "test" ]; then
    echo "🧪 Running in TEST MODE (10 agents)"
    echo ""
    
    # Run connector test
    echo "1️⃣ Testing Antigravity-Kimi Connector..."
    python3 "$SCRIPT_DIR/antigravity_connector.py" 2>&1 | tee "$LOG_DIR/connector.log" &
    sleep 5
    
    # Run small empire test
    echo ""
    echo "2️⃣ Testing Empire Orchestrator (20 tasks)..."
    python3 "$SCRIPT_DIR/empire_orchestrator.py" 2>&1 | tee "$LOG_DIR/empire.log" &
    sleep 5
    
    # Run pipeline test
    echo ""
    echo "3️⃣ Testing Revenue Pipeline (30 leads)..."
    python3 "$SCRIPT_DIR/revenue_pipeline.py" 2>&1 | tee "$LOG_DIR/pipeline.log"
    
else
    echo "🔥 Running in FULL MODE (1M agents)"
    echo ""
    
    # Start all systems
    python3 "$SCRIPT_DIR/antigravity_connector.py" > "$LOG_DIR/connector.log" 2>&1 &
    PID1=$!
    echo "Started Connector (PID: $PID1)"
    
    python3 "$SCRIPT_DIR/empire_orchestrator.py" > "$LOG_DIR/empire.log" 2>&1 &
    PID2=$!
    echo "Started Empire (PID: $PID2)"
    
    python3 "$SCRIPT_DIR/revenue_pipeline.py" > "$LOG_DIR/pipeline.log" 2>&1 &
    PID3=$!
    echo "Started Pipeline (PID: $PID3)"
    
    echo ""
    echo "All systems running. Check logs:"
    echo "  tail -f $LOG_DIR/*.log"
    echo ""
    echo "Stop all: pkill -f 'antigravity_connector\|empire_orchestrator\|revenue_pipeline'"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║  ✅ EMPIRE LAUNCHED                                                     ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
