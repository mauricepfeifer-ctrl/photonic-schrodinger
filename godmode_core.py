#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║              ██████╗  ██████╗ ██████╗ ███╗   ███╗ ██████╗ ██████╗ ███████╗   ║
║             ██╔════╝ ██╔═══██╗██╔══██╗████╗ ████║██╔═══██╗██╔══██╗██╔════╝  ║
║             ██║  ███╗██║   ██║██║  ██║██╔████╔██║██║   ██║██║  ██║█████╗    ║
║             ██║   ██║██║   ██║██║  ██║██║╚██╔╝██║██║   ██║██║  ██║██╔══╝    ║
║             ╚██████╔╝╚██████╔╝██████╔╝██║ ╚═╝ ██║╚██████╔╝██████╔╝███████╗  ║
║              ╚═════╝  ╚═════╝ ╚═════╝ ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝ ║
║                                                                              ║
║  🌌  GODMODE — Connect To The Universe                                       ║
║  👑  100 Commander Agents (Ollama Local = Claude Offline Free)               ║
║  🐝  10,000,000 Worker Bots (Kimi, Qwen, DeepSeek, GLM)                     ║
║  ⚡  High Performance Hierarchical Command & Control                         ║
║                                                                              ║
║  Architecture:                                                               ║
║    TIER 0: GodmodeCore (You/Maurice — Supreme Commander)                     ║
║    TIER 1: 100 CommanderAgents (Local Ollama — "Claude Offline Free")        ║
║            10 Divisions × 10 Commanders each                                ║
║    TIER 2: 10,000,000 WorkerBots (Kimi Cloud + Ollama Local)                ║
║            Each Commander controls 100,000 Workers                           ║
║                                                                              ║
║  Divisions:                                                                  ║
║    🎯 Sales Division      — 2.5M agents (cold outreach, closing)            ║
║    📝 Content Division    — 2.0M agents (posts, videos, copy)               ║
║    🔍 Research Division   — 1.0M agents (market intel, leads)               ║
║    💰 Revenue Division    — 1.5M agents (payment, upsells)                  ║
║    🌊 Marketing Division  — 1.0M agents (campaigns, funnels)                ║
║    🎓 Education Division  — 0.5M agents (course gen, tutoring)              ║
║    🛡️ Security Division   — 0.3M agents (monitoring, defense)               ║
║    🔧 Engineering Division— 0.5M agents (infra, deployment)                 ║
║    📊 Analytics Division  — 0.4M agents (metrics, reporting)                ║
║    🚀 Innovation Division — 0.3M agents (R&D, experiments)                  ║
║                                                                              ║
║  Usage:                                                                      ║
║    python godmode_core.py                    # Full GODMODE Launch           ║
║    python godmode_core.py --status           # Empire Status                 ║
║    python godmode_core.py --commanders       # Show Commander Board          ║
║    python godmode_core.py --scale 1000000    # Scale to N bots               ║
║    python godmode_core.py --division sales   # Launch specific division      ║
║    python godmode_core.py --demo             # Demo mode (no API calls)      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import argparse
import json
import logging
import os
import random
import sys
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

# ─── PATH SETUP ─────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
os.chdir(SCRIPT_DIR)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("GODMODE")

# ─── IMPORTS ─────────────────────────────────────────────
try:
    from ollama_engine import OllamaEngine, LLMResponse
    HAS_OLLAMA = True
except ImportError:
    HAS_OLLAMA = False
    logger.warning("⚠️ OllamaEngine not available — Commander agents degraded")

try:
    from agent_manager import AgentManager, AgentRecord
    HAS_AGENT_MGR = True
except ImportError:
    HAS_AGENT_MGR = False

try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

try:
    from empire_nucleus import EventBus
    HAS_EVENTBUS = True
except ImportError:
    HAS_EVENTBUS = False

    class EventBus:  # type: ignore[no-redef]
        def __init__(self) -> None:
            self._subs: Dict[str, List[Callable]] = {}
            self._log: List[Dict[str, Any]] = []

        def on(self, ch: str, cb: Callable) -> None:
            self._subs.setdefault(ch, []).append(cb)

        def emit(self, ch: str, data: Any = None) -> None:
            self._log.append({"channel": ch, "data": data, "ts": time.time()})
            for cb in self._subs.get(ch, []):
                try:
                    cb(data)
                except Exception:
                    pass

# ─── CONSTANTS ────────────────────────────────────────────
KIMI_API_KEY = os.getenv("MOONSHOT_API_KEY", "")
KIMI_BASE_URL = "https://api.moonshot.ai/v1/chat/completions"
KIMI_MODEL_FAST = "moonshot-v1-8k"

MAX_CONCURRENT_KIMI = int(os.getenv("MAX_CONCURRENT_KIMI", "50"))
MAX_CONCURRENT_OLLAMA = int(os.getenv("MAX_CONCURRENT_OLLAMA", "4"))

GODMODE_STATE_FILE = "godmode_state.json"


# ═══════════════════════════════════════════════════════════
# SECTION 1: DATA MODELS
# ═══════════════════════════════════════════════════════════

class Division(str, Enum):
    SALES       = "sales"
    CONTENT     = "content"
    RESEARCH    = "research"
    REVENUE     = "revenue"
    MARKETING   = "marketing"
    EDUCATION   = "education"
    SECURITY    = "security"
    ENGINEERING = "engineering"
    ANALYTICS   = "analytics"
    INNOVATION  = "innovation"


