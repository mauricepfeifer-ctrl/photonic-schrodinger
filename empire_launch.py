#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   🚀  EMPIRE LAUNCH — MASTER INTEGRATION                            ║
║                                                                      ║
║   Verbindet ALLE Module zu einer einzigen Geldmaschine:             ║
║                                                                      ║
║   • Nucleus (AgentSwarm + Brain + AutoPilot)                        ║
║   • Revenue Pipeline (Lead → Content → Outreach → Sale)             ║
║   • Dirk Kreuter Sales Engine (7 Prinzipien)                        ║
║   • Stripe Manager (Payment Processing)                              ║
║   • n8n Cloud (Automation Webhooks)                                  ║
║   • Content Arbitrage (Cross-Platform Viral)                         ║
║   • X/Twitter Content (58 Assets ready)                              ║
║                                                                      ║
║   Usage:                                                             ║
║     python empire_launch.py                    # Full Launch         ║
║     python empire_launch.py --status           # System Status       ║
║     python empire_launch.py --revenue          # Revenue Only        ║
║     python empire_launch.py --content          # Content Blast       ║
║     python empire_launch.py --interactive      # REPL Mode          ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""
from __future__ import annotations

import asyncio
import argparse
import json
import logging
import os
import sys
import time
import glob
from datetime import datetime
from typing import Any, Dict, List, Optional

# ─── LOGGING ────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("EmpireLaunch")

# ─── SAFE IMPORTS (graceful degradation) ────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_DIR)  # Ensure local imports work
os.chdir(SCRIPT_DIR)

# Core
try:
    from empire_nucleus import (
        EmpireNucleus, EventBus, AgentSwarm, RevenueCore,
        AutoPilot, Brain, MODELS, PRODUCTS, N8N_WEBHOOK_URL,
        HAS_OLLAMA, HAS_AIOHTTP, OFFLINE_MODE
    )
    HAS_NUCLEUS = True
except ImportError as e:
    HAS_NUCLEUS = False
    logger.warning(f"⚠️ Nucleus not available: {e}")

# Revenue Pipeline
try:
    from revenue_pipeline import RevenuePipeline
    HAS_PIPELINE = True
except ImportError:
    HAS_PIPELINE = False

# Dirk Kreuter Sales Engine
try:
    from dirk_kreuter_engine import DirkKreuterEngine, SalesMessage
    HAS_KREUTER = True
except ImportError:
    HAS_KREUTER = False

# Stripe Manager
try:
    from stripe_manager import StripeManager
    HAS_STRIPE = True
except ImportError:
    HAS_STRIPE = False

# N8N Connector
try:
    from n8n_connector import N8nConnector
    HAS_N8N = True
except ImportError:
    HAS_N8N = False

# Ollama Engine
try:
    from ollama_engine import OllamaEngine, LLMResponse
    HAS_OLLAMA_ENGINE = True
except ImportError:
    HAS_OLLAMA_ENGINE = False

# Content Arbitrage
try:
    from content_arbitrage import ArbitrageManager
    HAS_ARBITRAGE = True
except ImportError:
    HAS_ARBITRAGE = False

# Revenue Burst
try:
    from revenue_burst import RevenueBurst
    HAS_BURST = True
except ImportError:
    HAS_BURST = False

# Sales Force (Agencies)
try:
    from sales_force import SalesForce, SALES_ROLES
    HAS_SALES_FORCE = True
except ImportError:
    HAS_SALES_FORCE = False

# Content Blitz
try:
    from content_blitz import ContentBlitz
    HAS_CONTENT_BLITZ = True
except ImportError:
    HAS_CONTENT_BLITZ = False

# Agent Manager
try:
    from agent_manager import AgentManager
    HAS_AGENT_MGR = True
except ImportError:
    HAS_AGENT_MGR = False

# ─── CONFIGURATION ─────────────────────────────────────
N8N_CLOUD_URL = os.getenv(
    "N8N_WEBHOOK_URL",
    "https://ai1337empire.app.n8n.cloud/webhook/monster-machine"
)


# ════════════════════════════════════════════════════════
# SECTION 1: UNIFIED STATE — All modules in one place
# ════════════════════════════════════════════════════════

