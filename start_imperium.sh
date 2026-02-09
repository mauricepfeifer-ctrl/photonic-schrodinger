#!/bin/bash

# MAURICE'S AI EMPIRE - LAUNCH CONTROL
# 🚀 Starts the 1M Agent Swarm Infrastructure via Docker

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                                          ║${NC}"
echo -e "${BLUE}║           🏰 MAURICE'S AI IMPERIUM - INFRASTRUCTURE LAUNCH              ║${NC}"
echo -e "${BLUE}║                                                                          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 1. Check Environment
echo -e "${GREEN}[1/4] Checking Environment...${NC}"
if [ -z "$MOONSHOT_API_KEY" ]; then
    echo -e "${RED}⚠️  MOONSHOT_API_KEY is not set! Agents may fail.${NC}"
    echo "Export it with: export MOONSHOT_API_KEY='sk-...' or add to .env"
else
    echo -e "✅ API Key found."
fi

# 2. Build & Start Docker Stack
echo -e "${GREEN}[2/4] Deploying Swarm Containers...${NC}"

# Ensure agents directory permissions
chmod +x agents/*.py empire_orchestrator.py telegram_bot.py

echo "Running docker-compose up --build -d..."
docker-compose up --build -d

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Infrastructure Deployed Successfully.${NC}"
else
    echo -e "${RED}❌ Docker Deployment Failed! Check logs.${NC}"
    exit 1
fi

# 3. Health Check
echo -e "${GREEN}[3/4] Verify Services...${NC}"
docker-compose ps

# 4. Instructions
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🚀 SYSTEMS ONLINE                                                      ║${NC}"
echo -e "${BLUE}╠════════════════════════════════════════════════════════════════════════╣${NC}"
echo -e "${BLUE}║  📊 Grafana (Monitoring):  http://localhost:3001                        ║${NC}"
echo -e "${BLUE}║  🕸️ n8n (Workflows):       http://localhost:5678                        ║${NC}"
echo -e "${BLUE}║  💬 Open WebUI:            http://localhost:3000                        ║${NC}"
echo -e "${BLUE}║                                                                          ║${NC}"
echo -e "${BLUE}║  📱 Telegram Bot:          Active (Publishing to Redis)                 ║${NC}"
echo -e "${BLUE}║  👉 Monitor Logs:          docker-compose logs -f                       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