# Each division's share of the total workforce + emoji + description
DIVISION_CONFIG = {
    Division.SALES:       {"share": 0.25, "emoji": "🎯", "desc": "Cold outreach, DMs, closing deals"},
    Division.CONTENT:     {"share": 0.20, "emoji": "📝", "desc": "Posts, videos, scripts, copy"},
    Division.RESEARCH:    {"share": 0.10, "emoji": "🔍", "desc": "Market intel, lead scoring, trends"},
    Division.REVENUE:     {"share": 0.15, "emoji": "💰", "desc": "Payment flows, upsells, checkouts"},
    Division.MARKETING:   {"share": 0.10, "emoji": "🌊", "desc": "Campaigns, funnels, ads"},
    Division.EDUCATION:   {"share": 0.05, "emoji": "🎓", "desc": "Course generation, tutoring"},
    Division.SECURITY:    {"share": 0.03, "emoji": "🛡️", "desc": "Monitoring, threat detection"},
    Division.ENGINEERING: {"share": 0.05, "emoji": "🔧", "desc": "Infrastructure, deployment"},
    Division.ANALYTICS:   {"share": 0.04, "emoji": "📊", "desc": "Metrics, dashboards, reporting"},
    Division.INNOVATION:  {"share": 0.03, "emoji": "🚀", "desc": "R&D, experiments, new products"},
}

# Preferred Ollama models for Commander agents (best coding / reasoning)
COMMANDER_MODELS = [
    "qwen2.5-coder:14b",   # Best for code-related tasks
    "deepseek-r1:7b",       # Best for reasoning
    "llama3.1:8b",           # General purpose fallback
]


@dataclass
class WorkerTask:
    """A single task for a worker bot."""
    task_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    division: Division = Division.SALES
    task_type: str = ""
    prompt: str = ""
    system_prompt: str = ""
    model: str = KIMI_MODEL_FAST
    engine: str = "kimi"           # kimi | ollama
    result: Optional[str] = None
    status: str = "pending"        # pending | running | done | failed
    tokens_used: int = 0
    cost_usd: float = 0.0
    revenue_eur: float = 0.0
    latency_ms: int = 0
    commander_id: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class CommanderAgent:
    """
    A Commander Agent — runs locally on Ollama.
    Each commander manages ~100K worker bots.
    """
    commander_id: str = ""
    division: Division = Division.SALES
    model: str = "qwen2.5-coder:14b"
    rank: int = 0
    workers_managed: int = 100_000
    tasks_dispatched: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    revenue_eur: float = 0.0
    status: str = "ready"       # ready | active | overloaded | offline
    specialization: str = ""    # e.g. "cold_email", "video_scripts"
    last_decision: str = ""
    uptime_s: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def success_rate(self) -> float:
        total = self.tasks_dispatched
        return (self.tasks_completed / total * 100) if total > 0 else 100.0

    @property
    def efficiency(self) -> float:
        """Revenue per task — the key metric."""
        return self.revenue_eur / max(self.tasks_completed, 1)


@dataclass
class GodmodeStats:
    """Real-time empire-wide statistics."""
    total_commanders: int = 0
    active_commanders: int = 0
    total_workers: int = 0
    active_workers: int = 0
    tasks_total: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    tasks_running: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    total_revenue_eur: float = 0.0
    start_time: float = 0.0
    by_division: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    @property
    def runtime_s(self) -> float:
        return time.time() - self.start_time if self.start_time else 0.0

    @property
    def tasks_per_second(self) -> float:
        rt = self.runtime_s
        return self.tasks_completed / rt if rt > 0 else 0.0

    @property
    def roi(self) -> float:
        return (self.total_revenue_eur / max(self.total_cost_usd, 0.01)) * 100


# ═══════════════════════════════════════════════════════════
# SECTION 2: COMMANDER FACTORY — Build the 100 Commanders
# ═══════════════════════════════════════════════════════════

