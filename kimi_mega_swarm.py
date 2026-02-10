#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║   🔥 KIMI MEGA SWARM — 10.000 AGENTEN, EIN IMPERIUM 🔥                 ║
║                                                                          ║
║   Das MEGA-PROJEKT. Alle Module. Alle Tasks. Ein Script.                ║
║                                                                          ║
║   Departments:                                                           ║
║     🎯 SALES      — 3000 Agents (Outreach, Proposals, Closing)          ║
║     📢 MARKETING  — 2500 Agents (X, TikTok, YouTube, Ads)              ║
║     📝 CONTENT    — 2000 Agents (Kurse, Blog, Scripts, Threads)         ║
║     🎓 COURSES    — 1500 Agents (AI Academy, AI Consulting Kurse)     ║
║     📈 SCALING    — 1000 Agents (Analytics, Optimization, A/B Tests)    ║
║                                                                          ║
║   Engines Used:                                                          ║
║     • Kimi 2.5 API (Cloud — moonshot-v1-8k / moonshot-v1-128k)         ║
║     • Ollama (Local — DeepSeek-R1, GLM-4, Qwen2.5-Coder)              ║
║     • Dirk Kreuter Sales Psychology                                      ║
║     • Revenue Pipeline                                                   ║
║     • Content Arbitrage                                                  ║
║     • Stripe Manager                                                     ║
║     • n8n Cloud Webhooks                                                 ║
║                                                                          ║
║   Usage:                                                                 ║
║     python kimi_mega_swarm.py                    # Full 10K Launch      ║
║     python kimi_mega_swarm.py --agents 1000      # Custom count         ║
║     python kimi_mega_swarm.py --department sales  # Single dept         ║
║     python kimi_mega_swarm.py --dry-run           # Simulate only       ║
║     python kimi_mega_swarm.py --status            # Live dashboard      ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import aiohttp
import argparse
import json
import logging
import os
import random
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# ═══════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("mega_swarm.log", mode="a"),
    ],
)
logger = logging.getLogger("MegaSwarm")

# ═══════════════════════════════════════════════════════
# SAFE IMPORTS — Graceful degradation
# ═══════════════════════════════════════════════════════
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

# Dirk Kreuter Engine
try:
    from dirk_kreuter_engine import DirkKreuterEngine, SalesMessage
    HAS_KREUTER = True
except ImportError:
    HAS_KREUTER = False

# Revenue Pipeline
try:
    from revenue_pipeline import RevenuePipeline
    HAS_PIPELINE = True
except ImportError:
    HAS_PIPELINE = False

# Stripe Manager
try:
    from stripe_manager import StripeManager
    HAS_STRIPE = True
except ImportError:
    HAS_STRIPE = False

# n8n Connector
try:
    from n8n_connector import N8nConnector
    HAS_N8N = True
except ImportError:
    HAS_N8N = False

# Ollama Engine
try:
    from ollama_engine import OllamaEngine, LLMResponse
    HAS_OLLAMA = True
except ImportError:
    HAS_OLLAMA = False

# Content Arbitrage
try:
    from content_arbitrage import ArbitrageManager
    HAS_ARBITRAGE = True
except ImportError:
    HAS_ARBITRAGE = False

# Empire Intelligence
try:
    from empire_intelligence import MarketResearcher
    HAS_INTELLIGENCE = True
except ImportError:
    HAS_INTELLIGENCE = False

# ═══════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════
KIMI_API_KEY = os.getenv("MOONSHOT_API_KEY", "")
KIMI_BASE_URL = "https://api.moonshot.ai/v1/chat/completions"
KIMI_MODEL_FAST = "moonshot-v1-8k"
KIMI_MODEL_DEEP = "moonshot-v1-128k"

N8N_WEBHOOK_URL = os.getenv(
    "N8N_WEBHOOK_URL",
    "https://ai1337empire.app.n8n.cloud/webhook/empire-swarm"
)

# Rate limits & concurrency
MAX_CONCURRENT_KIMI = int(os.getenv("MAX_CONCURRENT_KIMI", "50"))
MAX_CONCURRENT_OLLAMA = int(os.getenv("MAX_CONCURRENT_OLLAMA", "3"))
BATCH_SIZE = int(os.getenv("SWARM_BATCH_SIZE", "100"))
RATE_LIMIT_DELAY = float(os.getenv("RATE_LIMIT_DELAY", "0.05"))

# Default agent count
DEFAULT_AGENTS = 10000

# Output
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "mega_swarm_output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ═══════════════════════════════════════════════════════
# SECTION 1: DATA MODELS
# ═══════════════════════════════════════════════════════

class Department(str, Enum):
    SALES = "sales"
    MARKETING = "marketing"
    CONTENT = "content"
    COURSES = "courses"
    SCALING = "scaling"
    TROUBLESHOOTING = "troubleshooting"


# Distribution: how many agents per department (percentage)
DEPARTMENT_DISTRIBUTION = {
    Department.SALES: 0.25,             # 25% = 2500 agents
    Department.MARKETING: 0.20,         # 20% = 2000 agents
    Department.CONTENT: 0.15,           # 15% = 1500 agents
    Department.COURSES: 0.12,           # 12% = 1200 agents
    Department.SCALING: 0.08,           # 8%  = 800 agents
    Department.TROUBLESHOOTING: 0.20,   # 20% = 2000 agents — BLOCKER KILLERS
}


@dataclass
class SwarmTask:
    """A single task for one Kimi agent."""
    task_id: int
    department: Department
    task_type: str
    prompt: str
    system_prompt: str
    model: str = KIMI_MODEL_FAST
    result: Optional[str] = None
    status: str = "pending"  # pending, running, done, failed
    tokens_used: int = 0
    cost_usd: float = 0.0
    revenue_eur: float = 0.0
    latency_ms: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class SwarmStats:
    """Real-time statistics across all departments."""
    total_agents: int = 0
    completed: int = 0
    failed: int = 0
    running: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    total_revenue_eur: float = 0.0
    start_time: float = 0.0
    by_department: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    top_results: List[Dict[str, Any]] = field(default_factory=list)

    def rate(self) -> float:
        elapsed = time.time() - self.start_time
        return self.completed / max(elapsed, 0.1)

    def eta_minutes(self) -> float:
        remaining = self.total_agents - self.completed - self.failed
        r = self.rate()
        return (remaining / max(r, 0.01)) / 60

    def roi(self) -> float:
        if self.total_cost_usd <= 0:
            return 0
        return self.total_revenue_eur / self.total_cost_usd

    def summary_dict(self) -> Dict[str, Any]:
        elapsed = time.time() - self.start_time
        return {
            "total_agents": self.total_agents,
            "completed": self.completed,
            "failed": self.failed,
            "running": self.running,
            "completion_pct": round(self.completed / max(self.total_agents, 1) * 100, 1),
            "total_tokens": self.total_tokens,
            "total_cost_usd": round(self.total_cost_usd, 4),
            "total_revenue_eur": round(self.total_revenue_eur, 2),
            "roi": f"{self.roi():.0f}x",
            "rate_per_sec": round(self.rate(), 1),
            "eta_minutes": round(self.eta_minutes(), 1),
            "elapsed_minutes": round(elapsed / 60, 1),
            "departments": self.by_department,
        }