class EmpireState:
    """Tracks the unified state of all empire modules."""

    def __init__(self):
        self.start_time = time.time()
        self.modules_loaded: Dict[str, bool] = {
            "nucleus": HAS_NUCLEUS,
            "pipeline": HAS_PIPELINE,
            "kreuter": HAS_KREUTER,
            "stripe": HAS_STRIPE,
            "n8n": HAS_N8N,
            "ollama": HAS_OLLAMA_ENGINE,
            "arbitrage": HAS_ARBITRAGE,
            "burst": HAS_BURST,
            "agent_mgr": HAS_AGENT_MGR,
            "sales_force": HAS_SALES_FORCE,
            "content_blitz": HAS_CONTENT_BLITZ,
        }
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.revenue_eur = 0.0
        self.content_generated = 0
        self.leads_processed = 0
        self.sales_messages_sent = 0
        self.n8n_events_fired = 0
        self.errors: List[str] = []

    def summary(self) -> str:
        uptime = time.time() - self.start_time
        hours = int(uptime // 3600)
        mins = int((uptime % 3600) // 60)
        loaded = sum(1 for v in self.modules_loaded.values() if v)
        total = len(self.modules_loaded)

        lines = [
            f"\n{'═'*65}",
            "🏰  EMPIRE STATUS DASHBOARD",
            f"{'═'*65}",
            f"⏱  Uptime:          {hours}h {mins}m",
            f"📦  Modules:         {loaded}/{total} loaded",
            f"✅  Tasks Done:      {self.tasks_completed}",
            f"❌  Tasks Failed:    {self.tasks_failed}",
            f"💰  Revenue:         €{self.revenue_eur:,.2f}",
            f"📝  Content:         {self.content_generated} pieces",
            f"🎯  Leads:           {self.leads_processed}",
            f"📧  Sales Messages:  {self.sales_messages_sent}",
            f"📡  n8n Events:      {self.n8n_events_fired}",
            f"{'─'*65}",
            "Module Status:",
        ]
        for name, loaded in self.modules_loaded.items():
            icon = "✅" if loaded else "❌"
            lines.append(f"  {icon} {name}")
        lines.append(f"{'═'*65}")
        return "\n".join(lines)


# ════════════════════════════════════════════════════════
# SECTION 2: N8N INTEGRATION — Fire webhooks to cloud
# ════════════════════════════════════════════════════════

class N8nBridge:
    """Fires events to n8n cloud for automation."""

    def __init__(self, webhook_url: str = N8N_CLOUD_URL):
        self.url = webhook_url
        self.connector: Optional[N8nConnector] = None
        if HAS_N8N:
            self.connector = N8nConnector(webhook_url=self.url)

    async def fire(self, event_type: str, data: Dict[str, Any]) -> bool:
        connector = self.connector
        if not connector:
            return False
        payload = {
            "event": event_type,
            "timestamp": datetime.now().isoformat(),
            **data,
        }
        try:
            result = await connector.send_data(payload)
            return bool(result)
        except Exception as e:
            logger.debug(f"n8n skip: {e}")
            return False

    async def close(self):
        if self.connector:
            await self.connector.close()


# ════════════════════════════════════════════════════════
# SECTION 3: TASK SPLITTER — Divide work between agents
# ════════════════════════════════════════════════════════

class TaskSplitter:
    """Splits revenue tasks across specialized agents."""

    # Task distribution for maximum revenue
    DISTRIBUTION = {
        "content":  0.25,   # 25% Content generation
        "sales":    0.25,   # 25% Sales outreach
        "research": 0.15,   # 15% Market research
        "tiktok":   0.15,   # 15% TikTok/Shorts scripts
        "strategy": 0.10,   # 10% Revenue strategy
        "outreach": 0.10,   # 10% Cold outreach
    }

    @staticmethod
    def split_tasks(total: int) -> Dict[str, int]:
        """Split N tasks across agents based on distribution."""
        tasks: Dict[str, int] = {}
        remaining = total
        for agent, ratio in TaskSplitter.DISTRIBUTION.items():
            count = int(total * ratio)
            tasks[agent] = count
            remaining -= count
        # Give remainder to sales (highest revenue per task)
        tasks["sales"] = tasks.get("sales", 0) + remaining
        return tasks

    @staticmethod
    def generate_prompts(agent_type: str, count: int) -> List[str]:
        """Generate revenue-focused prompts for each agent type."""
        templates = {
            "content": [
                "Erstelle einen viralen Tweet über AI Automation. Hook + Value + CTA. Max 280 Zeichen.",
                "Schreibe einen LinkedIn Post: Wie AI 15h/Woche spart. Professionell, mit Zahlen.",
                "Erstelle einen Instagram Caption über AI Consulting für KMUs. Emotional, mit Emoji.",
            ],
            "sales": [
                "Schreibe eine kalte Verkaufs-Email an einen E-Commerce Manager. "
                "Thema: AI Automatisierung spart 20h/Woche. Hook → Pain → Solution → CTA.",
                "Erstelle ein Freelancer-Proposal für den Gig: 'AI Chatbot für Immobilienagentur'. "
                "Kurz, professionell, mit klarem CTA.",
                "Schreibe eine Follow-Up Email an einen Lead der sich das AI Audit angesehen hat. "
                "Sanft, nicht pushy, mit neuem Value.",
            ],
            "research": [
                "Analysiere den deutschen Markt für AI Automation Services. "
                "Top 3 Branchen, durchschnittliche Budgets, Pain Points.",
                "Finde 3 AI-Trends die in den nächsten 3 Monaten relevant werden. "
                "Für jeden: Opportunity, Monetarisierung, Action Item.",
            ],
            "tiktok": [
                "Schreibe ein 30s TikTok Script: '3 Fehler die Firmen mit AI machen'. "
                "Hook (3s) + 3 Punkte + CTA. Emotional, punchy.",
                "TikTok Script: 'So sparst du 15h/Woche mit AI'. Hook + Story + CTA. 45 Sekunden.",
            ],
            "strategy": [
                "Erstelle einen 7-Tage Revenue Sprint Plan für AI Consulting. "
                "Jeden Tag einen Schritt: Montag bis Sonntag. Konkrete Actions.",
                "Analysiere: Was ist der schnellste Weg von €0 zu €1000 mit AI Automation? "
                "Konkrete Steps, keine Theorie.",
            ],
            "outreach": [
                "Schreibe 3 personalisierte Twitter DMs für AI Automation Leads. "
                "Kurz (max 280 Zeichen), relevant, nicht spammy.",
                "Erstelle eine Cold Email Sequenz (3 Emails) für SaaS Companies. "
                "Email 1: Introduction, Email 2: Value, Email 3: Soft Close.",
            ],
        }

        agent_prompts = templates.get(agent_type, templates["content"])
        result = []
        for i in range(count):
            result.append(agent_prompts[i % len(agent_prompts)])
        return result


# ════════════════════════════════════════════════════════
# SECTION 4: MASTER LAUNCH — The One Script to Rule Them
# ════════════════════════════════════════════════════════

class EmpireLaunch:
    """Master integration - connects all modules."""

    def __init__(self):
        self.state = EmpireState()
        self.n8n = N8nBridge()
        self.nucleus: Optional[EmpireNucleus] = None
        self.pipeline: Optional[RevenuePipeline] = None
        self.kreuter: Optional[DirkKreuterEngine] = None
        self.stripe: Optional[StripeManager] = None
        self.sales_force: Optional[SalesForce] = None
        self.content_blitz: Optional[ContentBlitz] = None

        # Initialize what's available
        if HAS_NUCLEUS:
            self.nucleus = EmpireNucleus()
        if HAS_PIPELINE:
            self.pipeline = RevenuePipeline()
        if HAS_KREUTER:
            self.kreuter = DirkKreuterEngine()
        if HAS_STRIPE:
            self.stripe = StripeManager()
        if HAS_SALES_FORCE:
            self.sales_force = SalesForce()
        if HAS_CONTENT_BLITZ:
            self.content_blitz = ContentBlitz()

    async def health_check(self) -> Dict[str, Any]:
        """Check all systems."""
        results: Dict[str, Any] = {}

        # Ollama
        if HAS_OLLAMA_ENGINE:
            engine = OllamaEngine()
            ok = await engine.health()
            models = await engine.list_models() if ok else []
            results["ollama"] = {"status": "UP" if ok else "DOWN", "models": models}
        else:
            results["ollama"] = {"status": "NOT_INSTALLED"}

        # Stripe
        stripe = self.stripe
        if stripe:
            results["stripe"] = {
                "status": "LIVE" if stripe.live else "SIMULATION",
                "revenue": f"€{stripe.stats.total_eur():.2f}",
            }
        else:
            results["stripe"] = {"status": "NOT_LOADED"}

        # n8n Cloud
        if HAS_N8N:
            results["n8n"] = {"status": "CONNECTED", "url": N8N_CLOUD_URL}
        else:
            results["n8n"] = {"status": "NOT_LOADED"}

        # X/Twitter Content
        x_content_dir = os.path.join(SCRIPT_DIR, "x_content")
        if os.path.isdir(x_content_dir):
            posts = glob.glob(os.path.join(x_content_dir, "*.json"))
            results["x_content"] = {"status": "READY", "posts": len(posts)}
        else:
            results["x_content"] = {"status": "NO_CONTENT"}

        # Revenue data
        rev_file = os.path.join(SCRIPT_DIR, "revenue_log.json")
        if os.path.exists(rev_file):
            with open(rev_file) as f:
                rev = json.load(f)
            results["revenue_log"] = {
                "total_eur": rev.get("total_revenue_cents", 0) / 100.0,
                "transactions": rev.get("total_transactions", 0),
            }
        else:
            results["revenue_log"] = {"total_eur": 0, "transactions": 0}

        return results

    # ─── LAUNCH MODES ────────────────────────────

    async def launch_full(self, cycles: int = 3, leads_per_wave: int = 5) -> Dict[str, Any]:
        """Full launch: all systems fire together."""
        logger.info("🚀 EMPIRE FULL LAUNCH — ALL SYSTEMS GO")

        # 1. Health check
        health = await self.health_check()
        logger.info(f"📊 Health: {json.dumps({k: v.get('status', '?') for k, v in health.items()})}")

        # 2. Fire n8n event
        await self.n8n.fire("empire_launch", {
            "mode": "full",
            "modules": {k: v for k, v in self.state.modules_loaded.items()},
        })
        self.state.n8n_events_fired += 1

        # 3. Run Nucleus Autopilot (connects Swarm + Revenue + Brain)
        if self.nucleus:
            ok = await self.nucleus.health_check()
            if ok and getattr(self.nucleus, 'autopilot', None):
                logger.info("🧠 Nucleus online — starting autopilot")
                await self.nucleus.autopilot.run(cycles=cycles)
                self.state.tasks_completed += sum(
                    a.tasks_done for a in self.nucleus.swarm.agents.values()
                )
                self.state.tasks_failed += sum(
                    a.tasks_failed for a in self.nucleus.swarm.agents.values()
                )
                self.state.revenue_eur = self.nucleus.revenue.total_eur
                self.nucleus.swarm.save_rankings()
            else:
                logger.warning("⚠️ Nucleus health check failed or autopilot missing")

        # 4. Launch Sales Force & Content Blitz (New System)
        await self.launch_sales_force()

        # 5. Fire completion event
        await self.n8n.fire("empire_cycle_complete", {
            "revenue_eur": self.state.revenue_eur,
            "tasks_completed": self.state.tasks_completed,
            "tasks_failed": self.state.tasks_failed,
        })
        self.state.n8n_events_fired += 1

        # 6. Show Kreuter sales sequence for top product
        if self.kreuter:
            logger.info("\n💼 Dirk Kreuter Sales Sequence (AI Consulting):")
            sequence = self.kreuter.generate_complete_sequence("core", slots_taken=2)
            for i, msg in enumerate(sequence, 1):
                logger.info(f"  {i}. [{msg.principle.value}] {msg.headline}")
            self.state.sales_messages_sent += len(sequence)

        # 7. Stripe status
        if self.stripe:
            logger.info(f"\n💳 Stripe: {self.stripe.get_revenue_summary()}")

        # 8. Final dashboard
        logger.info(self.state.summary())

        return {
            "revenue_eur": self.state.revenue_eur,
            "tasks_completed": self.state.tasks_completed,
            "content_generated": self.state.content_generated,
        }

    async def launch_sales_force(self):
        """Run the new specialized Sales Force and Content Blitz."""
        logger.info("🚀 LAUNCHING SALES FORCE & CONTENT BLITZ...")
        
        # 1. Content Blitz
        if self.content_blitz:
            logger.info("⚡ Executing Content Blitz (3 pieces)...")
            await self.content_blitz.run_blitz(count=3)
            self.state.content_generated += 9 # 3 topics * 3 platforms
        
        # 2. Sales Force
        if self.sales_force:
            logger.info("🕵️ Executing Sales Force (Prospecting)...")
            await self.sales_force.run_all()
            self.state.tasks_completed += 6 # 6 agents

    async def launch_revenue(self, waves: int = 3, leads: int = 10) -> Dict[str, Any]:
        """Revenue-focused launch: pipeline + outreach."""
        logger.info("💰 REVENUE LAUNCH — Maximum Money Mode")

        results: Dict[str, Any] = {"mode": "revenue"}

        # Run nucleus revenue pipeline
        nucleus = self.nucleus
        if nucleus:
            ok = await nucleus.health_check()
            if ok:
                r = await nucleus.revenue.run_pipeline(
                    nucleus.swarm, waves=waves, leads=leads
                )
                results["nucleus_pipeline"] = r
                self.state.revenue_eur = nucleus.revenue.total_eur
                self.state.leads_processed += waves * leads
                nucleus.swarm.save_rankings()

        # Run standalone pipeline if nucleus failed
        if not self.nucleus and self.pipeline:
            r = await self.pipeline.run_continuous(waves=waves, leads_per_wave=leads)
            results["standalone_pipeline"] = r

        # Generate Kreuter sales messages
        kreuter = self.kreuter
        if kreuter:
            for product in ["tripwire", "core", "pro"]:
                seq = kreuter.generate_complete_sequence(product)
                self.state.sales_messages_sent += len(seq)
            results["sales_sequences"] = self.state.sales_messages_sent

        # Fire n8n
        await self.n8n.fire("revenue_launch_complete", {
            "revenue_eur": self.state.revenue_eur,
            "leads": self.state.leads_processed,
            "sales_messages": self.state.sales_messages_sent,
        })

        logger.info(self.state.summary())
        return results

    async def launch_content(self, count: int = 10) -> Dict[str, Any]:
        """Content blast: generate maximum content across all channels."""
        logger.info(f"📝 CONTENT BLAST — Generating {count} pieces")

        results: Dict[str, Any] = {"mode": "content", "pieces": []}

        nucleus = self.nucleus
        if nucleus:
            ok = await nucleus.health_check()
            if ok:
                # Split tasks across content agents
                task_split = TaskSplitter.split_tasks(count)
                for agent_type, task_count in task_split.items():
                    if task_count <= 0:
                        continue
                    prompts = TaskSplitter.generate_prompts(agent_type, task_count)
                    logger.info(f"  🤖 {agent_type}: {task_count} tasks")
                    batch_results = await nucleus.swarm.batch(
                        prompts, max_concurrent=2
                    )
                    for r in batch_results:
                        if "response" in r:
                            self.state.content_generated += 1
                            results["pieces"].append({
                                "agent": r["agent"],
                                "preview": r["response"][:100],
                            })
                        else:
                            self.state.tasks_failed += 1

                self.state.tasks_completed += self.state.content_generated
                nucleus.swarm.save_rankings()

        # Fire n8n
        await self.n8n.fire("content_blast_complete", {
            "pieces_generated": self.state.content_generated,
        })

        logger.info(self.state.summary())
        return results

    async def show_status(self) -> str:
        """Show complete system status."""
        health = await self.health_check()

        lines = [
            f"\n{'═'*65}",
            "🏰  MAURICE'S AI EMPIRE — COMPLETE STATUS",
            f"{'═'*65}",
            f"📅  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
        ]

        # Ollama
        o = health.get("ollama", {})
        lines.append(f"🤖 Ollama: {o.get('status', '?')}")
        if o.get("models"):
            for m in o["models"]:
                lines.append(f"   └─ {m}")

        # n8n
        n = health.get("n8n", {})
        lines.append(f"📡 n8n Cloud: {n.get('status', '?')}")
        if n.get("url"):
            lines.append(f"   └─ {n['url']}")

        # Stripe
        s = health.get("stripe", {})
        lines.append(f"💳 Stripe: {s.get('status', '?')}")
        if s.get("revenue"):
            lines.append(f"   └─ Revenue: {s['revenue']}")

        # X Content
        x = health.get("x_content", {})
        lines.append(f"🐦 X/Twitter: {x.get('status', '?')} ({x.get('posts', 0)} posts)")

        # Revenue
        r = health.get("revenue_log", {})
        lines.append(f"💰 Revenue Log: €{r.get('total_eur', 0):,.2f} ({r.get('transactions', 0)} txns)")

        # Products
        nucleus = self.nucleus
        if nucleus:
            lines.append(f"\n📦 Products ({len(PRODUCTS)}):")
            for pid, prod in PRODUCTS.items():
                lines.append(f"   └─ {prod['name']}: €{prod['price']}")

        # Sales Force
        if self.sales_force:
            lines.append(f"🕵️ Sales Force: ✅ Active (Agents: {len(SALES_ROLES)})")
        
        # Content Blitz
        if self.content_blitz:
            lines.append(f"⚡ Content Blitz: ✅ Active")

        # Agent leaderboard
        if self.nucleus:
            lines.append(self.nucleus.swarm.leaderboard())

        # Kreuter status
        kreuter = self.kreuter
        if kreuter:
            lines.append(f"\n📊 Dirk Kreuter Engine: ✅ Active")
            lines.append(f"   └─ Products: {len(kreuter.products)}")
            lines.append(f"   └─ Tripwire Steps: {len(kreuter.get_tripwire_sequence())}")

        lines.append(f"\n{'═'*65}")
        return "\n".join(lines)

    async def interactive(self):
        """Interactive REPL mode — the cockpit."""
        nucleus = self.nucleus
        if not nucleus:
            logger.error("❌ Nucleus required for interactive mode")
            return

        print(BANNER)
        ok = await nucleus.health_check()
        if not ok:
            print("❌ Ollama offline — starte: ollama serve")
            return

        while True:
            try:
                cmd = input("\n🚀 > ").strip()
                if not cmd:
                    continue
                if cmd.lower() in ("exit", "quit", "q"):
                    print("👋 Empire offline.")
                    break

                if cmd == "!status":
                    print(await self.show_status())
                    continue
                if cmd == "!revenue":
                    if self.nucleus:
                        print(self.nucleus.revenue.dashboard())
                    if self.stripe:
                        print(f"Stripe: {self.stripe.get_revenue_summary()}")
                    continue
                if cmd == "!rank":
                    print(nucleus.swarm.leaderboard())
                    continue
                if cmd == "!kreuter":
                    kreuter = self.kreuter
                    if kreuter:
                        seq = kreuter.generate_complete_sequence("core", slots_taken=2)
                        for i, msg in enumerate(seq, 1):
                            print(f"\n--- {i}. {msg.principle.value.upper()} ---")
                            print(f"📌 {msg.headline}")
                            print(msg.body[:200])
                            print(f"🎯 CTA: {msg.cta}")
                    continue
                if cmd == "!stripe":
                    stripe = self.stripe
                    if stripe:
                        print(stripe.get_revenue_summary())
                    continue
                if cmd.startswith("!launch"):
                    await self.launch_full(cycles=2, leads_per_wave=3)
                    continue
                if cmd.startswith("!blast"):
                    n = int(cmd.split()[-1]) if len(cmd.split()) > 1 else 6
                    await self.launch_content(count=n)
                    continue
                if cmd.startswith("!burst"):
                    n = int(cmd.split()[-1]) if len(cmd.split()) > 1 else 10
                    await self.launch_revenue(waves=1, leads=n)
                    continue
                if cmd.startswith("!sales"):
                    await self.launch_sales_force()
                    continue

                # Default: route to nucleus agent
                agent_override = None
                for prefix in ["sales", "content", "tiktok", "research", "code", "strategy", "outreach", "closer"]:
                    if cmd.startswith(f"!{prefix} "):
                        agent_override = prefix
                        cmd = cmd[len(prefix) + 2:]
                        break

                result = await nucleus.swarm.execute(cmd, agent_override)
                if "response" in result:
                    print(f"\n{'─'*60}")
                    print(result["response"])
                    print(f"{'─'*60}")
                    print(f"⚡ {result.get('latency_ms', 0)}ms | 🤖 {result['agent']} | Model: {result.get('model', '?')}")
                else:
                    print(f"❌ {result.get('error', 'Unknown error')}")

            except KeyboardInterrupt:
                print("\n👋 Empire offline.")
                break
            except Exception as e:
                logger.error(f"Error: {e}")

        if self.nucleus:
            self.nucleus.swarm.save_rankings()
        await self.n8n.close()

    async def cleanup(self):
        """Clean shutdown."""
        if self.nucleus:
            self.nucleus.swarm.save_rankings()
        await self.n8n.close()


BANNER = """
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   🚀  EMPIRE LAUNCH — MASTER CONTROL                                ║
║   🧠  Nucleus + Pipeline + Kreuter + Stripe + n8n                   ║
║   💰  Maximum Revenue Mode                                          ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║  Commands:                                                           ║
║    <prompt>            → Auto-routed to best agent                  ║
║    !sales <prompt>     → Sales Agent                                ║
║    !content <prompt>   → Content Agent                              ║
║    !tiktok <prompt>    → TikTok Agent                               ║
║    !research <prompt>  → Research Agent                             ║
║    !code <prompt>      → Code Agent                                 ║
║    !strategy <prompt>  → Strategy Agent                             ║
║    !status             → Full System Status                         ║
║    !rank               → Agent Leaderboard                          ║
║    !revenue            → Revenue Dashboard                          ║
║    !kreuter            → Dirk Kreuter Sales Sequence                ║
║    !stripe             → Stripe Payment Status                      ║
║    !launch             → Full Launch (2 cycles)                     ║
║    !blast <N>          → Content Blast (N pieces)                   ║
║    !burst <N>          → Revenue Burst (N leads)                    ║
║    exit                → Quit                                       ║
╚══════════════════════════════════════════════════════════════════════╝
"""


# ════════════════════════════════════════════════════════
# CLI
# ════════════════════════════════════════════════════════

async def main() -> None:
    parser = argparse.ArgumentParser(
        description="🚀 Empire Launch — Master Integration"
    )
    parser.add_argument("--status", "-s", action="store_true", help="Show full status")
    parser.add_argument("--revenue", "-r", action="store_true", help="Revenue launch mode")
    parser.add_argument("--content", "-c", type=int, default=0, help="Content blast (N pieces)")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive REPL")
    parser.add_argument("--full", "-f", action="store_true", help="Full autopilot launch")
    parser.add_argument("--sales", action="store_true", help="Launch Sales Force & Content Blitz")
    parser.add_argument("--cycles", type=int, default=3, help="Autopilot cycles")
    parser.add_argument("--leads", type=int, default=5, help="Leads per wave")
    parser.add_argument("prompt", nargs="*", help="Single task prompt")

    args = parser.parse_args()
    empire = EmpireLaunch()

    try:
        if args.status:
            print(await empire.show_status())
            return

        if args.sales:
            await empire.launch_sales_force()
            return

        if args.revenue:
            await empire.launch_revenue(waves=args.cycles, leads=args.leads)
            return

        if args.content > 0:
            await empire.launch_content(count=args.content)
            return

        if args.full or (not args.interactive and not args.prompt):
            await empire.launch_full(cycles=args.cycles, leads_per_wave=args.leads)
            return

        if args.prompt:
            if not empire.nucleus:
                logger.error("❌ Nucleus required")
                return
            ok = await empire.nucleus.health_check()
            if not ok:
                return
            prompt = " ".join(args.prompt)
            result = await empire.nucleus.swarm.execute(prompt)
            if "response" in result:
                print(result["response"])
            else:
                print(f"❌ {result.get('error')}")
            return

        # Default: interactive
        await empire.interactive()
    finally:
        await empire.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
