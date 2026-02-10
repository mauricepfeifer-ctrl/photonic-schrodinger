# 🏰 AI Empire — Architecture & Usage

## 🧠 Core Systems (The Brain)

- **Nucleus (`empire_nucleus.py`)**: Central decision engine. Runs the 8-cell parallel Brain (`PARL8Brain`) to evaluate strategic moves.
- **Orchestrator (`empire_orchestrator.py`)**: Task dispatcher for 100k+ agents. Manages load balancing between Kimi (Cloud) and Ollama (Local).
- **Mega Swarm (`kimi_mega_swarm.py`)**: The massive workforce. specialized agents for Sales, Content, Research.

## 💰 Revenue Engines (The Money)

- **Revenue Burst (`revenue_burst.py`)**: Scrapes Upwork/Fiverr RSS feeds, generates proposals using `DeepSeek-R1`, and creates drafts.
- **Stripe Manager (`stripe_manager.py`)**: Handles product catalog sync, checkout links, and webhook processing.
- **Ghost Squadron (`ghost_squadron.py`)**: Elite autonomous units that hunt for specific high-value opportunities.

## 🕸️ Automation (The Nervous System)

- **n8n (`n8n_workflow_builder.py`)**: Programmatically defines and deploys 10+ workflows for recurring tasks (Social Posting, CRM updates).
- **Message Bus (`redis`)**: Pub/Sub channel for inter-agent communication.

## 🚀 Usage

### 1. Setup

```bash
# Install dependencies
make install

# Configure Secrets
cp .env.example .env
# Edit .env with your Moonshot/Stripe keys
```

### 2. Launch

```bash
# Full Auto-Pilot
make run-launch

# Interactive Mode
make run-nucleus

# Dashboard
python empire_cli.py status
```

### 3. Testing

```bash
# Run all unit tests
make test
```

## 🐳 Docker

```bash
# Start Infrastructure (Redis, n8n, Monitoring)
make docker-up

# Stop
make docker-down
```