# ═══════════════════════════════════════════════════════
# SECTION 2: TASK GENERATORS — Each department gets its own
# ═══════════════════════════════════════════════════════

class TaskFactory:
    """Generates specialized tasks for each department."""

    # ─── SALES TASKS ──────────────────────────────────
    SALES_TASKS = [
        {
            "type": "cold_email",
            "system": (
                "Du bist ein Elite-Sales-Agent nach Dirk Kreuter Prinzipien. "
                "VALUE FIRST. ROI vor Preis. Echte Verknappung. Social Proof. "
                "Schreibe professionell aber direkt. Immer mit CTA."
            ),
            "prompts": [
                "Schreibe eine Cold Email für AI-Automation Services an einen Mittelstands-CEO. "
                "Fokus: Zeitersparnis von 20h/Woche. Preis: ab EUR 297. Max 150 Wörter.",
                "Erstelle eine Follow-Up Email für einen Lead der nicht geantwortet hat. "
                "Nutze Loss Aversion: 'Ihre Konkurrenz automatisiert bereits...'",
                "Schreibe eine Referral-Email: 'Ihr Kollege [Name] hat bereits Ergebnisse...' "
                "Social Proof + Commitment. CTA: Kostenloser 15-Min Strategy Call.",
                "Erstelle eine Re-Engagement Email für inaktive Leads. "
                "Hook: Neue Case Study, ROI 340%. Verknappung: Noch 3 Plätze diesen Monat.",
                "Schreibe eine Partnership-Anfrage an Agenturen. "
                "White-Label AI Services. Win-Win Proposition.",
            ],
        },
        {
            "type": "proposal",
            "system": (
                "You are an elite freelance proposal writer. "
                "Structure: Hook (pain point), Solution (how you fix it), "
                "Proof (authority/cases), CTA. Under 150 words. Professional but punchy."
            ),
            "prompts": [
                "Write a proposal for: 'Need AI Chatbot for Real Estate Agency'. "
                "Budget $500-$1000. Client: Marcus R. on Upwork.",
                "Write a proposal for: 'Automate my Instagram Content Creation'. "
                "Budget: $200. Client: Sarah L. on Fiverr.",
                "Write a proposal for: 'Build AI-powered customer support system'. "
                "Budget: $2000-$5000. Enterprise client.",
                "Write a proposal for: 'Create automated email marketing sequences'. "
                "Budget: $300. Small business owner.",
                "Write a proposal for: 'Develop AI data analysis dashboard'. "
                "Budget: $1500. Startup founder.",
            ],
        },
        {
            "type": "objection_handling",
            "system": (
                "Du bist ein Verkaufsexperte. Behandle Einwände mit Value-Argumentation. "
                "Nie defensiv. Immer den ROI zeigen. Dirk Kreuter Methode."
            ),
            "prompts": [
                "Handle: 'Das ist mir zu teuer.' Produkt: AI Consulting Sprint (EUR 297)",
                "Handle: 'Ich muss noch darüber nachdenken.' Loss Aversion nutzen.",
                "Handle: 'Mein Entwickler kann das auch.' Differenzierung durch Speed + Expertise.",
                "Handle: 'Wir haben kein Budget dafür.' ROI-Argumentation: Investition vs Kosten.",
                "Handle: 'Welche Garantie gibt es?' 30-Tage Risk-Reversal positionieren.",
            ],
        },
    ]

    # ─── MARKETING TASKS ──────────────────────────────
    MARKETING_TASKS = [
        {
            "type": "x_thread",
            "system": (
                "You are a top-tier X (Twitter) ghostwriter. You understand engagement algorithms. "
                "Short sentences. Punchy hooks. No hashtags unless absolutely viral. "
                "Format: JSON with key 'tweets' (list of strings)."
            ),
            "prompts": [
                "Write a viral 5-tweet thread about: 'How AI agents will replace 80% of office jobs by 2027'",
                "Write a controversial take thread: 'Why most people will never make money with AI'",
                "Write an educational thread: '5 AI tools that replaced my $10K/month team'",
                "Write a story thread: 'I built a $5000/month business with AI in 30 days. Here's how.'",
                "Write a thread about: 'The AI automation stack that runs my entire business'",
                "Write a motivational thread: 'Stop trading time for money. Here's the AI blueprint.'",
                "Write a thread: 'Why German businesses are 5 years behind in AI (and how to profit)'",
            ],
        },
        {
            "type": "tiktok_script",
            "system": (
                "Du bist ein TikTok Content Creator Experte. "
                "Hook in den ersten 2 Sekunden. Storytelling format. "
                "Max 60 Sekunden Sprechzeit. Retention > alles."
            ),
            "prompts": [
                "TikTok Script: 'Warum 95% der Leute nie reich werden' (Motivation/Hustle Niche)",
                "TikTok Script: 'Ich verdiene Geld im Schlaf mit AI' (How-To Format)",
                "TikTok Script: '3 AI Tools die dein Leben verändern' (Listicle Format)",
                "TikTok Script: 'Mein Morgenroutine als 24/7 AI-Unternehmer' (Day in Life)",
                "TikTok Script: 'ChatGPT ist out. Diese AI ist 10x besser.' (Controversy Hook)",
            ],
        },
        {
            "type": "youtube_script",
            "system": (
                "You are a faceless YouTube script writer. "
                "Create engaging 8-12 minute scripts. Hook → Problem → Solution → CTA. "
                "Optimized for retention. Include thumbnail title suggestions."
            ),
            "prompts": [
                "YouTube Script: 'How I Built a $10K/month AI Empire from Zero' (AI News niche)",
                "YouTube Script: 'The $0 to $5000 AI Automation Blueprint' (Finance niche)",
                "YouTube Script: 'Top 10 AI Tools Nobody Talks About in 2026' (Tech Review)",
                "YouTube Script: 'I Replaced My Team with AI Agents — What Happened Next' (Story)",
                "YouTube Script: 'Passive Income with AI: The Complete Guide' (Education)",
            ],
        },
        {
            "type": "ad_copy",
            "system": (
                "You are a direct response copywriter. "
                "AIDA framework. Short paragraphs. Benefit-driven. "
                "Include multiple CTA variations."
            ),
            "prompts": [
                "Write Facebook/Instagram ad copy for: AI Consulting Sprint (EUR 297). "
                "Target: Small business owners. Pain: Manual processes eating profits.",
                "Write ad copy for: Prompt Cheatsheet Pro (EUR 27). "
                "Target: Entrepreneurs. Pain: Wasting hours on bad prompts.",
                "Write ad copy for: AI Email Automation Setup (EUR 97). "
                "Target: Freelancers. Pain: Spending hours on cold outreach.",
                "Write retargeting ad copy for warm leads. Urgency: Limited spots this month.",
                "Write lead magnet ad: 'Free AI Business Blueprint PDF'. "
                "Goal: Email list building.",
            ],
        },
    ]

    # ─── CONTENT TASKS ────────────────────────────────
    CONTENT_TASKS = [
        {
            "type": "blog_post",
            "system": (
                "You are an SEO-optimized blog writer. "
                "Write engaging, value-packed posts. Include H2/H3 headers. "
                "Optimize for search intent. 800-1200 words."
            ),
            "prompts": [
                "Write a blog post: 'AI Automation für KMUs: Der ultimative Leitfaden 2026'",
                "Write a blog post: '5 Wege wie AI dein Business in 30 Tagen transformiert'",
                "Write a blog post: 'AI Automation: Warum jetzt der beste Zeitpunkt ist'",
                "Write a blog post: 'Vom Angestellter zum AI-Unternehmer: Mein Weg'",
                "Write a blog post: 'Die besten Open-Source AI Tools für Startups'",
            ],
        },
        {
            "type": "email_sequence",
            "system": (
                "Du bist ein Email-Marketing Experte. "
                "Schreibe eine 5-Email Nurturing Sequenz. "
                "Value → Authority → Social Proof → Scarcity → Hard CTA."
            ),
            "prompts": [
                "5-Email Welcome Sequence für neue Newsletter Subscriber. "
                "Thema: AI Automation. Ziel: EUR 97 Produkt verkaufen.",
                "5-Email Abandon Cart Sequence. Produkt: AI Consulting Sprint (EUR 297). "
                "Tag 1: Reminder, Tag 2: Social Proof, Tag 3: FAQ, Tag 4: Discount, Tag 5: Last Chance.",
                "3-Email Upsell Sequence nach EUR 27 Tripwire Kauf. "
                "Upgrade auf EUR 297 Paket.",
                "5-Email Re-Engagement für tote Liste. "
                "Win-Back mit neuem kostenlosen Content.",
            ],
        },
        {
            "type": "lead_magnet",
            "system": (
                "Create high-value lead magnet content. "
                "Actionable, structured, professional. "
                "Include checklists, frameworks, and templates."
            ),
            "prompts": [
                "Create a '10-Step AI Business Blueprint' lead magnet outline with key content for each step.",
                "Create an 'AI Automation Checklist 2026' — comprehensive PDF content.",
                "Create '50 AI Automation Ideas for Small Businesses' — categorized by industry.",
                "Create 'The AI Freelancer Toolkit' — tools, prompts, and pricing guide.",
                "Create 'Revenue Calculator: How Much Can AI Save Your Business?' — interactive framework.",
            ],
        },
    ]

    # ─── COURSES TASKS ────────────────────────────────
    COURSES_TASKS = [
        {
            "type": "course_module",
            "system": (
                "You are an expert online course creator. "
                "Structure: Lesson Title → Learning Objectives → Content → "
                "Practical Exercise → Quiz Questions. "
                "Make it actionable and engaging."
            ),
            "prompts": [
                "Create Module 1 of 'AI Automation Masterclass': "
                "'Getting Started — Building Your First AI Agent in 30 Minutes'",
                "Create Module 2: 'Revenue Automation — Setting Up Your AI Sales Pipeline'",
                "Create Module 3: 'Content at Scale — AI-Powered Content for Every Platform'",
                "Create Module 4: 'Advanced Strategies — Multi-Agent Systems & Swarm Intelligence'",
                "Create Module 5: 'Scaling to EUR 10K/month — From Side Hustle to Full Business'",
                "Create AI Academy Module 1: 'AI Grundlagen — Prompting verstehen'",
                "Create AI Academy Module 2: 'Agent Builder — Dein erster AI Agent'",
                "Create AI Academy Module 3: 'Automation at Scale — Multi-Agent Systems'",
            ],
        },
        {
            "type": "course_sales_page",
            "system": (
                "Du bist ein Conversion-Optimierter Texter. "
                "Erstelle Verkaufsseiten-Content nach Dirk Kreuter Prinzipien. "
                "Headline → Problem → Agitate → Solution → Proof → Offer → CTA."
            ),
            "prompts": [
                "Schreibe den Sales Page Content für: 'AI Automation Masterclass' (EUR 497). "
                "Zielgruppe: Selbständige die mit AI skalieren wollen.",
                "Schreibe Sales Page Content für: 'AI Agent Masterclass' (EUR 497). "
                "Zielgruppe: Unternehmer die AI-Agents bauen wollen.",
                "Schreibe Sales Page Content für: 'AI Consulting Crash Course' (EUR 197). "
                "Zielgruppe: Berater die AI-Services anbieten wollen.",
                "Schreibe Webinar Registration Page: 'Wie Sie mit AI in 30 Tagen EUR 5.000 verdienen'. "
                "Kostenlos. Lead-Gen Funnel.",
            ],
        },
        {
            "type": "course_workbook",
            "system": (
                "Create practical workbook content for online courses. "
                "Include: Templates, worksheets, checklists, action plans, "
                "and reflection questions."
            ),
            "prompts": [
                "Create workbook for Module 1: 'My First AI Agent' — Step-by-step worksheet.",
                "Create workbook: 'Revenue Calculator & Goal Setting Template'",
                "Create workbook: 'AI Tool Stack Decision Matrix' — Compare and choose tools.",
                "Create workbook: 'Client Acquisition Playbook' — 30-day action plan.",
            ],
        },
    ]

    # ─── SCALING TASKS ────────────────────────────────
    SCALING_TASKS = [
        {
            "type": "analytics",
            "system": (
                "You are a data-driven growth strategist. "
                "Analyze metrics, identify opportunities, and provide "
                "actionable recommendations. Be specific with numbers."
            ),
            "prompts": [
                "Analyze: Conversion rate 2.3%, Traffic 500 visitors/day, AOV EUR 197. "
                "Give 5 specific recommendations to increase revenue by 50%.",
                "Create A/B test plan for landing page. Variables: Headline, CTA color, "
                "Price display, Social proof placement. Define success metrics.",
                "Analyze sales funnel: 1000 leads → 100 calls → 20 sales. "
                "Identify bottleneck and create optimization plan.",
                "Create KPI dashboard specifications: Revenue, MRR, Churn, LTV, CAC. "
                "Include alert thresholds and weekly report template.",
                "Pricing strategy analysis: Current EUR 97/197/497. "
                "Evaluate adding EUR 997 premium tier. Market positioning advice.",
            ],
        },
        {
            "type": "automation_blueprint",
            "system": (
                "You are an automation architect. "
                "Design complete n8n/Zapier workflows. "
                "Include triggers, actions, error handling, and expected outcomes."
            ),
            "prompts": [
                "Design automation: 'New Stripe Payment → Gumroad Fulfillment → "
                "Welcome Email → Slack Notification → CRM Update'. Full workflow spec.",
                "Design automation: 'New Lead from Landing Page → Score Lead → "
                "Route to Sales Agent → Auto Follow-up Sequence'. Include timing.",
                "Design automation: 'Content Calendar → AI Generate → "
                "Schedule Posts → Track Performance → Optimize'. Multi-platform.",
                "Design automation: 'Support Ticket → AI Classify → "
                "Auto-Respond or Route to Human → Track Resolution Time'.",
            ],
        },
        {
            "type": "market_research",
            "system": (
                "You are a market researcher. "
                "Analyze trends, competition, and opportunities. "
                "Provide data-driven insights with actionable next steps."
            ),
            "prompts": [
                "Research: AI Automation Services market in DACH region 2026. "
                "Market size, growth rate, key players, pricing models, entry strategies.",
                "Competitive analysis: Top 5 AI consulting companies in Germany. "
                "Pricing, positioning, strengths, weaknesses, opportunities.",
                "Research: Online course market in Germany. "
                "Best platforms, average prices, marketing channels, success factors.",
                "Research: Freelance AI services demand on Upwork/Fiverr. "
                "Top categories, average budgets, competition level, winning strategies.",
            ],
        },
    ]

    # ─── TROUBLESHOOTING TASKS — BLOCKER KILLERS ─────────
    TROUBLESHOOTING_TASKS = [
        {
            "type": "debug_code",
            "system": (
                "Du bist ein Elite Python/Go Debugger und DevOps Engineer. "
                "Analysiere Fehler systematisch. Gib konkrete Lösungen mit Code-Fixes. "
                "Priorisiere: 1. Crash verhindern 2. Funktionalität wiederherstellen 3. Optimieren."
            ),
            "prompts": [
                "Debug: Pyre2 meldet 'missing-module-attribute' für lokale Imports in Python. "
                "Das Projekt nutzt os.chdir(SCRIPT_DIR) aber Pyre findet die Module nicht. "
                "Erstelle eine .pyre_configuration die alle lokalen Module korrekt resolved.",
                "Fix: aiohttp.ClientSession wird nicht korrekt geschlossen und erzeugt ResourceWarnings. "
                "Erstelle einen sicheren Context Manager Pattern für alle async HTTP calls.",
                "Debug: asyncio.gather() Tasks die bei Rate Limiting (429) endlos retrien. "
                "Implementiere exponential backoff mit max 3 retries und circuit breaker.",
                "Fix: Ollama Engine timeout bei DeepSeek-R1 reasoning model (>60s Antworten). "
                "Dynamic timeout basierend auf Model-Typ implementieren.",
                "Debug: JSON parse errors wenn Kimi API response malformed ist. "
                "Robust error handling mit fallback content.",
                "Fix: Race condition in SwarmStats — concurrent updates auf shared counters. "
                "Implementiere thread-safe atomic operations.",
            ],
        },
        {
            "type": "integration_fix",
            "system": (
                "You are a systems integration specialist. "
                "Fix connection issues between services. "
                "Provide complete, tested solutions with error handling."
            ),
            "prompts": [
                "Fix: n8n webhook returns 404 for 'empire-swarm' endpoint. "
                "Debug the webhook URL, test with curl, and create fallback URL strategy.",
                "Fix: Stripe webhook server receives events but fails signature verification. "
                "Review STRIPE_WEBHOOK_SECRET handling and implement proper verification.",
                "Fix: Gumroad API returns 401 Unauthorized despite valid token. "
                "Debug auth flow, check token expiry, implement token refresh.",
                "Fix: Docker containers can't reach Ollama on host.docker.internal:11434. "
                "Network configuration for Mac Docker Desktop.",
                "Fix: Redis connection refused in docker-compose setup. "
                "Review service dependencies and health checks.",
                "Fix: Telegram bot webhook not receiving messages. "
                "Debug webhook URL, SSL cert, and Telegram API registration.",
            ],
        },
        {
            "type": "performance_fix",
            "system": (
                "You are a performance optimization engineer. "
                "Identify bottlenecks, fix memory leaks, optimize throughput. "
                "Provide benchmarks and measurable improvements."
            ),
            "prompts": [
                "Optimize: Python async swarm currently processes 10 tasks/sec but target is 100/sec. "
                "Profile the bottleneck and provide optimized implementation.",
                "Fix: Memory leak in long-running agent swarm — RSS grows to 2GB after 1000 tasks. "
                "Identify leak source and implement proper cleanup.",
                "Optimize: Go swarm engine using too many goroutines (>10K) causing OOM. "
                "Implement worker pool pattern with bounded concurrency.",
                "Fix: Content generation pipeline takes 5min per piece. "
                "Implement parallel processing and caching to get under 30sec.",
                "Optimize: Database writes blocking API responses. "
                "Implement async write-behind cache pattern.",
            ],
        },
        {
            "type": "devops_fix",
            "system": (
                "You are a DevOps/SRE engineer. "
                "Fix deployment issues, CI/CD pipelines, and infrastructure problems. "
                "Provide complete config files and step-by-step solutions."
            ),
            "prompts": [
                "Fix: GitHub Pages deployment fails for landing page. "
                "Debug the deploy workflow, fix CNAME, and ensure HTTPS works.",
                "Create: Complete .env.example with all required environment variables "
                "for the AI Empire stack. Include descriptions and default values.",
                "Fix: venv activation fails on Mac M-series. "
                "Create universal setup script that works on ARM64 and x86_64.",
                "Create: Health check endpoint that monitors all empire services "
                "(Ollama, n8n, Stripe, Gumroad, Telegram) and reports status.",
                "Fix: Git repo has API keys in history. "
                "Create BFG cleanup script and pre-commit hook to prevent future leaks.",
                "Create: Automated backup script for all empire data "
                "(revenue_log.json, agent_rankings.json, swarm outputs) to iCloud.",
            ],
        },
        {
            "type": "error_recovery",
            "system": (
                "Du bist ein Fehler-Recovery-Spezialist. "
                "Analysiere Fehlermeldungen und erstelle sofort umsetzbare Fixes. "
                "Jeder Fix muss getestet und verifiziert werden können."
            ),
            "prompts": [
                "Recovery: 'ModuleNotFoundError: No module named rich' — "
                "Erstelle requirements.txt mit allen Dependencies und auto-install script.",
                "Recovery: 'ConnectionRefusedError: [Errno 61] Connection refused' bei Ollama. "
                "Auto-start Ollama, health check, und graceful fallback zu Kimi API.",
                "Recovery: 'stripe.error.AuthenticationError' — API Key ungültig. "
                "Implementiere Key rotation und Testmode fallback.",
                "Recovery: 'aiohttp.ClientPayloadError' bei großen API responses. "
                "Implement streaming response handler und chunked processing.",
                "Recovery: Swarm crash nach 5000 Tasks wegen 'Too many open files'. "
                "Fix ulimit settings und implementiere connection pooling.",
                "Recovery: 'asyncio.TimeoutError' bei 30% der Kimi API calls. "
                "Adaptive timeout strategy basierend auf response time history.",
            ],
        },
    ]

    @staticmethod
    def get_tasks_for_department(dept: Department) -> List[Dict[str, Any]]:
        """Get all task templates for a department."""
        mapping = {
            Department.SALES: TaskFactory.SALES_TASKS,
            Department.MARKETING: TaskFactory.MARKETING_TASKS,
            Department.CONTENT: TaskFactory.CONTENT_TASKS,
            Department.COURSES: TaskFactory.COURSES_TASKS,
            Department.SCALING: TaskFactory.SCALING_TASKS,
            Department.TROUBLESHOOTING: TaskFactory.TROUBLESHOOTING_TASKS,
        }
        return mapping.get(dept, [])

    @staticmethod
    def generate_task(task_id: int, dept: Department) -> SwarmTask:
        """Generate a single task for a specific department."""
        templates = TaskFactory.get_tasks_for_department(dept)
        template = random.choice(templates)
        prompt = random.choice(template["prompts"])

        # Add variation to avoid duplicate outputs
        variation = random.choice([
            "",
            " Be creative and unique.",
            " Focus on German market.",
            " Use a conversational tone.",
            " Be data-driven and specific.",
            " Include real-world examples.",
            " Make it actionable.",
            " Add urgency elements.",
        ])

        return SwarmTask(
            task_id=task_id,
            department=dept,
            task_type=template["type"],
            prompt=prompt + variation,
            system_prompt=template["system"],
            model=KIMI_MODEL_FAST,
        )

    @staticmethod
    def distribute_agents(total: int) -> Dict[Department, int]:
        """Distribute total agents across departments."""
        distribution = {}
        allocated = 0
        departments = list(DEPARTMENT_DISTRIBUTION.items())

        for i, (dept, pct) in enumerate(departments):
            if i == len(departments) - 1:
                # Last department gets remainder
                distribution[dept] = total - allocated
            else:
                count = int(total * pct)
                distribution[dept] = count
                allocated += count

        return distribution


