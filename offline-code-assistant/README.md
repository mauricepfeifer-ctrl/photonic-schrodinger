# 🧠 Offline AI Code Assistant

**100% Kostenlos • 100% Offline • 100% Privat**

> Claude Code Erlebnis - ohne Internet, ohne Kosten, ohne Limits.

## ⚡ Quickstart

```bash
# 1. Einmal Setup ausführen
chmod +x setup.sh && ./setup.sh

# 2. In dein Projekt navigieren
cd ~/dein-projekt

# 3. Starten!
ai-code          # Qwen Coder (bester für Code)
ai-think         # DeepSeek R1 (Reasoning)
ai-llama         # Llama 3.1 (Allround)

# Oder mit dem Menü:
~/offline-code-assistant/launch.sh
```

## 🤖 Verfügbare Modelle

| Modell | Alias | Stärken | RAM-Nutzung |
|--------|-------|---------|-------------|
| **Qwen2.5-Coder:7B** | `ai-code` | Code-Generierung, Refactoring, Debugging | ~5 GB |
| **DeepSeek-R1:8B** | `ai-think` | Tiefes Nachdenken, Architektur, Planung | ~5.5 GB |
| **Llama 3.1:8B** | `ai-llama` | Allround, Erklärungen, Doku | ~5 GB |
| **CodeLlama:7B** | direkt | Code-Spezialist von Meta | ~4 GB |
| **StarCoder2:7B** | direkt | Code Completion, Auto-Fill | ~4 GB |

## 🏗️ Architect Mode (Pro-Tipp!)

Nutzt **zwei Modelle gleichzeitig** - eines denkt, eines codet:

```bash
ai-pair
# Qwen2.5-Coder plant die Architektur
# CodeLlama implementiert den Code
```

## 📋 Aider Befehle

| Befehl | Funktion |
|--------|----------|
| `/add datei.py` | Datei zum Kontext hinzufügen |
| `/drop datei.py` | Datei aus Kontext entfernen |
| `/undo` | Letzte Änderung rückgängig |
| `/diff` | Letzte Änderungen anzeigen |
| `/run pytest` | Shell-Befehl ausführen |
| `/ask Frage` | Frage stellen ohne Code zu ändern |
| `/architect` | In Architect-Modus wechseln |
| `/chat-mode code` | In Code-Edit-Modus wechseln |
| `/tokens` | Token-Nutzung anzeigen |
| `/clear` | Chat-Verlauf löschen |
| `/quit` | Beenden |

## 🔧 Tipps für M4/16GB

1. **Nur ein Modell gleichzeitig** - 16GB reichen für ein 7B-8B Modell komfortabel
2. **Context Window**: Auf 16K gesetzt für gute Code-Übersicht
3. **Architect Mode** lädt 2 Modelle nacheinander (nicht gleichzeitig)
4. **Ollama cached** - einmal geladen, bleibt das Modell im RAM

## 📁 Dateien

```
offline-code-assistant/
├── setup.sh                         # Einmalige Installation
├── launch.sh                        # Interaktiver Launcher
├── .aider.model.settings.yml        # Modell-Konfiguration
└── README.md                        # Diese Datei
```

## 🌐 Optional: Open WebUI (Chat-Interface)

Wenn du auch ein schickes Chat-Interface willst:

```bash
# Docker benötigt
docker run -d -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui \
  ghcr.io/open-webui/open-webui:main

# Dann öffne http://localhost:3000
```

## 💡 Vergleich: Cloud vs. Lokal

| Feature | Claude Code (Cloud) | Offline Assistant (Lokal) |
|---------|-------------------|---------------------------|
| Kosten | $20+/Monat | **0€ für immer** |
| Internet | Erforderlich | **Nicht nötig** |
| Privatsphäre | Code geht in Cloud | **100% lokal** |
| Speed | Schnell | Gut (M4 GPU) |
| Qualität | Sehr hoch | Gut (7B-8B) |
| Limits | Token-Limits | **Keine Limits!** |

---
*Powered by Ollama + Aider • Made for Apple Silicon • Volle Power, Null Kosten* 🚀