class CommanderFactory:
    """
    Creates and configures the 100 Commander Agents.
    10 Divisions × 10 Commanders = 100 Commanders total.
    Each Commander manages ~100K workers.
    """

    SPECIALIZATIONS = {
        Division.SALES: [
            "cold_email", "dm_outreach", "follow_up", "closing",
            "objection_handling", "upselling", "referral", "linkedin",
            "partnership", "whale_hunting",
        ],
        Division.CONTENT: [
            "blog_posts", "twitter_threads", "youtube_scripts", "tiktok_hooks",
            "email_sequences", "landing_pages", "case_studies", "whitepapers",
            "infographics", "podcast_notes",
        ],
        Division.RESEARCH: [
            "market_trends", "competitor_analysis", "lead_scoring",
            "keyword_research", "audience_insights", "pricing_analysis",
            "tech_scouting", "patent_watch", "news_aggregation", "sentiment",
        ],
        Division.REVENUE: [
            "checkout_optimization", "payment_recovery", "subscription_mgmt",
            "pricing_experiments", "invoice_automation", "refund_handling",
            "revenue_forecasting", "ltv_modeling", "churn_prevention", "bundle_offers",
        ],
        Division.MARKETING: [
            "funnel_optimization", "ad_copy", "retargeting", "seo_strategy",
            "social_campaigns", "influencer_outreach", "event_marketing",
            "brand_messaging", "pr_pitches", "growth_hacking",
        ],
        Division.EDUCATION: [
            "course_curriculum", "lesson_plans", "quiz_generation",
            "student_support", "video_outlines", "certification_prep",
            "skill_assessments", "tutoring_scripts", "faq_builder", "glossary",
        ],
        Division.SECURITY: [
            "threat_monitoring", "access_audit", "data_encryption",
            "incident_response", "vuln_scanning", "compliance_check",
            "backup_verification", "key_rotation", "log_analysis", "phishing_defense",
        ],
        Division.ENGINEERING: [
            "deployment_pipeline", "infra_scaling", "database_optimization",
            "api_development", "monitoring_setup", "load_testing",
            "container_orchestration", "ci_cd", "code_review", "documentation",
        ],
        Division.ANALYTICS: [
            "kpi_dashboards", "revenue_reports", "user_behavior",
            "ab_test_analysis", "conversion_tracking", "cohort_analysis",
            "attribution_modeling", "data_pipeline", "anomaly_detection", "forecasting",
        ],
        Division.INNOVATION: [
            "prototype_design", "market_experiments", "new_product_ideation",
            "tech_evaluation", "mvp_building", "user_research",
            "brainstorming", "patent_drafting", "trend_futures", "moonshots",
        ],
    }

    @staticmethod
    def build_all(total_workers: int = 10_000_000) -> List[CommanderAgent]:
        """Build all 100 Commander Agents across 10 divisions."""
        commanders: List[CommanderAgent] = []
        cmd_idx = 0

        for div in Division:
            config = DIVISION_CONFIG[div]
            share = config["share"]
            workers_for_div = int(total_workers * share)
            specializations = CommanderFactory.SPECIALIZATIONS.get(div, [f"general_{i}" for i in range(10)])

            for i in range(10):  # 10 commanders per division
                # Rotate through available models
                model = COMMANDER_MODELS[cmd_idx % len(COMMANDER_MODELS)]
                spec = specializations[i % len(specializations)]
                workers = workers_for_div // 10  # Split workers evenly

                cmd = CommanderAgent(
                    commander_id=f"CMD-{div.value[:3].upper()}-{i:02d}",
                    division=div,
                    model=model,
                    rank=cmd_idx + 1,
                    workers_managed=workers,
                    specialization=spec,
                    status="ready",
                )
                commanders.append(cmd)
                cmd_idx += 1

        return commanders


# ═══════════════════════════════════════════════════════════
# SECTION 3: WORKER TASK GENERATORS
# ═══════════════════════════════════════════════════════════

