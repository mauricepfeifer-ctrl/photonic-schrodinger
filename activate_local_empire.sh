#!/bin/bash

# 1. Umgebungsvariablen für "Claude Code" (und andere Tools), um auf Ollama umzuleiten
# Ollama muss laufen (ollama serve)

export ANTHROPIC_BASE_URL="http://localhost:11434/v1"
export ANTHROPIC_API_KEY="ollama"

# Optional: Auch für OpenAI-kompatible Tools setzen
export OPENAI_BASE_URL="http://localhost:11434/v1"
export OPENAI_API_KEY="ollama"

echo "✅ Umgebung auf LOKAL umgestellt (Ollama: http://localhost:11434)"
echo "   - Coding Model: qwen2.5-coder:14b (wird im Hintergrund geladen)"
echo "   - Reasoning Model: deepseek-r1:7b (wird im Hintergrund geladen)"
echo ""
echo "Teste jetzt mit:"
echo "   claude --model qwen2.5-coder:14b 'Schreibe ein Hello World in Python'"
