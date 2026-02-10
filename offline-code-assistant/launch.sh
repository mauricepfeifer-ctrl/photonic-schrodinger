#!/bin/bash
# ============================================================
#  🚀 OFFLINE CODE ASSISTANT - Quick Launcher
#  Wähle dein Modell und leg los!
# ============================================================

BOLD="\033[1m"
GREEN="\033[0;32m"
CYAN="\033[0;36m"
YELLOW="\033[1;33m"
MAGENTA="\033[0;35m"
NC="\033[0m"

AIDER="$HOME/.local/aider-env/bin/aider"
export OLLAMA_API_BASE="http://127.0.0.1:11434"

# Ensure Ollama is running
if ! pgrep -x "ollama" > /dev/null 2>&1; then
    echo -e "${YELLOW}🔄 Starte Ollama Server...${NC}"
    ollama serve &>/dev/null &
    sleep 2
fi

echo -e "${BOLD}${CYAN}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║  🧠 OFFLINE AI CODE ASSISTANT                       ║"
echo "║  100% Free • 100% Offline • 100% Private            ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║                                                      ║"
echo "║  [1] 🔥 Qwen2.5 Coder    - Bestes Code-Modell      ║"
echo "║  [2] 🧠 DeepSeek R1      - Deep Thinking & Planning║"
echo "║  [3] 🦙 Llama 3.1        - Allround-Talent          ║"
echo "║  [4] 💻 CodeLlama        - Code-Spezialist          ║"
echo "║  [5] ⭐ StarCoder2       - Code Completion          ║"
echo "║  [6] 🏗️ Architect Mode   - 2 Modelle (Denken+Code) ║"
echo "║  [7] 🗨️ Chat Only        - Nur Chat, kein Code-Edit ║"
echo "║                                                      ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"

read -p "Wähle [1-7]: " choice

case $choice in
    1)
        echo -e "\n${GREEN}🔥 Starte Qwen2.5 Coder...${NC}\n"
        $AIDER --model ollama_chat/qwen2.5-coder:7b "$@"
        ;;
    2)
        echo -e "\n${GREEN}🧠 Starte DeepSeek R1...${NC}\n"
        $AIDER --model ollama_chat/deepseek-r1:8b "$@"
        ;;
    3)
        echo -e "\n${GREEN}🦙 Starte Llama 3.1...${NC}\n"
        $AIDER --model ollama_chat/llama3.1:8b "$@"
        ;;
    4)
        echo -e "\n${GREEN}💻 Starte CodeLlama...${NC}\n"
        $AIDER --model ollama_chat/codellama:7b "$@"
        ;;
    5)
        echo -e "\n${GREEN}⭐ Starte StarCoder2...${NC}\n"
        $AIDER --model ollama_chat/starcoder2:7b "$@"
        ;;
    6)
        echo -e "\n${GREEN}🏗️ Starte Architect Mode (Qwen denkt, CodeLlama codet)...${NC}\n"
        $AIDER --model ollama_chat/qwen2.5-coder:7b \
               --architect \
               --editor-model ollama_chat/codellama:7b "$@"
        ;;
    7)
        echo -e "\n${GREEN}🗨️ Chat Modus...${NC}\n"
        echo -e "Welches Modell? (z.B. llama3.1:8b)"
        read -p "> " model
        ollama run "$model"
        ;;
    *)
        echo -e "${YELLOW}Standard: Qwen2.5 Coder${NC}"
        $AIDER --model ollama_chat/qwen2.5-coder:7b "$@"
        ;;
esac