# ═══════════════════════════════════════════════════════
# SECTION 3: KIMI EXECUTOR — The actual API caller
# ═══════════════════════════════════════════════════════

class KimiExecutor:
    """Handles all Kimi API communication with rate limiting."""

    def __init__(self, max_concurrent: int = MAX_CONCURRENT_KIMI):
        self.api_key = KIMI_API_KEY
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.session: Optional[aiohttp.ClientSession] = None
        self.request_count = 0
        self.rate_limit_hits = 0

    async def init(self):
        connector = aiohttp.TCPConnector(
            limit=MAX_CONCURRENT_KIMI,
            ttl_dns_cache=300,
        )
        timeout = aiohttp.ClientTimeout(total=120)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
        )

    async def close(self):
        if self.session:
            await self.session.close()

    async def execute(self, task: SwarmTask) -> SwarmTask:
        """Execute a single task via Kimi API."""
        async with self.semaphore:
            task.status = "running"
            t0 = time.time()

            try:
                if not self.api_key:
                    # Simulation mode if no API key
                    return await self._simulate(task, t0)

                payload = {
                    "model": task.model,
                    "messages": [
                        {"role": "system", "content": task.system_prompt},
                        {"role": "user", "content": task.prompt},
                    ],
                    "max_tokens": 500,
                    "temperature": 0.7,
                }

                async with self.session.post(
                    KIMI_BASE_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                ) as resp:
                    self.request_count += 1

                    if resp.status == 200:
                        data = await resp.json()
                        content = data["choices"][0]["message"]["content"]
                        tokens = data.get("usage", {}).get("total_tokens", 200)

                        task.result = content
                        task.tokens_used = tokens
                        task.cost_usd = tokens * 0.0000005  # moonshot-v1-8k pricing
                        task.status = "done"
                        task.latency_ms = int((time.time() - t0) * 1000)

                        # Estimate revenue based on department
                        task.revenue_eur = self._estimate_revenue(task)

                        return task

                    elif resp.status == 429:
                        self.rate_limit_hits += 1
                        await asyncio.sleep(random.uniform(2, 5))
                        task.status = "failed"
                        return task

                    else:
                        error_text = await resp.text()
                        logger.debug(f"Kimi error {resp.status}: {error_text[:100]}")
                        task.status = "failed"
                        return task

            except asyncio.TimeoutError:
                task.status = "failed"
                task.latency_ms = int((time.time() - t0) * 1000)
                return task
            except Exception as e:
                logger.debug(f"Task {task.task_id} error: {e}")
                task.status = "failed"
                return task

    async def _simulate(self, task: SwarmTask, t0: float) -> SwarmTask:
        """Simulate task execution (dry-run or no API key)."""
        await asyncio.sleep(random.uniform(0.01, 0.05))
        task.result = f"[SIMULATED] {task.task_type} output for {task.department.value}"
        task.tokens_used = random.randint(100, 400)
        task.cost_usd = task.tokens_used * 0.0000005
        task.status = "done"
        task.latency_ms = int((time.time() - t0) * 1000)
        task.revenue_eur = self._estimate_revenue(task)
        return task

    @staticmethod
    def _estimate_revenue(task: SwarmTask) -> float:
        """Estimate revenue contribution based on task type."""
        # Conservative revenue estimates per task
        estimates = {
            # Sales
            "cold_email": 2.50,        # 1% conversion × EUR 250 avg deal
            "proposal": 5.00,          # 2% win rate × EUR 250 avg
            "objection_handling": 1.50, # Support for closing

            # Marketing
            "x_thread": 0.80,          # Engagement → followers → revenue
            "tiktok_script": 0.60,     # Brand awareness
            "youtube_script": 3.00,    # Ad revenue + leads
            "ad_copy": 2.00,           # ROAS multiplier

            # Content
            "blog_post": 1.50,         # SEO → organic traffic
            "email_sequence": 4.00,    # Nurture → conversion
            "lead_magnet": 2.50,       # List building

            # Courses
            "course_module": 5.00,     # Product development
            "course_sales_page": 8.00, # Direct revenue driver
            "course_workbook": 3.00,   # Product quality

            # Scaling
            "analytics": 3.00,         # Optimization insights
            "automation_blueprint": 5.00, # Efficiency gains
            "market_research": 4.00,   # Strategic decisions

            # Troubleshooting — saves time = saves money = revenue
            "debug_code": 10.00,          # Hours saved × EUR rate
            "integration_fix": 15.00,     # Blocker removed → pipeline unblocked
            "performance_fix": 12.00,     # Throughput increase → more revenue
            "devops_fix": 8.00,           # Infrastructure stability
            "error_recovery": 20.00,      # Critical path recovery
        }
        return estimates.get(task.task_type, 1.00)