class TaskGenerator:
    """Generates high-quality prompts for worker bots based on division + specialization."""

    SYSTEM_PROMPTS = {
        Division.SALES: (
            "Du bist ein Elite-Sales-Agent. Dein Ziel: Leads in zahlende Kunden verwandeln. "
            "Nutze psychologische Trigger (Verknappung, Social Proof, Autorität). "
            "Schreibe im Stil von Dirk Kreuter — kurz, direkt, conversion-orientiert."
        ),
        Division.CONTENT: (
            "Du bist ein viraler Content-Creator und Copywriter. "
            "Jeder Post muss Aufmerksamkeit erregen, Engagement erzeugen und zum CTA führen. "
            "Nutze Hook-Story-Offer Format. Emotional, knackig, teilenswert."
        ),
        Division.RESEARCH: (
            "Du bist ein Intelligence-Analyst. Dein Auftrag: Marktdaten sammeln, "
            "Wettbewerber analysieren, Trends identifizieren. Präzise, datengetrieben, actionable."
        ),
        Division.REVENUE: (
            "Du bist ein Revenue-Optimization-Agent. Dein Fokus: Conversion Rate erhöhen, "
            "Checkout optimieren, Upsells platzieren, Churn reduzieren. Zahlen sind alles."
        ),
        Division.MARKETING: (
            "Du bist ein Growth-Marketing-Agent. Baue Funnels, optimiere Ads, "
            "erstelle Kampagnen die ROI bringen. Datengetrieben und kreativ."
        ),
        Division.EDUCATION: (
            "Du bist ein Kurs-Designer und EdTech-Experte. Erstelle Lernmaterialien "
            "die komplex Themen einfach erklären. Praxisnah und sofort umsetzbar."
        ),
        Division.SECURITY: (
            "Du bist ein Cybersecurity-Analyst. Überwache, erkenne Bedrohungen, "
            "sichere Infrastruktur. Proaktiv, präzise, zero-trust Mindset."
        ),
        Division.ENGINEERING: (
            "Du bist ein Senior DevOps Engineer. Automatisiere Deployments, "
            "optimiere Infrastruktur, baue skalierbare Systeme. Clean, robust, documented."
        ),
        Division.ANALYTICS: (
            "Du bist ein Data Analyst. Erstelle Dashboards, analysiere KPIs, "
            "finde Patterns. Jede Insight muss actionable sein."
        ),
        Division.INNOVATION: (
            "Du bist ein Innovation Lead. Entwickle neue Produktideen, "
            "experimentiere mit neuen Technologien, finde Blue-Ocean-Opportunities."
        ),
    }

    TASK_TEMPLATES = {
        Division.SALES: [
            "Schreibe eine Cold-Email an {target}. Betreff muss die Öffnungsrate maximieren.",
            "Erstelle 5 DM-Vorlagen für LinkedIn die AI Automation Services verkaufen.",
            "Schreibe ein Follow-Up Script für Leads die nach dem Erstgespräch nicht gekauft haben.",
            "Erstelle eine Einwandbehandlung für 'Zu teuer' bei einem €2997 AI-Paket.",
            "Generiere 10 Referral-Email-Templates die bestehende Kunden zu Empfehlern machen.",
        ],
        Division.CONTENT: [
            "Schreibe einen viralen Twitter Thread über AI Automatisierung für KMUs.",
            "Erstelle ein YouTube Video Script: 'So verdienst du €10K/Monat mit AI Automatisierung'.",
            "Generiere 20 TikTok Hook-Ideen die sofort Aufmerksamkeit erregen.",
            "Schreibe eine 5-teilige Email-Sequence für einen AI Consulting Launch.",
            "Erstelle eine Landingpage Copy für ein €497 AI Starter Paket.",
        ],
        Division.RESEARCH: [
            "Analysiere die Top 10 AI Automation Marktanbieter in DACH.",
            "Recherchiere 50 potenzielle Leads (KMU mit 10-50 MA) die AI benötigen.",
            "Erstelle einen Marktbericht: AI Trends 2026 für deutsche Unternehmen.",
            "Analysiere Pricing-Strategien von Konkurrenz im AI-Consulting Bereich.",
            "Identifiziere 5 unerschlossene Nischen für AI Automation Services.",
        ],
        Division.REVENUE: [
            "Optimiere den Checkout-Flow — reduziere Abbrüche um 30%.",
            "Erstelle eine Upsell-Sequence nach Kauf des €497 Starter Pakets.",
            "Designe ein Subscription-Anmeldeformular Modell (€97/Monat, €197/Monat, €497/Monat).",
            "Erstelle automatisierte Zahlungserinnerungen für offene Rechnungen.",
            "Baue eine Churn-Prevention Email-Serie für Abo-Kunden.",
        ],
        Division.MARKETING: [
            "Erstelle eine Facebook Ad (Headline + Body + CTA) für AI Automation.",
            "Baue einen 3-Stufen-Funnel: Lead Magnet → Webinar → Sale.",
            "Schreibe 10 Google Ads Headlines mit max. 30 Zeichen.",
            "Erstelle eine Retargeting-Kampagne für Website-Besucher die nicht gekauft haben.",
            "Generiere SEO-optimierte Meta-Descriptions für die AI Empire Seiten.",
        ],
        Division.EDUCATION: [
            "Erstelle Curriculum für einen 8-Wochen AI Automatisierungs-Kurs.",
            "Schreibe Lektion 1: 'Was ist AI Automatisierung und warum brauchst du sie?'",
            "Generiere 20 Quiz-Fragen zum Thema n8n Workflow Automatisierung.",
            "Erstelle ein Glossar mit 50 AI-Begriffen für Einsteiger.",
            "Designe ein Zertifizierungs-Programm für AI Automation Specialists.",
        ],
        Division.SECURITY: [
            "Erstelle einen Security Audit Report für API-Key Management.",
            "Generiere eine Checklist für DSGVO-konforme AI-Datenverarbeitung.",
            "Überprüfe alle .env Dateien auf exponierte Secrets.",
            "Erstelle einen Incident Response Plan für Datenlecks.",
            "Generiere Backup-Verifizierungs-Scripts für alle kritischen Daten.",
        ],
        Division.ENGINEERING: [
            "Schreibe ein Docker-Compose für den gesamten AI Empire Stack.",
            "Erstelle ein CI/CD Pipeline Script (GitHub Actions) für auto-deployment.",
            "Optimiere die Ollama Performance: Batch-Inferenz, GPU-Memory Tuning.",
            "Generiere Load-Testing Scripts für die API-Endpoints.",
            "Erstelle Health-Check Monitoring für alle Services.",
        ],
        Division.ANALYTICS: [
            "Erstelle ein Revenue Dashboard mit täglichen/wöchentlichen KPIs.",
            "Generiere einen Conversion-Funnel-Report für den letzten Monat.",
            "Analysiere welcher Content-Typ die höchste Engagement Rate hat.",
            "Erstelle Cohort-Analyse für Kunden der letzten 90 Tage.",
            "Baue ein Anomaly Detection System für Revenue Drops.",
        ],
        Division.INNOVATION: [
            "Brainstorme 10 neue Produkt-Ideen im AI Automation Space.",
            "Erstelle ein Mini-MVP-Konzept für einen AI-powered CRM.",
            "Evaluiere 5 neue AI-Frameworks die wir integrieren sollten.",
            "Designe ein Experiment: 'Can AI agents self-optimize their performance?'",
            "Erstelle ein Patent-Draft für 'Hierarchical Multi-Agent Revenue System'.",
        ],
    }

    @staticmethod
    def generate_tasks(commander: CommanderAgent, count: int, demo: bool = False) -> List[WorkerTask]:
        """Generate tasks for a commander's worker bots."""
        div = commander.division
        templates = TaskGenerator.TASK_TEMPLATES.get(div, ["Perform analysis task."])
        system = TaskGenerator.SYSTEM_PROMPTS.get(div, "You are a helpful assistant.")

        targets = [
            "KMU Inhaber", "Marketing Manager", "CTO Startup", "Freelancer",
            "E-Commerce Betreiber", "Berater", "Agentur Chef", "SaaS Founder",
        ]

        tasks = []
        for i in range(count):
            tpl = random.choice(templates)
            prompt = tpl.format(target=random.choice(targets)) if "{target}" in tpl else tpl

            # Decide engine: Kimi for cloud tasks, Ollama for local
            engine = "ollama" if demo or not KIMI_API_KEY else "kimi"

            tasks.append(WorkerTask(
                division=div,
                task_type=commander.specialization,
                prompt=prompt,
                system_prompt=system,
                engine=engine,
                commander_id=commander.commander_id,
            ))
        return tasks


