# 🚀 AI EMPIRE — LAUNCH MANUAL

> One-page guide to fire up the entire system.

---

## Prerequisites

| Requirement | Check Command |
|---|---|
| Python 3.10+ | `python3 --version` |
| Ollama | `ollama --version` |
| Docker (optional) | `docker --version` |
| `.env` file | Copy `.env.example` → `.env`, fill in keys |

### Required API Keys (in `.env`)

```bash
MOONSHOT_API_KEY=sk-...       # Kimi 2.5 (moonshot.ai)
STRIPE_SECRET_KEY=sk_...      # Stripe payments
STRIPE_WEBHOOK_SECRET=whsec_... # Stripe webhook signing
N8N_API_KEY=...               # n8n REST API
```

---

## 🔥 Quick Start (3 Steps)

### Step 1: Start Local AI Engine

```bash
ollama serve &
ollama pull deepseek-r1:8b
ollama pull qwen2.5-coder:7b
```

### Step 2: Export & Import N8N Workflows

```bash
python3 n8n_workflow_builder.py          # Exports 10 JSON files
python3 n8n_workflow_builder.py --push   # Pushes directly to n8n cloud
```

Workflows are saved in `n8n_workflows/`. Import them manually via **n8n → Settings → Import from File** if not using `--push`.

### Step 3: Launch the Empire

```bash
# Full Launch (all systems)
python3 empire_launch.py

# Interactive Cockpit
python3 empire_launch.py --interactive

# Status Check Only
python3 empire_launch.py --status
```

---

## 💰 Revenue Commands

| Command | What it does |
|---|---|
| `python3 revenue_burst.py` | Scan Upwork RSS for gigs, auto-generate proposals |
| `python3 revenue_burst.py --demo` | Use seed data (no network needed) |
| `python3 revenue_burst.py --manual` | Enter gigs by hand via CLI |

Proposals are saved to `revenue_drafts/` as Markdown files, ready for copy-paste.

---

## 🐝 Kimi Mega Swarm

```bash
# Full 10,000 Agent Swarm
python3 kimi_mega_swarm.py

# Dry Run (simulation, no API calls)
python3 kimi_mega_swarm.py --dry-run

# Single Department
python3 kimi_mega_swarm.py --department sales

# Custom Agent Count
python3 kimi_mega_swarm.py --agents 1000
```

---

## 🏥 Mission Control

```bash
# System status across all services
./mission-control/scripts/mc_status.sh

# View logs
./mission-control/scripts/mc_logs.sh

# Restart services
./mission-control/scripts/mc_restart.sh
```

---

## 🐳 Docker Stack (Full Infrastructure)

```bash
./start_imperium.sh
```

Services:

- **Grafana**: `http://localhost:3001`
- **n8n**: `http://localhost:5678`
- **Open WebUI**: `http://localhost:3000`

---

## 📂 Key Files Reference

| File | Purpose |
|---|---|
| `GOLD_NUGGETS_MASTERPLAN.md` | All strategies, prompts & architecture |
| `empire_launch.py` | Master integration script |
| `kimi_mega_swarm.py` | 10K agent swarm engine |
| `revenue_burst.py` | Upwork/Fiverr proposal generator |
| `n8n_workflow_builder.py` | N8N workflow creator (10 workflows) |
| `godmode_dashboard.html` | Live swarm visualization |
| `stripe_manager.py` | Payment processing |
| `ghost_squadron.py` | Covert ops / competitive intelligence |
