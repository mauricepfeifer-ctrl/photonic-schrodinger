import os
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# API Keys
MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY", "")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID", "")

# URLs
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "https://ai1337empire.app.n8n.cloud/webhook/")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")

# Models
MODEL_SALES = os.getenv("MODEL_SALES", "deepseek-r1:7b")
MODEL_CONTENT = os.getenv("MODEL_CONTENT", "qwen2.5-coder:14b")
MODEL_RESEARCH = os.getenv("MODEL_RESEARCH", "deepseek-r1:7b")

# Application Settings
OFFLINE_MODE = os.getenv("OFFLINE_MODE", "false").lower() == "true"
DEBUG_MODE = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL = "DEBUG" if DEBUG_MODE else "INFO"

# Constants
EMPIRE_NAME = "Photonic Schrödinger"
VERSION = "1.0.0-DELTA"