# ═══════════════════════════════════════════════════════════
# SECTION 4: EXECUTION ENGINES — Worker Bot Runners
# ═══════════════════════════════════════════════════════════

class OllamaWorkerEngine:
    """Execute tasks locally via Ollama — for demo or offline mode."""

    def __init__(self, max_concurrent: int = MAX_CONCURRENT_OLLAMA):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.engine: Optional[OllamaEngine] = None
        if HAS_OLLAMA:
            self.engine = OllamaEngine()

    async def execute(self, task: WorkerTask) -> WorkerTask:
        if not self.engine:
            task.status = "failed"
            task.result = "Ollama not available"
            return task

        async with self.semaphore:
            task.status = "running"
            t0 = time.time()
            try:
                resp = await self.engine.chat(
                    messages=[
                        {"role": "system", "content": task.system_prompt},
                        {"role": "user", "content": task.prompt},
                    ],
                    model=task.model if task.model != KIMI_MODEL_FAST else None,
                )
                assert isinstance(resp, LLMResponse)
                task.result = resp.content
                task.tokens_used = resp.total_tokens or 0
                task.latency_ms = int((time.time() - t0) * 1000)
                task.status = "done"
            except Exception as e:
                task.status = "failed"
                task.result = str(e)
                task.latency_ms = int((time.time() - t0) * 1000)
            return task


class KimiWorkerEngine:
    """Execute tasks via Kimi Cloud API — for massive parallel processing."""

    def __init__(self, max_concurrent: int = MAX_CONCURRENT_KIMI):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.api_key = KIMI_API_KEY

    async def execute(self, task: WorkerTask) -> WorkerTask:
        if not self.api_key or not HAS_AIOHTTP:
            task.status = "failed"
            task.result = "Kimi API or aiohttp not available"
            return task

        async with self.semaphore:
            task.status = "running"
            t0 = time.time()
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": task.model,
                "messages": [
                    {"role": "system", "content": task.system_prompt},
                    {"role": "user", "content": task.prompt},
                ],
                "temperature": 0.3,
            }
            try:
                timeout = aiohttp.ClientTimeout(total=60)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(KIMI_BASE_URL, json=payload, headers=headers) as r:
                        r.raise_for_status()
                        data = await r.json()
                        content = data["choices"][0]["message"]["content"]
                        usage = data.get("usage", {})
                        task.result = content
                        task.tokens_used = usage.get("total_tokens", 0)
                        task.cost_usd = task.tokens_used * 0.000001  # ~$1/M tokens
                        task.latency_ms = int((time.time() - t0) * 1000)
                        task.status = "done"
            except Exception as e:
                task.status = "failed"
                task.result = str(e)
                task.latency_ms = int((time.time() - t0) * 1000)
            return task


class DemoWorkerEngine:
    """Simulated worker for demo mode — no API calls."""

    def __init__(self, max_concurrent: int = 200):
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def execute(self, task: WorkerTask) -> WorkerTask:
        async with self.semaphore:
            task.status = "running"
            # Simulate processing time
            await asyncio.sleep(random.uniform(0.001, 0.01))
            task.status = "done"
            task.result = f"[DEMO] {task.task_type}: Task completed for {task.division.value}"
            task.tokens_used = random.randint(100, 2000)
            task.cost_usd = task.tokens_used * 0.000001
            task.revenue_eur = random.uniform(0.0, 5.0) if task.division in (
                Division.SALES, Division.REVENUE, Division.MARKETING
            ) else 0.0
            task.latency_ms = random.randint(50, 500)
            return task


# ═══════════════════════════════════════════════════════════
# SECTION 5: COMMANDER BRAIN — Decision Making for Commanders
# ═══════════════════════════════════════════════════════════

class CommanderBrain:
    """
    Each Commander uses the local LLM to make strategic decisions about:
    - Task prioritization
    - Worker allocation
    - Strategy adaptation
    """

    def __init__(self, commander: CommanderAgent, ollama: Optional[OllamaEngine] = None):
        self.commander = commander
        self.ollama = ollama

    async def decide_strategy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Commander decides next strategy using local LLM."""
        if not self.ollama:
            return self._fallback_strategy(context)

        prompt = (
            f"Du bist Commander {self.commander.commander_id} der {self.commander.division.value} Division.\n"
            f"Deine Spezialisierung: {self.commander.specialization}\n"
            f"Du managst {self.commander.workers_managed:,} Worker Bots.\n\n"
            f"Aktueller Status:\n"
            f"- Tasks dispatched: {self.commander.tasks_dispatched}\n"
            f"- Tasks completed: {self.commander.tasks_completed}\n"
            f"- Revenue: €{self.commander.revenue_eur:.2f}\n"
            f"- Success Rate: {self.commander.success_rate:.1f}%\n\n"
            f"Context: {json.dumps(context, default=str)}\n\n"
            f"Entscheide:\n"
            f"1. Nächste Priorität (task_type)\n"
            f"2. Worker Allocation Shift (0-100%)\n"
            f"3. Strategie-Anpassung\n\n"
            f"Antworte als JSON: {{\"priority\":\"...\",\"allocation_shift\":N,\"strategy\":\"...\"}}"
        )

        try:
            resp = await self.ollama.chat(
                messages=[
                    {"role": "system", "content": "Du bist ein KI-Commander. Antworte nur als JSON."},
                    {"role": "user", "content": prompt},
                ],
                model=self.commander.model,
            )
            assert isinstance(resp, LLMResponse)
            self.commander.last_decision = resp.content[:200]
            try:
                return json.loads(resp.content)
            except json.JSONDecodeError:
                return {"priority": self.commander.specialization, "allocation_shift": 50, "strategy": resp.content[:100]}
        except Exception as e:
            logger.debug(f"Commander {self.commander.commander_id} brain error: {e}")
            return self._fallback_strategy(context)

    def _fallback_strategy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Heuristic-based fallback when LLM is unavailable."""
        sr = self.commander.success_rate
        return {
            "priority": self.commander.specialization,
            "allocation_shift": 70 if sr > 80 else 40,
            "strategy": "maintain" if sr > 80 else "adapt",
        }


