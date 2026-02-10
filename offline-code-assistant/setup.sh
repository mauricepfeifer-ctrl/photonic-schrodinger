#!/bin/bash
# ============================================================
#  🧠 OFFLINE CODE ASSISTANT - Vollständig Kostenlos
#  Setup Script für Apple M4 / 16GB RAM
# ============================================================

set -e

BOLD="\033[1m"
GREEN="\033[0;32m"
CYAN="\033[0;36m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m"

echo -e "${BOLD}${CYAN}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║  🧠 OFFLINE AI CODE ASSISTANT - Setup               ║"
echo "║  100% Kostenlos • 100% Offline • 100% Privat        ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ---- 1. Check Ollama ----
echo -e "${BOLD}[1/4] Checking Ollama...${NC}"
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✅ Ollama ist installiert: $(ollama --version)${NC}"
else
    echo -e "${YELLOW}📦 Installiere Ollama...${NC}"
    brew install ollama
fi

# Ensure Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo -e "${YELLOW}🔄 Starte Ollama Server...${NC}"
    ollama serve &
    sleep 3
fi

# ---- 2. Pull Models (optimiert für M4/16GB) ----
echo -e "\n${BOLD}[2/4] Downloading AI Models...${NC}"
echo -e "${CYAN}Optimiert für Apple M4 / 16GB RAM${NC}\n"

MODELS=(
    "qwen2.5-coder:7b"      # Bester Coding-Modell - 4.7GB
    "llama3.1:8b"            # Allround-Talent - 4.7GB  
    "deepseek-r1:8b"         # Deep Reasoning - 5.2GB
    "codellama:7b"           # Meta's Code-Spezialist - 3.8GB
    "starcoder2:7b"          # Code Completion - 3.8GB
)

for model in "${MODELS[@]}"; do
    echo -e "${CYAN}📥 Pulling ${model}...${NC}"
    ollama pull "$model" 2>&1 | tail -1
    echo -e "${GREEN}✅ ${model} ready${NC}"
done

# ---- 3. Install Aider (AI Coding Assistant) ----
echo -e "\n${BOLD}[3/4] Installing Aider AI Coding Assistant...${NC}"

AIDER_ENV="$HOME/.local/aider-env"
if [ -f "$AIDER_ENV/bin/aider" ]; then
    echo -e "${GREEN}✅ Aider bereits installiert${NC}"
else
    echo -e "${CYAN}📦 Erstelle Python venv und installiere Aider...${NC}"
    python3 -m venv "$AIDER_ENV"
    source "$AIDER_ENV/bin/activate"
    pip install --upgrade pip
    pip install aider-chat
    deactivate
    echo -e "${GREEN}✅ Aider installiert in $AIDER_ENV${NC}"
fi

# ---- 4. Create Launcher Scripts ----
echo -e "\n${BOLD}[4/4] Creating Launcher Scripts...${NC}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Shell aliases
SHELL_CONFIG="$HOME/.zshrc"
if ! grep -q "# OFFLINE AI CODE ASSISTANT" "$SHELL_CONFIG" 2>/dev/null; then
    cat >> "$SHELL_CONFIG" << 'ALIASES'

# OFFLINE AI CODE ASSISTANT - 100% Free & Offline
export OLLAMA_API_BASE="http://127.0.0.1:11434"
alias ai-code='$HOME/.local/aider-env/bin/aider --model ollama_chat/qwen2.5-coder:7b'
alias ai-think='$HOME/.local/aider-env/bin/aider --model ollama_chat/deepseek-r1:8b'
alias ai-llama='$HOME/.local/aider-env/bin/aider --model ollama_chat/llama3.1:8b'
alias ai-pair='$HOME/.local/aider-env/bin/aider --model ollama_chat/qwen2.5-coder:7b --architect --editor-model ollama_chat/codellama:7b'
ALIASES
    echo -e "${GREEN}✅ Shell-Aliases erstellt${NC}"
fi

echo -e "\n${BOLD}${GREEN}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║  ✅ SETUP COMPLETE!                                  ║"
echo "║                                                      ║"
echo "║  Starte mit:                                         ║"
echo "║    ai-code  → Qwen Coder (bester für Code)          ║"
echo "║    ai-think → DeepSeek R1 (Reasoning & Planung)     ║"
echo "║    ai-llama → Llama 3.1 (Allround-Talent)           ║"
echo "║    ai-pair  → Architect Mode (2 Modelle)             ║"
echo "║                                                      ║"
echo "║  Oder direkt:                                        ║"
echo "║    cd dein-projekt                                   ║"
echo "║    ai-code                                           ║"
echo "║                                                      ║"
echo "║  100% OFFLINE • 100% KOSTENLOS • 100% PRIVAT        ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"
