# 🎛️ N8N Workflow Builder — Configuration
# ══════════════════════════════════════════════════════
# Central configuration for automating n8n workflows.
# This file is used by `n8n_workflow_builder.py` to ensure consistency.

import os
from dotenv import load_dotenv

load_dotenv()

# N8N Instance Connection
N8N_BASE_URL = os.getenv("N8N_API_URL", "https://ai1337empire.app.n8n.cloud/api/v1")
N8N_API_KEY = os.getenv("N8N_API_KEY", "")

# Webhook Secrets (for verification)
WEBHOOK_SECRET = os.getenv("N8N_WEBHOOK_SECRET", "super-secret-token-123")

# Workflow Names
WF_KIMI_RECEIVER = "Kimi Swarm Receiver"
WF_REVENUE_DASHBOARD = "Revenue Dashboard"
WF_CONTENT_BLITZ = "Content Blitz Auto-Post"
WF_SALES_FORCE = "Sales Force Pipeline"
WF_GHOST_SQUADRON = "Ghost Squadron Ops"
WF_EMPIRE_HEARTBEAT = "Empire Heartbeat"
WF_BRAIN_LOGGER = "Brain Decision Logger"
WF_STRIPE_PROCESSOR = "Stripe Payment Processor"
WF_YOUTUBE_AUTOMATION = "YouTube Automation"
WF_X_MONSTER = "X Monster Auto-Post"

# Default Polling Intervals (Cron)
CRON_EVERY_MINUTE = "bar:*"
CRON_HOURLY = "0 *"
CRON_DAILY_9AM = "0 9 * * *"