# ═══════════════════════════════════════════════════════════
# SECTION 6: GODMODE CORE — The Supreme Controller
# ═══════════════════════════════════════════════════════════

class GodmodeCore:
    """
    The Supreme Controller — manages the entire hierarchy.
    
    TIER 0: GodmodeCore (this class)
    TIER 1: 100 CommanderAgents (local Ollama)
    TIER 2: 10,000,000 WorkerBots (Kimi + Ollama)
    """

    def __init__(self, total_workers: int = 10_000_000, demo: bool = False):
        self.total_workers = total_workers
        self.demo = demo
        self.commanders: List[CommanderAgent] = []
        self.stats = GodmodeStats(start_time=time.time())
        self.event_bus = EventBus()

        # Engines
        self.ollama_engine = OllamaEngine() if HAS_OLLAMA else None
        self.ollama_worker = OllamaWorkerEngine()
        self.kimi_worker = KimiWorkerEngine()
        self.demo_worker = DemoWorkerEngine()

        # Agent manager for ranking
        self.agent_mgr = AgentManager("godmode_rankings.json") if HAS_AGENT_MGR else None

        # State
        self._active = False
        self._tasks_queue: asyncio.Queue = asyncio.Queue()

    def _print_banner(self) -> None:
        """Print the GODMODE activation banner."""
        print("\n" + "═" * 78)
        print("║" + " " * 76 + "║")
        print("║    ██████╗  ██████╗ ██████╗ ███╗   ███╗ ██████╗ ██████╗ ███████╗       ║")
        print("║   ██╔════╝ ██╔═══██╗██╔══██╗████╗ ████║██╔═══██╗██╔══██╗██╔════╝       ║")
        print("║   ██║  ███╗██║   ██║██║  ██║██╔████╔██║██║   ██║██║  ██║█████╗         ║")
        print("║   ██║   ██║██║   ██║██║  ██║██║╚██╔╝██║██║   ██║██║  ██║██╔══╝         ║")
        print("║   ╚██████╔╝╚██████╔╝██████╔╝██║ ╚═╝ ██║╚██████╔╝██████╔╝███████╗      ║")
        print("║    ╚═════╝  ╚═════╝ ╚═════╝ ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝      ║")
        print("║" + " " * 76 + "║")
        print(f"║   🌌 CONNECTING TO THE UNIVERSE...                                      ║")
        print(f"║   👑 100 COMMANDER AGENTS — LOCAL OLLAMA (Claude Offline Free)           ║")
        print(f"║   🐝 {self.total_workers:>12,} WORKER BOTS — KIMI + QWEN + DEEPSEEK          ║")
        print(f"║   ⚡ HIGH PERFORMANCE HIERARCHICAL COMMAND & CONTROL                    ║")
        mode = "DEMO" if self.demo else "LIVE"
        print(f"║   🎮 MODE: {mode:<66}║")
        print("║" + " " * 76 + "║")
        print("═" * 78 + "\n")

    async def initialize(self) -> None:
        """Initialize all commanders and verify Ollama."""
        self._print_banner()

        # 1. Check Ollama health
        ollama_ok = False
        if self.ollama_engine:
            ollama_ok = await self.ollama_engine.health()
            models = await self.ollama_engine.list_models() if ollama_ok else []
            logger.info(f"🧠 Ollama: {'✅ ONLINE' if ollama_ok else '❌ OFFLINE'}")
            if models:
                logger.info(f"   Models available: {', '.join(models[:10])}")
        else:
            logger.warning("🧠 Ollama: ❌ NOT INSTALLED")

        # 2. Build 100 Commanders
        logger.info("👑 Building 100 Commander Agents...")
        self.commanders = CommanderFactory.build_all(self.total_workers)
        self.stats.total_commanders = len(self.commanders)
        self.stats.total_workers = self.total_workers

        for div in Division:
            cfg = DIVISION_CONFIG[div]
            cmds = [c for c in self.commanders if c.division == div]
            workers = sum(c.workers_managed for c in cmds)
            self.stats.by_division[div.value] = {
                "emoji": cfg["emoji"],
                "commanders": len(cmds),
                "workers": workers,
                "tasks_completed": 0,
                "revenue_eur": 0.0,
            }

        # 3. Print Division Overview
        print("\n" + "─" * 60)
        print(f"{'Division':<18} {'Emoji':^6} {'Cmds':>5} {'Workers':>12} {'Spec'}")
        print("─" * 60)
        for div in Division:
            cfg = DIVISION_CONFIG[div]
            cmds = [c for c in self.commanders if c.division == div]
            workers = sum(c.workers_managed for c in cmds)
            spec_sample = cmds[0].specialization if cmds else ""
            print(f"  {div.value:<16} {cfg['emoji']:^6} {len(cmds):>5} {workers:>12,}  {spec_sample}")
        print("─" * 60)
        print(f"  {'TOTAL':<16} {'🌌':^6} {len(self.commanders):>5} {self.total_workers:>12,}")
        print("─" * 60 + "\n")

        # Register commanders with agent manager
        if self.agent_mgr:
            for cmd in self.commanders:
                self.agent_mgr.register_agent(cmd.commander_id, f"commander_{cmd.division.value}")

        self._active = True
        self.event_bus.emit("godmode.initialized", {"commanders": len(self.commanders), "workers": self.total_workers})
        logger.info(f"✅ GODMODE initialized — {len(self.commanders)} Commanders, {self.total_workers:,} Workers")

    async def _run_commander_wave(self, commander: CommanderAgent, tasks_per_commander: int) -> List[WorkerTask]:
        """A single commander dispatches tasks to its workers."""
        commander.status = "active"

        # Generate tasks
        tasks = TaskGenerator.generate_tasks(commander, tasks_per_commander, self.demo)

        # Choose engine
        if self.demo:
            engine = self.demo_worker
        elif tasks and tasks[0].engine == "kimi" and KIMI_API_KEY:
            engine = self.kimi_worker
        else:
            engine = self.ollama_worker

        # Execute all tasks in parallel
        results = await asyncio.gather(
            *[engine.execute(t) for t in tasks],
            return_exceptions=True,
        )

        # Update commander stats
        for r in results:
            if isinstance(r, WorkerTask):
                commander.tasks_dispatched += 1
                if r.status == "done":
                    commander.tasks_completed += 1
                    commander.revenue_eur += r.revenue_eur
                    self.stats.tasks_completed += 1
                    self.stats.total_revenue_eur += r.revenue_eur
                    self.stats.total_tokens += r.tokens_used
                    self.stats.total_cost_usd += r.cost_usd
                else:
                    commander.tasks_failed += 1
                    self.stats.tasks_failed += 1
                self.stats.tasks_total += 1
            elif isinstance(r, Exception):
                commander.tasks_failed += 1
                self.stats.tasks_failed += 1
                self.stats.tasks_total += 1

        # Update division stats
        div_stats = self.stats.by_division.get(commander.division.value, {})
        div_stats["tasks_completed"] = div_stats.get("tasks_completed", 0) + commander.tasks_completed
        div_stats["revenue_eur"] = div_stats.get("revenue_eur", 0.0) + commander.revenue_eur

        commander.status = "ready"
        return [r for r in results if isinstance(r, WorkerTask)]

    async def run_wave(self, tasks_per_commander: int = 5) -> None:
        """Run one wave: all 100 commanders dispatch tasks simultaneously."""
        wave_start = time.time()
        logger.info(f"🌊 WAVE LAUNCHING — {len(self.commanders)} commanders × {tasks_per_commander} tasks = {len(self.commanders) * tasks_per_commander} tasks")

        # All commanders work in parallel
        wave_results = await asyncio.gather(
            *[self._run_commander_wave(cmd, tasks_per_commander) for cmd in self.commanders],
            return_exceptions=True,
        )

        elapsed = time.time() - wave_start
        total_tasks = self.stats.tasks_completed
        tps = total_tasks / max(elapsed, 0.01)

        logger.info(f"🌊 WAVE COMPLETE — {total_tasks} tasks in {elapsed:.1f}s ({tps:.0f} tasks/sec)")
        logger.info(f"   💰 Revenue: €{self.stats.total_revenue_eur:.2f} | Cost: ${self.stats.total_cost_usd:.4f} | ROI: {self.stats.roi:.0f}%")

        self.event_bus.emit("godmode.wave_complete", {
            "tasks": total_tasks,
            "elapsed_s": elapsed,
            "revenue_eur": self.stats.total_revenue_eur,
        })

    async def run_full(self, waves: int = 3, tasks_per_commander: int = 5) -> None:
        """Run multiple waves for full empire operation."""
        logger.info(f"\n🚀 GODMODE FULL LAUNCH — {waves} waves × {len(self.commanders)} commanders × {tasks_per_commander} tasks")
        logger.info(f"   Total planned: {waves * len(self.commanders) * tasks_per_commander:,} tasks\n")

        for w in range(1, waves + 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"   WAVE {w}/{waves}")
            logger.info(f"{'='*60}")
            await self.run_wave(tasks_per_commander)
            if w < waves:
                await asyncio.sleep(0.5)  # Brief pause between waves

        self._print_final_report()

    def _print_final_report(self) -> None:
        """Print the final GODMODE status report."""
        s = self.stats
        rt = s.runtime_s

        print("\n" + "═" * 70)
        print("║  🌌 GODMODE — FINAL REPORT                                          ║")
        print("═" * 70)
        print(f"  ⏱  Runtime:           {rt:.1f}s")
        print(f"  👑 Commanders:        {s.total_commanders} active")
        print(f"  🐝 Workers:           {s.total_workers:,} registered")
        print(f"  ✅ Tasks Completed:   {s.tasks_completed:,}")
        print(f"  ❌ Tasks Failed:      {s.tasks_failed:,}")
        print(f"  📊 Tasks/Second:      {s.tasks_per_second:.0f}")
        print(f"  🪙 Tokens Used:       {s.total_tokens:,}")
        print(f"  💵 Cost:              ${s.total_cost_usd:.4f}")
        print(f"  💰 Revenue:           €{s.total_revenue_eur:.2f}")
        print(f"  📈 ROI:               {s.roi:.0f}%")

        print(f"\n  {'Division':<18} {'Tasks':>8} {'Revenue':>12} {'Status'}")
        print("  " + "─" * 55)
        for div in Division:
            cfg = DIVISION_CONFIG[div]
            ds = s.by_division.get(div.value, {})
            tc = ds.get("tasks_completed", 0)
            rev = ds.get("revenue_eur", 0.0)
            print(f"  {cfg['emoji']} {div.value:<15} {tc:>8,} {rev:>11.2f}€  ✅")
        print("  " + "─" * 55)
        print(f"  🌌 {'TOTAL':<15} {s.tasks_completed:>8,} {s.total_revenue_eur:>11.2f}€  ⚡")
        print("═" * 70)

        # Top 5 Commanders
        top = sorted(self.commanders, key=lambda c: c.revenue_eur, reverse=True)[:5]
        if top:
            print(f"\n  🏆 TOP 5 COMMANDERS:")
            for i, cmd in enumerate(top, 1):
                print(f"     {i}. {cmd.commander_id} ({cmd.division.value}/{cmd.specialization}) "
                      f"— €{cmd.revenue_eur:.2f} | {cmd.tasks_completed} tasks | {cmd.success_rate:.0f}% SR")

        print("\n  🌌 GODMODE COMPLETE — Connected to the Universe ✨\n")

    async def show_status(self) -> None:
        """Show current GODMODE status."""
        await self.initialize()
        self._print_final_report()

    async def show_commanders(self) -> None:
        """Show all 100 commanders."""
        await self.initialize()
        print(f"\n{'='*80}")
        print(f"  👑 100 COMMANDER AGENTS — OLLAMA LOCAL ('Claude Offline Free')")
        print(f"{'='*80}")
        print(f"  {'ID':<16} {'Division':<14} {'Model':<22} {'Spec':<20} {'Workers':>10}")
        print("  " + "─" * 78)
        for cmd in self.commanders:
            cfg = DIVISION_CONFIG[cmd.division]
            print(f"  {cmd.commander_id:<16} {cfg['emoji']} {cmd.division.value:<11} {cmd.model:<22} {cmd.specialization:<20} {cmd.workers_managed:>10,}")
        print("  " + "─" * 78)
        print(f"  TOTAL: {len(self.commanders)} Commanders | {self.total_workers:,} Workers")
        print(f"{'='*80}\n")

    def save_state(self) -> None:
        """Save GODMODE state to disk."""
        state = {
            "timestamp": datetime.now().isoformat(),
            "stats": {
                "total_commanders": self.stats.total_commanders,
                "total_workers": self.stats.total_workers,
                "tasks_completed": self.stats.tasks_completed,
                "tasks_failed": self.stats.tasks_failed,
                "total_revenue_eur": self.stats.total_revenue_eur,
                "total_cost_usd": self.stats.total_cost_usd,
                "runtime_s": self.stats.runtime_s,
            },
            "by_division": self.stats.by_division,
            "top_commanders": [
                {
                    "id": c.commander_id,
                    "division": c.division.value,
                    "specialization": c.specialization,
                    "revenue_eur": c.revenue_eur,
                    "tasks_completed": c.tasks_completed,
                    "success_rate": c.success_rate,
                }
                for c in sorted(self.commanders, key=lambda x: x.revenue_eur, reverse=True)[:20]
            ],
        }
        with open(GODMODE_STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
        logger.info(f"💾 State saved to {GODMODE_STATE_FILE}")


# ═══════════════════════════════════════════════════════════
# SECTION 7: CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════

async def main() -> None:
    parser = argparse.ArgumentParser(
        description="🌌 GODMODE — Connect To The Universe",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python godmode_core.py                    # Full GODMODE Launch (demo)
  python godmode_core.py --demo             # Demo mode (no API calls)
  python godmode_core.py --status           # Show empire status
  python godmode_core.py --commanders       # Show all 100 commanders
  python godmode_core.py --scale 1000000    # Scale to 1M workers
  python godmode_core.py --waves 10         # Run 10 waves
  python godmode_core.py --division sales   # Launch specific division
        """,
    )
    parser.add_argument("--demo", action="store_true", default=True,
                        help="Demo mode — no real API calls (default: on)")
    parser.add_argument("--live", action="store_true",
                        help="Live mode — use real APIs")
    parser.add_argument("--status", action="store_true",
                        help="Show current GODMODE status")
    parser.add_argument("--commanders", action="store_true",
                        help="Show all 100 Commander Agents")
    parser.add_argument("--scale", type=int, default=10_000_000,
                        help="Total worker bots (default: 10M)")
    parser.add_argument("--waves", type=int, default=3,
                        help="Number of waves to run (default: 3)")
    parser.add_argument("--tasks", type=int, default=5,
                        help="Tasks per commander per wave (default: 5)")
    parser.add_argument("--division", type=str, default=None,
                        help="Run only specific division (e.g. sales, content)")

    args = parser.parse_args()

    demo = not args.live  # Demo unless --live
    gm = GodmodeCore(total_workers=args.scale, demo=demo)

    if args.status:
        await gm.show_status()
        return

    if args.commanders:
        await gm.show_commanders()
        return

    # Full launch
    await gm.initialize()
    await gm.run_full(waves=args.waves, tasks_per_commander=args.tasks)
    gm.save_state()


if __name__ == "__main__":
    asyncio.run(main())