# ═══════════════════════════════════════════════════════
# SECTION 4: MEGA SWARM ENGINE — The main orchestrator
# ═══════════════════════════════════════════════════════

class MegaSwarm:
    """
    The unified engine. Spawns 10,000 Kimi agents across all departments.
    One script to rule them all.
    """

    def __init__(
        self,
        total_agents: int = DEFAULT_AGENTS,
        department_filter: Optional[Department] = None,
        dry_run: bool = False,
    ):
        self.total_agents = total_agents
        self.department_filter = department_filter
        self.dry_run = dry_run
        self.executor = KimiExecutor()
        self.stats = SwarmStats(total_agents=total_agents)
        self.n8n_connector: Optional[N8nConnector] = None
        self.stream_to_n8n = True  # ALWAYS STREAM FOR MAX POWER
        self.results: List[SwarmTask] = []

        # Init department stats
        for dept in Department:
            self.stats.by_department[dept.value] = {
                "agents": 0,
                "completed": 0,
                "failed": 0,
                "tokens": 0,
                "cost_usd": 0.0,
                "revenue_eur": 0.0,
            }

    async def init(self):
        """Initialize all connections."""
        await self.executor.init()
        if HAS_N8N:
            self.n8n_connector = N8nConnector(webhook_url=N8N_WEBHOOK_URL)

    async def close(self):
        """Clean shutdown."""
        await self.executor.close()
        if self.n8n_connector:
            await self.n8n_connector.close()

    def _generate_all_tasks(self) -> List[SwarmTask]:
        """Generate all tasks distributed across departments."""
        tasks = []
        task_id = 0

        if self.department_filter:
            # Only run one department
            distribution = {self.department_filter: self.total_agents}
        else:
            distribution = TaskFactory.distribute_agents(self.total_agents)

        for dept, count in distribution.items():
            self.stats.by_department[dept.value]["agents"] = count
            logger.info(f"  {dept.value.upper():12s}: {count:,} agents")

            for _ in range(count):
                task = TaskFactory.generate_task(task_id, dept)
                tasks.append(task)
                task_id += 1

        return tasks

    async def _process_result(self, task: SwarmTask):
        """Process a completed task — update stats, save output."""
        if task.status == "done":
            self.stats.completed += 1
            self.stats.total_tokens += task.tokens_used
            self.stats.total_cost_usd += task.cost_usd
            self.stats.total_revenue_eur += task.revenue_eur

            dept_stats = self.stats.by_department[task.department.value]
            dept_stats["completed"] += 1
            dept_stats["tokens"] += task.tokens_used
            dept_stats["cost_usd"] += task.cost_usd
            dept_stats["revenue_eur"] += task.revenue_eur

            # Save top results
            if task.result and len(task.result) > 50:
                self.results.append(task)
                # Keep only top 100 results
                if len(self.results) > 100:
                    self.results = self.results[-100:]

            # 🔥 BEAM TO N8N FOR MAXIMAL POWER
            if self.stream_to_n8n and self.n8n_connector:
                payload = {
                    "event": "task_completed",
                    "task_id": task.task_id,
                    "department": task.department.value,
                    "type": task.task_type,
                    "prompt": task.prompt,
                    "result": task.result,
                    "revenue_eur": task.revenue_eur,
                    "cost_usd": task.cost_usd,
                    "timestamp": datetime.now().isoformat()
                }
                # Fire and forget - don't await/block
                asyncio.create_task(self._fire_n8n_event(f"task_completed", payload))

        elif task.status == "failed":
            self.stats.failed += 1
            self.stats.by_department[task.department.value]["failed"] += 1

        self.stats.running = max(0, self.stats.running - 1)

    def _print_progress(self, force: bool = False):
        """Print live progress bar."""
        total = self.stats.total_agents
        done = self.stats.completed + self.stats.failed
        pct = done / max(total, 1) * 100

        if not force and done % max(total // 20, 1) != 0:
            return

        bar_len = 40
        filled = int(bar_len * done / max(total, 1))
        bar = "█" * filled + "░" * (bar_len - filled)

        print(
            f"\r  [{bar}] {pct:5.1f}% | "
            f"✅ {self.stats.completed:,} | ❌ {self.stats.failed:,} | "
            f"⚡ {self.stats.rate():.0f}/s | "
            f"💰 EUR {self.stats.total_revenue_eur:,.0f} | "
            f"💸 ${self.stats.total_cost_usd:.2f} | "
            f"📈 {self.stats.roi():.0f}x ROI | "
            f"⏱️  ETA {self.stats.eta_minutes():.1f}min",
            end="",
            flush=True,
        )

    async def _fire_n8n_event(self, event_type: str, data: Dict[str, Any]):
        """Send event to n8n for automation."""
        if self.n8n_connector:
            try:
                await self.n8n_connector.send_data(data, event_type)
            except Exception:
                pass  # Don't block on webhook failures

    async def run(self):
        """
        🚀 LAUNCH THE MEGA SWARM
        """
        self.stats.start_time = time.time()

        # ─── Banner ───
        print("\n" + "═" * 72)
        print("🔥  KIMI MEGA SWARM — 10.000 AGENTEN, EIN IMPERIUM")
        print("═" * 72)
        print(f"  Total Agents:  {self.total_agents:,}")
        print(f"  Departments:   {self.department_filter.value if self.department_filter else 'ALL'}")
        print(f"  Concurrency:   {MAX_CONCURRENT_KIMI} (Kimi) / {MAX_CONCURRENT_OLLAMA} (Ollama)")
        print(f"  API Key:       {'✅ Set' if KIMI_API_KEY else '⚠️  SIMULATION MODE'}")
        print(f"  Dry Run:       {'YES' if self.dry_run else 'NO'}")
        print(f"  n8n Webhooks:  {'✅ Active' if HAS_N8N else '❌ Disabled'}")
        if HAS_N8N:
            print(f"  → Stream URL:  {N8N_WEBHOOK_URL}/task_completed")
        print(f"  Output:        {OUTPUT_DIR}")
        print("─" * 72)

        # ─── Initialize ───
        await self.init()

        # ─── Generate Tasks ───
        print("\n📋 Generating tasks...")
        tasks = self._generate_all_tasks()
        print(f"  Total tasks generated: {len(tasks):,}")

        # ─── Fire start event ───
        await self._fire_n8n_event("swarm_started", {
            "total_agents": self.total_agents,
            "departments": {d.value: c for d, c in TaskFactory.distribute_agents(self.total_agents).items()},
            "timestamp": datetime.now().isoformat(),
        })

        # ─── Execute in batches ───
        print("\n🚀 LAUNCHING SWARM...\n")
        try:
            for batch_start in range(0, len(tasks), BATCH_SIZE):
                batch = tasks[batch_start:batch_start + BATCH_SIZE]
                self.stats.running += len(batch)

                # Execute batch concurrently
                results = await asyncio.gather(
                    *[self.executor.execute(task) for task in batch],
                    return_exceptions=True,
                )

                # Process results
                for result in results:
                    if isinstance(result, SwarmTask):
                        await self._process_result(result)
                    elif isinstance(result, Exception):
                        self.stats.failed += 1
                        self.stats.running = max(0, self.stats.running - 1)

                self._print_progress()

                # Rate limiting between batches
                await asyncio.sleep(RATE_LIMIT_DELAY)

                # Fire progress event every 10%
                done = self.stats.completed + self.stats.failed
                if done % max(self.total_agents // 10, 1) == 0 and done > 0:
                    await self._fire_n8n_event("swarm_progress", self.stats.summary_dict())

        except KeyboardInterrupt:
            print("\n\n⚠️  SWARM INTERRUPTED BY USER")

        # ─── Final progress ───
        self._print_progress(force=True)
        print()  # newline after progress bar

        # ─── Save results ───
        await self._save_all_results()

        # ─── Print final report ───
        self._print_final_report()

        # ─── Fire completion event ───
        await self._fire_n8n_event("swarm_completed", self.stats.summary_dict())

        # ─── Cleanup ───
        await self.close()

    async def _save_all_results(self):
        """Save all results to organized files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = os.path.join(OUTPUT_DIR, f"run_{timestamp}")
        os.makedirs(run_dir, exist_ok=True)

        # Save results by department
        by_dept: Dict[str, List[Dict]] = {}
        for task in self.results:
            dept_key = task.department.value
            if dept_key not in by_dept:
                by_dept[dept_key] = []
            by_dept[dept_key].append({
                "task_id": task.task_id,
                "type": task.task_type,
                "prompt": task.prompt[:100],
                "result": task.result,
                "tokens": task.tokens_used,
                "cost_usd": round(task.cost_usd, 6),
                "revenue_eur": round(task.revenue_eur, 2),
                "latency_ms": task.latency_ms,
            })

        for dept, items in by_dept.items():
            filepath = os.path.join(run_dir, f"{dept}_results.json")
            with open(filepath, "w") as f:
                json.dump(items, f, indent=2, ensure_ascii=False)
            logger.info(f"  Saved {len(items)} {dept} results → {filepath}")

        # Save stats
        stats_file = os.path.join(run_dir, "stats.json")
        with open(stats_file, "w") as f:
            json.dump(self.stats.summary_dict(), f, indent=2)
        logger.info(f"  Stats saved → {stats_file}")

        # Save mega summary
        summary_file = os.path.join(run_dir, "SUMMARY.md")
        with open(summary_file, "w") as f:
            f.write(self._generate_markdown_report())
        logger.info(f"  Summary → {summary_file}")

    def _generate_markdown_report(self) -> str:
        """Generate a beautiful markdown report."""
        elapsed = time.time() - self.stats.start_time
        s = self.stats

        report = f"""# 🔥 KIMI MEGA SWARM — Run Report

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Duration:** {elapsed/60:.1f} minutes
**Total Agents:** {s.total_agents:,}

## 📊 Overall Results

| Metric | Value |
|--------|-------|
| ✅ Completed | {s.completed:,} |
| ❌ Failed | {s.failed:,} |
| ⚡ Rate | {s.rate():.0f} tasks/sec |
| 🎫 Total Tokens | {s.total_tokens:,} |
| 💸 Total Cost | ${s.total_cost_usd:.2f} |
| 💰 Est. Revenue | EUR {s.total_revenue_eur:,.2f} |
| 📈 ROI | {s.roi():.0f}x |

## 🏢 Department Breakdown

| Department | Agents | Done | Revenue (EUR) | Cost ($) |
|-----------|--------|------|---------------|----------|
"""
        for dept, stats in s.by_department.items():
            report += (
                f"| {dept.upper()} | {stats['agents']:,} | "
                f"{stats['completed']:,} | "
                f"EUR {stats['revenue_eur']:,.2f} | "
                f"${stats['cost_usd']:.2f} |\n"
            )

        report += f"""
## 🏆 Top Results

"""
        for i, task in enumerate(self.results[-10:], 1):
            snippet = (task.result or "")[:200].replace("\n", " ")
            report += f"### {i}. [{task.department.value.upper()}] {task.task_type}\n"
            report += f"> {snippet}...\n\n"

        report += f"""
## 🔧 System Configuration

- Kimi Model: {KIMI_MODEL_FAST}
- Max Concurrent: {MAX_CONCURRENT_KIMI}
- Batch Size: {BATCH_SIZE}
- API Key: {'Set' if KIMI_API_KEY else 'Simulation Mode'}

---
*Generated by KIMI MEGA SWARM v1.0 — Maurice's AI Empire*
"""
        return report

    def _print_final_report(self):
        """Print final report to console."""
        elapsed = time.time() - self.stats.start_time
        s = self.stats

        print("\n" + "═" * 72)
        print("🏆  MEGA SWARM — FINAL REPORT")
        print("═" * 72)
        print(f"  Duration:        {elapsed/60:.1f} minutes")
        print(f"  Tasks Completed: {s.completed:,} / {s.total_agents:,}")
        print(f"  Tasks Failed:    {s.failed:,}")
        print(f"  Success Rate:    {s.completed / max(s.completed + s.failed, 1) * 100:.1f}%")
        print(f"  Rate:            {s.rate():.0f} tasks/sec")
        print(f"  Total Tokens:    {s.total_tokens:,}")
        print(f"  Total Cost:      ${s.total_cost_usd:.2f}")
        print(f"  Est. Revenue:    EUR {s.total_revenue_eur:,.2f}")
        print(f"  ROI:             {s.roi():.0f}x")
        print("─" * 72)
        print("  DEPARTMENT BREAKDOWN:")
        print("─" * 72)
        for dept, ds in s.by_department.items():
            if ds["agents"] > 0:
                pct = ds["completed"] / max(ds["agents"], 1) * 100
                print(
                    f"  {dept.upper():12s} │ "
                    f"Agents: {ds['agents']:>6,} │ "
                    f"Done: {ds['completed']:>6,} ({pct:.0f}%) │ "
                    f"Revenue: EUR {ds['revenue_eur']:>8,.2f} │ "
                    f"Cost: ${ds['cost_usd']:.2f}"
                )
        print("═" * 72)
        print(f"  Output saved to: {OUTPUT_DIR}")
        print("═" * 72 + "\n")


# ═══════════════════════════════════════════════════════
# SECTION 5: STATUS DISPLAY
# ═══════════════════════════════════════════════════════

def show_status():
    """Show current system status — what modules are available."""
    print("\n" + "═" * 72)
    print("📊  AI EMPIRE — SYSTEM STATUS")
    print("═" * 72)

    modules = {
        "Kimi API Key": bool(KIMI_API_KEY),
        "Dirk Kreuter Engine": HAS_KREUTER,
        "Revenue Pipeline": HAS_PIPELINE,
        "Stripe Manager": HAS_STRIPE,
        "n8n Connector": HAS_N8N,
        "Ollama Engine": HAS_OLLAMA,
        "Content Arbitrage": HAS_ARBITRAGE,
        "Market Intelligence": HAS_INTELLIGENCE,
    }

    for name, status in modules.items():
        icon = "✅" if status else "❌"
        print(f"  {icon} {name}")

    print("─" * 72)

    # Departments & task counts
    print("  DEPARTMENTS & TASKS:")
    for dept in Department:
        templates = TaskFactory.get_tasks_for_department(dept)
        total_types = len(templates)
        total_prompts = sum(len(t["prompts"]) for t in templates)
        print(f"  📁 {dept.value.upper():12s} │ {total_types} task types │ {total_prompts} prompt variations")

    total_variations = sum(
        len(t["prompts"])
        for dept in Department
        for t in TaskFactory.get_tasks_for_department(dept)
    )
    print(f"\n  Total unique prompt variations: {total_variations}")

    # Distribution for 10K
    print("\n  DEFAULT DISTRIBUTION (10,000 agents):")
    dist = TaskFactory.distribute_agents(10000)
    for dept, count in dist.items():
        print(f"    {dept.value.upper():12s}: {count:,} agents ({count/100:.0f}%)")

    print("═" * 72 + "\n")


# ═══════════════════════════════════════════════════════
# SECTION 6: CLI
# ═══════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="🔥 KIMI MEGA SWARM — 10,000 Agents, One Empire",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python kimi_mega_swarm.py                      # Full 10K launch
  python kimi_mega_swarm.py --agents 1000        # 1K agents
  python kimi_mega_swarm.py --department sales    # Sales only
  python kimi_mega_swarm.py --dry-run             # Simulate
  python kimi_mega_swarm.py --status              # System status
        """,
    )

    parser.add_argument(
        "-n", "--agents",
        type=int,
        default=DEFAULT_AGENTS,
        help=f"Number of agents to spawn (default: {DEFAULT_AGENTS})",
    )
    parser.add_argument(
        "-d", "--department",
        type=str,
        choices=[d.value for d in Department],
        help="Run only a specific department",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate without API calls",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show system status and exit",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=MAX_CONCURRENT_KIMI,
        help=f"Max concurrent Kimi requests (default: {MAX_CONCURRENT_KIMI})",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=BATCH_SIZE,
        help=f"Batch size for processing (default: {BATCH_SIZE})",
    )
    parser.add_argument(
        "--no-stream",
        action="store_true",
        help="Disable streaming results to n8n (enabled by default)",
    )

    args = parser.parse_args()

    if args.status:
        show_status()
        return

    dept_filter = Department(args.department) if args.department else None

    swarm = MegaSwarm(
        total_agents=args.agents,
        department_filter=dept_filter,
        dry_run=args.dry_run,
    )
    if args.no_stream:
        swarm.stream_to_n8n = False
        
    # Apply CLI overrides to executor
    # Apply CLI overrides to executor
    swarm.executor.semaphore = asyncio.Semaphore(args.concurrency)

    asyncio.run(swarm.run())


if __name__ == "__main__":
    main()
