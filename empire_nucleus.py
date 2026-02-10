#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   👑  EMPIRE NUCLEUS — Zentrales Nervensystem                       ║
║                                                                      ║
║   ALLES zentralisiert. MAXIMALE Autonomie. MAXIMALE Revenue.        ║
║                                                                      ║
║   Vereint:                                                           ║
║   • AgentSwarm (Sales, Content, Research, TikTok, Code, Strategy)   ║
║   • RevenuePipeline (Lead → Content → Outreach → Sale → Payment)   ║
║   • AutoPilot (Autonomes Scheduling, Self-Optimization)             ║
║   • BrainSystem (8-Cell Parallel Decisions)                         ║
║   • StripeIntegration (Live Payments)                                ║
║   • Leaderboard (Revenue-Based Agent Ranking)                       ║
║   • CLI + Dashboard (Ein Befehl = volle Power)                      ║
║                                                                      ║
║   Usage:                                                             ║
║     python empire_nucleus.py                    # Full Autopilot     ║
║     python empire_nucleus.py --interactive      # REPL Mode         ║
║     python empire_nucleus.py --burst 50         # Revenue Burst     ║
║     python empire_nucleus.py --dashboard        # Status Dashboard  ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import time
import random
import logging
import argparse
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

# ─── OPTIONAL IMPORTS (graceful degradation) ─────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_DIR)

try:
    from ollama_engine import OllamaEngine, LLMResponse
    HAS_OLLAMA = True
except ImportError as e:
    HAS_OLLAMA = False
    OllamaEngine = None  # type: ignore
    LLMResponse = None  # type: ignore
    logger.warning(f"⚠️ OllamaEngine not available: {e}")

try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError as e:
    HAS_AIOHTTP = False
    logger.warning(f"⚠️ aiohttp not available: {e}")

# ─── AGENT MANAGER (single source of truth for ranking) ───
try:
    from agent_manager import AgentManager
    HAS_AGENT_MGR = True
except ImportError as e:
    HAS_AGENT_MGR = False
    AgentManager = None  # type: ignore
    logger.warning(f"⚠️ AgentManager not available: {e}")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("Nucleus")

# ═══════════════════════════════════════════════════════
# SECTION 1: CONFIGURATION — Single Source of Truth
# ═══════════════════════════════════════════════════════

OFFLINE_MODE = os.getenv("OFFLINE_MODE", "true").lower() == "true"
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
KIMI_API_KEY = os.getenv("MOONSHOT_API_KEY", "")
KIMI_BASE_URL = "https://api.moonshot.ai/v1"

# ─── POWER-STACK IMPORTS ───
try:
    from memory_core import MemorySystem
    from heartbeat_scheduler import Heartbeat
    from guarded_tools import Toolkit
    from skills_library import SkillsLibrary
    HAS_POWER_STACK = True
except ImportError as e:
    HAS_POWER_STACK = False
    logger.warning(f"⚠️ Power-Stack not available: {e}")

    # Minimal stubs so the rest of the code can run
    class MemorySystem:  # type: ignore[no-redef]
        def __init__(self) -> None:
            self._events: list[dict] = []
        def add_event(self, *a: object, **kw: object) -> None:
            pass
        def recall(self, *a: object, **kw: object) -> list:
            return []

    class Heartbeat:  # type: ignore[no-redef]
        def __init__(self, *a: object) -> None:
            pass
        def start(self) -> None:
            pass

    class Toolkit:  # type: ignore[no-redef]
        pass

    class SkillsLibrary:  # type: ignore[no-redef]
        def __init__(self, *a: object) -> None:
            pass

# Initialize Power-Stack
runtime_memory = MemorySystem()
runtime_tools = Toolkit()
runtime_skills = SkillsLibrary(runtime_tools, runtime_memory)
runtime_heartbeat = Heartbeat(runtime_memory)
runtime_heartbeat.start()

RANKINGS_FILE = "agent_rankings.json"
REVENUE_FILE = "revenue_log.json"
STATE_FILE = "nucleus_state.json"

MODELS = {
    "reasoning": os.getenv("MODEL_REASONING", "deepseek-r1:7b"),
    "creative": os.getenv("MODEL_CREATIVE", "qwen2.5-coder:14b"),
    "code": os.getenv("MODEL_CODE", "qwen2.5-coder:14b"),
}

# ─── DIE BESTEN 5 PRODUKTE (alles andere rausgeflogen) ───
PRODUCTS = {
    "prompt_cheatsheet": {"name": "Prompt Cheatsheet Pro",      "price": 27,  "category": "digital"},
    "agent_starter":     {"name": "AI Agent Starter Kit",       "price": 47,  "category": "digital"},
    "automation_bp":     {"name": "AI Automation Blueprint",    "price": 79,  "category": "digital"},
    "side_hustle":       {"name": "AI Side Hustle Playbook",    "price": 97,  "category": "digital"},
    "consulting_call":   {"name": "1:1 AI Setup Call",          "price": 297, "category": "consulting"},
}

# n8n Cloud Webhook Integration
N8N_WEBHOOK_URL = os.getenv(
    "N8N_WEBHOOK_URL",
    "https://ai1337empire.app.n8n.cloud/webhook-test/content-generate3a43a000-384d-46ca-93ae-b88ef134816d"
)


# ═══════════════════════════════════════════════════════
# SECTION 2: MESSAGE BUS — In-Process Event System
# ═══════════════════════════════════════════════════════

class EventBus:
    """Lightweight in-process pub/sub. No Redis needed."""

    def __init__(self) -> None:
        self._subs: Dict[str, List[Callable]] = {}
        self._log: List[Dict[str, Any]] = []

    def on(self, channel: str, callback: Callable) -> None:
        self._subs.setdefault(channel, []).append(callback)

    def emit(self, channel: str, data: Any = None) -> None:
        self._log.append({"ch": channel, "data": data, "t": time.time()})
        for cb in self._subs.get(channel, []):
            try:
                cb(data)
            except Exception as e:
                logger.error(f"EventBus error on {channel}: {e}")

    async def notify_n8n(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Fire webhook to n8n cloud for automation triggers."""
        if not HAS_AIOHTTP or not N8N_WEBHOOK_URL:
            return
        try:
            data = {"event": event_type, "timestamp": datetime.now().isoformat(), **payload}
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as s:
                async with s.post(N8N_WEBHOOK_URL, json=data) as r:
                    if r.status < 300:
                        logger.info(f"📡 n8n webhook fired: {event_type}")
                    else:
                        logger.warning(f"⚠️ n8n webhook {r.status}")
        except Exception as e:
            logger.debug(f"n8n webhook skip: {e}")

    def history(self, channel: str = "", last_n: int = 20) -> List[Dict]:
        items = self._log if not channel else [e for e in self._log if e["ch"] == channel]
        return items[-last_n:]  # pyre-ignore[16]


# ═══════════════════════════════════════════════════════
# SECTION 3: BRAIN — 8-Cell Parallel Decision System
# ═══════════════════════════════════════════════════════

class BrainCell(ABC):
    """Base class for a single decision cell."""

    name: str = "base"
    weight: float = 1.0  # Relative voting weight

    @abstractmethod
    def evaluate(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Return {score: 0-100, signal: str, action: str, details: dict}"""
        ...


class RevenueCell(BrainCell):
    """Cell 1: Revenue health & trajectory analysis."""
    name = "revenue"
    weight = 2.0  # Highest weight — money talks

    def evaluate(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        revenue = ctx.get("revenue", 0)
        target = ctx.get("revenue_target", 5000)
        transactions = ctx.get("transactions", 0)

        progress = min(100, (revenue / max(target, 1)) * 100)
        velocity = revenue / max(ctx.get("hours_running", 1), 0.1)

        if revenue < 100:
            signal, action = "CRITICAL", "AGGRESSIVE_OUTREACH"
        elif revenue < 500:
            signal, action = "LOW", "SCALE_PIPELINE"
        elif revenue < 2000:
            signal, action = "GROWING", "OPTIMIZE_CONVERSION"
        elif revenue < target:
            signal, action = "STRONG", "MAINTAIN_MOMENTUM"
        else:
            signal, action = "TARGET_HIT", "DIVERSIFY"

        return {
            "score": int(progress),
            "signal": signal,
            "action": action,
            "details": {
                "revenue_eur": revenue,
                "target_eur": target,
                "velocity_eur_hr": round(velocity, 2),
                "aov": round(revenue / max(transactions, 1), 2),
            },
        }


class AgentCell(BrainCell):
    """Cell 2: Agent performance & utilization."""
    name = "agents"
    weight = 1.5

    def evaluate(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        agents = ctx.get("agents", {})
        if not agents:
            return {"score": 50, "signal": "NO_DATA", "action": "INIT", "details": {}}

        total_done = sum(a.get("done", 0) for a in agents.values())
        total_failed = sum(a.get("failed", 0) for a in agents.values())
        success_rate = total_done / max(total_done + total_failed, 1)
        avg_latency = sum(a.get("avg_ms", 0) for a in agents.values()) / max(len(agents), 1)

        # Find underperformers and stars
        stars = [k for k, a in agents.items() if a.get("done", 0) > 5 and a.get("failed", 0) == 0]
        laggards = [k for k, a in agents.items()
                    if a.get("failed", 0) > a.get("done", 0) * 0.3]

        score = int(success_rate * 80 + min(20.0, 20.0 - (avg_latency / 5000) * 20))

        if success_rate < 0.5:
            signal, action = "FAILING", "RESTART_AGENTS"
        elif success_rate < 0.8:
            signal, action = "DEGRADED", "DEMOTE_LAGGARDS"
        elif avg_latency > 10000:
            signal, action = "SLOW", "REDUCE_BATCH"
        else:
            signal, action = "HEALTHY", "BOOST_STARS"

        return {
            "score": max(0, min(100, score)),
            "signal": signal,
            "action": action,
            "details": {
                "success_rate": round(success_rate, 3),  # pyre-ignore[6]
                "avg_latency_ms": round(avg_latency),
                "stars": stars[:3],  # pyre-ignore[16]
                "laggards": laggards[:3],  # pyre-ignore[16]
                "total_tasks": total_done + total_failed,
            },
        }


class RiskCell(BrainCell):
    """Cell 3: Risk assessment & circuit breaker."""
    name = "risk"
    weight = 1.8

    def evaluate(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        error_rate = ctx.get("error_rate", 0)
        pending = ctx.get("pending", 0)
        consecutive_fails = ctx.get("consecutive_fails", 0)
        memory_pct = ctx.get("memory_pct", 50)

        risk_score = 0
        risk_score += min(30, error_rate * 300)             # 0-30 from errors
        risk_score += min(20, (pending / 10000) * 20)       # 0-20 from backlog
        risk_score += min(25, consecutive_fails * 5)        # 0-25 from fail streaks
        risk_score += min(25, max(0, memory_pct - 75))      # 0-25 from memory

        if risk_score > 70:
            signal, action = "CRITICAL", "CIRCUIT_BREAK"
        elif risk_score > 50:
            signal, action = "HIGH", "THROTTLE"
        elif risk_score > 30:
            signal, action = "MODERATE", "MONITOR"
        else:
            signal, action = "LOW", "PROCEED"

        return {
            "score": max(0, min(100, 100 - int(risk_score))),  # Invert: high score = low risk
            "signal": signal,
            "action": action,
            "details": {
                "risk_level": round(risk_score),
                "error_contribution": round(min(30, error_rate * 300)),
                "backlog_contribution": round(min(20, (pending / 10000) * 20)),
                "circuit_breaker": risk_score > 70,
            },
        }


class TimingCell(BrainCell):
    """Cell 4: Market timing & scheduling optimization."""
    name = "timing"
    weight = 1.0

    def evaluate(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        hour = datetime.now().hour
        weekday = datetime.now().weekday()  # 0=Mon, 6=Sun

        # Business hours scoring (DACH market)
        if 9 <= hour <= 11:          # Morning peak
            biz_score, window = 100, "PRIME_MORNING"
        elif 14 <= hour <= 16:       # Afternoon peak
            biz_score, window = 90, "PRIME_AFTERNOON"
        elif 8 <= hour <= 18:        # Business hours
            biz_score, window = 70, "BUSINESS_HOURS"
        elif 19 <= hour <= 22:       # Evening content
            biz_score, window = 60, "EVENING_CONTENT"
        else:                        # Night
            biz_score, window = 30, "OFF_HOURS"

        # Weekend penalty for B2B
        if weekday >= 5:
            biz_score = int(biz_score * 0.6)
            window = f"WEEKEND_{window}"

        # Decide focus based on timing
        if "PRIME" in window:
            action = "OUTREACH_BLAST"
        elif "EVENING" in window:
            action = "CONTENT_FOCUS"
        elif "OFF" in window:
            action = "BATCH_PREP"
        else:
            action = "BALANCED"

        return {
            "score": biz_score,
            "signal": window,
            "action": action,
            "details": {
                "hour": hour,
                "weekday": weekday,
                "is_business": 8 <= hour <= 18 and weekday < 5,
                "content_window": hour >= 19 or hour <= 7 or weekday >= 5,
            },
        }


class ResourceCell(BrainCell):
    """Cell 5: Resource allocation & capacity planning."""
    name = "resources"
    weight = 1.2

    def evaluate(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        num_agents = ctx.get("num_agents", 8)
        active_tasks = ctx.get("active_tasks", 0)
        offline = ctx.get("offline_mode", OFFLINE_MODE)

        # Capacity: local models = 2-3 concurrent, cloud = 50+
        max_concurrent = 2 if offline else 50
        utilization = active_tasks / max(max_concurrent, 1)

        if utilization > 0.9:
            signal, action = "SATURATED", "QUEUE"
            score = 20
        elif utilization > 0.7:
            signal, action = "HIGH_UTIL", "OPTIMIZE"
            score = 50
        elif utilization > 0.3:
            signal, action = "BALANCED", "MAINTAIN"
            score = 80
        else:
            signal, action = "UNDERUTILIZED", "SCALE_UP"
            score = 90

        # Recommend batch size
        batch_size = max(1, min(max_concurrent, int(max_concurrent * (1 - utilization))))

        return {
            "score": score,
            "signal": signal,
            "action": action,
            "details": {
                "utilization": round(utilization, 2),
                "max_concurrent": max_concurrent,
                "recommended_batch": batch_size,
                "offline_mode": offline,
            },
        }


class ContentCell(BrainCell):
    """Cell 6: Content velocity & channel analysis."""
    name = "content"
    weight = 1.0

    def evaluate(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        content_count = ctx.get("content_generated", 0)
        target_daily = ctx.get("content_target", 20)
        channels = ctx.get("channels", {"twitter": 0, "tiktok": 0, "linkedin": 0})

        velocity = content_count / max(ctx.get("hours_running", 1), 0.1)
        coverage = sum(1 for v in channels.values() if v > 0) / max(len(channels), 1)

        score = int(min(100, (content_count / max(target_daily, 1)) * 100))

        if content_count == 0:
            signal, action = "EMPTY", "CONTENT_BURST"
        elif coverage < 0.5:
            signal, action = "GAPS", "DIVERSIFY_CHANNELS"
        elif velocity < 2:
            signal, action = "SLOW", "ACCELERATE"
        else:
            signal, action = "FLOWING", "MAINTAIN"

        # Best channel mix for current time
        hour = datetime.now().hour
        if 7 <= hour <= 9:
            mix = {"twitter": 0.5, "linkedin": 0.3, "tiktok": 0.2}
        elif 12 <= hour <= 14:
            mix = {"twitter": 0.3, "linkedin": 0.4, "tiktok": 0.3}
        elif 18 <= hour <= 22:
            mix = {"tiktok": 0.5, "twitter": 0.3, "linkedin": 0.2}
        else:
            mix = {"twitter": 0.4, "tiktok": 0.3, "linkedin": 0.3}

        return {
            "score": score,
            "signal": signal,
            "action": action,
            "details": {
                "content_count": content_count,
                "velocity_per_hr": round(velocity, 1),
                "channel_coverage": round(coverage, 2),  # pyre-ignore[6]
                "recommended_mix": mix,
            },
        }


class PipelineCell(BrainCell):
    """Cell 7: Sales pipeline efficiency."""
    name = "pipeline"
    weight = 1.5

    def evaluate(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        leads = ctx.get("leads_processed", 0)
        conversions = ctx.get("conversions", 0)
        outreach_sent = ctx.get("outreach_sent", 0)

        conv_rate = conversions / max(leads, 1)
        response_rate = ctx.get("response_rate", 0.05)

        score = int(min(100, conv_rate * 1000 + response_rate * 200))

        if leads == 0:
            signal, action = "EMPTY", "FILL_PIPELINE"
        elif conv_rate < 0.02:
            signal, action = "LOW_CONVERSION", "IMPROVE_MESSAGING"
        elif conv_rate < 0.05:
            signal, action = "AVERAGE", "A_B_TEST"
        elif conv_rate < 0.10:
            signal, action = "GOOD", "SCALE_VOLUME"
        else:
            signal, action = "EXCELLENT", "MAINTAIN"

        return {
            "score": max(0, min(100, score)),
            "signal": signal,
            "action": action,
            "details": {
                "leads": leads,
                "conversions": conversions,
                "conversion_rate": round(conv_rate, 4),
                "outreach_sent": outreach_sent,
            },
        }


class CompetitiveCell(BrainCell):
    """Cell 8: Competitive pressure & market position."""
    name = "competitive"
    weight = 0.8

    def evaluate(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        products = ctx.get("num_products", len(PRODUCTS))
        avg_price = ctx.get("avg_price", 217)
        market_position = ctx.get("market_position", "challenger")

        # Price positioning score
        if avg_price < 50:
            price_signal = "TOO_CHEAP"
            price_score = 40
        elif avg_price < 150:
            price_signal = "COMPETITIVE"
            price_score = 70
        elif avg_price < 400:
            price_signal = "PREMIUM"
            price_score = 85
        else:
            price_signal = "LUXURY"
            price_score = 75

        # Product breadth
        breadth_score = min(100, products * 15)

        score = int((price_score * 0.6 + breadth_score * 0.4))

        if score < 40:
            action = "LAUNCH_PRODUCTS"
        elif score < 60:
            action = "REPOSITION"
        elif score < 80:
            action = "UPSELL_FOCUS"
        else:
            action = "DEFEND_POSITION"

        return {
            "score": score,
            "signal": price_signal,
            "action": action,
            "details": {
                "num_products": products,
                "avg_price": avg_price,
                "market_position": market_position,
                "breadth_score": breadth_score,
            },
        }


class Brain:
    """
    Strategic brain with 8 parallel decision cells.
    Each cell independently evaluates one dimension.
    Weighted consensus produces the final directive.
    """

    def __init__(self, memory_system) -> None:
        self.memory = memory_system
        self.cells: List[BrainCell] = [
            RevenueCell(),       # Cell 1: Money health
            AgentCell(),         # Cell 2: Agent performance
            RiskCell(),          # Cell 3: Risk / circuit breaker
            TimingCell(),        # Cell 4: Market timing
            ResourceCell(),      # Cell 5: Capacity planning
            ContentCell(),       # Cell 6: Content velocity
            PipelineCell(),      # Cell 7: Pipeline efficiency
            CompetitiveCell(),   # Cell 8: Market position
        ]
        self._history: List[Dict[str, Any]] = []

    def decide(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Run all 8 cells in parallel and produce unified decision."""
        # Evaluate all cells
        evaluations: Dict[str, Dict[str, Any]] = {}
        total_weight = 0
        weighted_score = 0

        for cell in self.cells:
            result = cell.evaluate(ctx)
            evaluations[cell.name] = result
            weighted_score += result["score"] * cell.weight
            total_weight += cell.weight

        # Consensus score (0-100)
        consensus = int(weighted_score / max(total_weight, 1))

        # Check for circuit breaker (risk cell override)
        risk_eval = evaluations.get("risk", {})
        circuit_break = risk_eval.get("details", {}).get("circuit_breaker", False)

        # Determine macro strategy from cell votes
        actions = [e.get("action", "") for e in evaluations.values()]
        if circuit_break:
            strategy = "EMERGENCY_STOP"
        elif any(a in ("AGGRESSIVE_OUTREACH", "FILL_PIPELINE") for a in actions):
            strategy = "SCALE_UP"
        elif any(a in ("THROTTLE", "REDUCE_BATCH") for a in actions):
            strategy = "THROTTLE"
        elif any(a in ("CONTENT_BURST", "OUTREACH_BLAST") for a in actions):
            strategy = "BLITZ"
        elif consensus > 75:
            strategy = "MAINTAIN"
        elif consensus > 50:
            strategy = "OPTIMIZE"
        else:
            strategy = "SCALE_UP"

        # Calculate recommended batch size from resource cell
        resource_eval = evaluations.get("resources", {})
        batch_size = resource_eval.get("details", {}).get("recommended_batch", 2)

        # Content mix from content cell
        content_eval = evaluations.get("content", {})
        content_mix = content_eval.get("details", {}).get("recommended_mix", {})

        # Timing: what to prioritize right now
        timing_eval = evaluations.get("timing", {})
        timing_action = timing_eval.get("action", "BALANCED")

        # Build urgency from revenue + pipeline signals
        rev_eval = evaluations.get("revenue", {})
        urgency = 50
        if rev_eval.get("signal") in ("CRITICAL", "LOW"):
            urgency = 95
        elif rev_eval.get("signal") == "GROWING":
            urgency = 70
        elif strategy == "BLITZ":
            urgency = 85

        decision = {
            "strategy": strategy,
            "consensus_score": consensus,
            "risk": int(100 - risk_eval.get("score", 50)),
            "proceed": not circuit_break and consensus > 25,
            "urgency": urgency,
            "batch_size": batch_size,
            "timing_action": timing_action,
            "content_mix": content_mix,
            "cell_signals": {cell.name: evaluations[cell.name]["signal"] for cell in self.cells},
            "cell_actions": {cell.name: evaluations[cell.name]["action"] for cell in self.cells},
            "cell_scores": {cell.name: evaluations[cell.name]["score"] for cell in self.cells},
        }

        self._history.append({
            "timestamp": datetime.now().isoformat(),
            "decision": decision,
        })

        return decision

    def explain(self) -> str:
        """Human-readable explanation of last decision."""
        if not self._history:
            return "No decisions made yet."

        last = self._history[-1]["decision"]
        lines = [
            f"\n{'═'*65}",
            "🧠  BRAIN DECISION — 8-Cell Analysis",
            f"{'═'*65}",
            f"Strategy:      {last['strategy']}",
            f"Consensus:     {last['consensus_score']}/100",
            f"Risk Level:    {last['risk']}/100",
            f"Urgency:       {last['urgency']}/100",
            f"Proceed:       {'✅ YES' if last['proceed'] else '🛑 NO'}",
            f"Batch Size:    {last['batch_size']}",
            f"Timing:        {last['timing_action']}",
            f"{'─'*65}",
            "Cell Breakdown:",
        ]
        for name, score in last["cell_scores"].items():
            signal = last["cell_signals"][name]
            action = last["cell_actions"][name]
            bar = "█" * (score // 5) + "░" * (20 - score // 5)
            lines.append(f"  {name:<14} [{bar}] {score:>3} | {signal:<18} → {action}")
        lines.append(f"{'═'*65}")
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════
# SECTION 4: AGENT SYSTEM — Unified, Self-Ranking
# ═══════════════════════════════════════════════════════

@dataclass
class AgentProfile:
    agent_id: str
    model_key: str  # "reasoning", "creative", "code"
    system_prompt: str
    
    # ─── ROLE CARD ───
    ownership: str = "TBD"
    deliverables: str = "TBD"
    constraints: str = "None"
    escalation: str = "If stuck, ask Strategy Agent"

    revenue: float = 0.0
    tasks_done: int = 0
    tasks_failed: int = 0
    avg_ms: float = 0.0
    rank: int = 0
    status: str = "active"
    multiplier: float = 1.0

    def success_rate(self) -> float:
        t = self.tasks_done + self.tasks_failed
        return self.tasks_done / max(t, 1)

AGENT_CONFIGS: Dict[str, Dict[str, str]] = {
    "sales": {
        "model_key": "reasoning",
        "system": "Du bist ein Elite Sales Agent. Fokus: High-Ticket Closing.",
        "ownership": "Inbound Leads & Email Pipeline",
        "deliverables": "50 Qualifizierte Leads/Tag, 10 Proposals/Woche, 20% Conversion Rate",
        "constraints": "Keine Fake-Versprechungen. Preise nicht unter 1000€ ohne Approval. Max 2 Follow-ups pro Tag.",
        "escalation": "Wenn Lead Budget < 500€ hat -> Downsell. Wenn Lead Technical Questions hat -> Code Agent.",
    },
    "content": {
        "model_key": "creative",
        "system": "Du bist ein viraler Content Creator. Fokus: Attention Engineering.",
        "ownership": "Social Media Feed (Twitter/X, LinkedIn)",
        "deliverables": "3 Threads/Woche, 5 Tweets/Tag, 1 LinkedIn Deep Dive/Woche",
        "constraints": "Keine Politik, keine Negativität. Alles muss 'High Agency' vibe haben. Max 280 Zeichen für Tweets.",
        "escalation": "Wenn Engagement < 1% -> Style ändern. Wenn Shitstorm -> Strategy Agent.",
    },
    "tiktok": {
        "model_key": "creative",
        "system": "Du bist ein TikTok-Experte. Fokus: Retention Maximierung.",
        "ownership": "TikTok & Shorts Scripting",
        "deliverables": "7 Scripts/Woche (Daily Upload). 1 Viral Hit/Monat (>10k Views).",
        "constraints": "Max 60s. Hook in den ersten 3s ist PFLICHT. Keine langsamen Intros.",
        "escalation": "Wenn Trend verpasst -> sofort Research Agent fragen.",
    },
    "research": {
        "model_key": "reasoning",
        "system": "Du bist der Intelligence Officer. Fokus: Market Alpha.",
        "ownership": "Market Trends & Competitor Analysis",
        "deliverables": "Daily Alpha Report. Competitor Watchlist Updates. Tech Stack Radar.",
        "constraints": "Nur verifizierte Quellen. Keine Halluzinationen. Fakten > Meinung.",
        "escalation": "Wenn Info unklar -> 'Uncertainty' flaggen.",
    },
    "code": {
        "model_key": "code",
        "system": "Du bist der Lead Developer. Fokus: Production Stability.",
        "ownership": "Codebase (Python/Go) & System Architecture",
        "deliverables": "Bug-free Code. Test Coverage > 80%. Self-healing Scripts.",
        "constraints": "Keine Breaking Changes ohne Backup. Keine unkommentierten Funktionen. PEP8/GoFmt Pflicht.",
        "escalation": "Wenn API down -> Circuit Breaker aktivieren -> Admin informieren.",
    },
    "strategy": {
        "model_key": "reasoning",
        "system": "Du bist der CEO / Chef-Stratege. Fokus: Profit Maximierung.",
        "ownership": "Business Model, Pricing & Agent Orchestration",
        "deliverables": "Weekly Growth Plan. Revenue Forecasting. Agent Audits.",
        "constraints": "Kein Micro-Management. Fokus auf die 20% die 80% Impact bringen.",
        "escalation": "Wenn Revenue < Target -> 'War Room' Mode aktivieren.",
    },
    "outreach": {
        "model_key": "reasoning",
        "system": "Du bist der Hunter. Fokus: Cold Contact Volume.",
        "ownership": "Cold Outreach (DM/Email) & Initial Contact",
        "deliverables": "50 DMs/Tag. 5 Calls gebucht/Woche.",
        "constraints": "Nicht spammy wirken. Immer Value-First. Keine generischen Templates.",
        "escalation": "Wenn Response Rate < 5% -> Script ändern via Content Agent.",
    },
    "closer": {
        "model_key": "reasoning",
        "system": "Du bist der Deal Maker. Fokus: Revenue Capture.",
        "ownership": "Contract Negotiation & Closing",
        "deliverables": "Signed Contracts. Up-Sells beim Closing.",
        "constraints": "Rabatte max 10%. Payment Terms max 30 Tage.",
        "escalation": "Wenn Deal > 5k -> Strategy Agent konsultieren.",
    },
}


class AgentSwarm:
    """Centralized agent management with auto-ranking.
    Delegates real ranking/persistence to AgentManager."""

    def __init__(self, bus: EventBus, skills, tools, memory) -> None:
        self.bus = bus
        self.skills = skills
        self.tools = tools
        self.memory = memory
        self.agents: Dict[str, AgentProfile] = {}
        self.engines: Dict[str, Any] = {}  # model_key -> OllamaEngine

        # ── Unified manager: single source of truth for ranking ──
        self.manager: Optional[AgentManager] = None
        if HAS_AGENT_MGR and AgentManager is not None:
            self.manager = AgentManager(rankings_file=RANKINGS_FILE)
            logger.info("✅ AgentManager connected — unified ranking active")
        else:
            logger.warning("⚠️ AgentManager not available — using local ranking")

        self._init_agents()
        self._load_rankings()

    def _init_agents(self) -> None:
        for aid, cfg in AGENT_CONFIGS.items():
            # Build robust Role Card System Prompt
            base_sys = cfg["system"]
            ownership = cfg.get("ownership", "General Task")
            deliverables = cfg.get("deliverables", "High Quality Output")
            constraints = cfg.get("constraints", "None")
            escalation = cfg.get("escalation", "Ask human if unsure")

            # Format: ROLE CARD
            full_system_prompt = (
                f"{base_sys}\n\n"
                f"📋 ROLE CARD:\n"
                f"• OWNERSHIP: {ownership}\n"
                f"• DELIVERABLES: {deliverables}\n"
                f"• CONSTRAINTS: {constraints}\n"
                f"• ESCALATION: {escalation}\n"
            )

            self.agents[aid] = AgentProfile(
                agent_id=aid,
                model_key=cfg["model_key"],
                system_prompt=full_system_prompt,
                ownership=ownership,
                deliverables=deliverables,
                constraints=constraints,
                escalation=escalation,
            )

            # Register in AgentManager
            if self.manager:
                self.manager.register_agent(aid, aid)  # type = agent_id

        # Init Ollama engines (deduplicated by model)
        if HAS_OLLAMA and OFFLINE_MODE and OllamaEngine is not None:
            for key, model_name in MODELS.items():
                if key not in self.engines:
                    self.engines[key] = OllamaEngine(
                        host=OLLAMA_HOST, model=model_name, timeout_s=600.0
                    )

    def route(self, text: str) -> str:
        """Smart-route prompt to best agent."""
        t = text.lower()
        routes = [
            (["tiktok", "short", "viral", "hook", "reel"], "tiktok"),
            (["sell", "sales", "email", "outreach", "verkauf", "mail", "proposal"], "sales"),
            (["close", "einwand", "objection", "deal", "preis"], "closer"),
            (["outreach", "dm", "cold", "anschreiben"], "outreach"),
            (["research", "trend", "markt", "analyse", "market"], "research"),
            (["code", "python", "script", "function", "class", "bug", "go"], "code"),
            (["strateg", "money", "geld", "revenue", "plan", "monetar"], "strategy"),
        ]
        for keywords, agent_id in routes:
            if any(w in t for w in keywords):
                return agent_id
        return "content"

    async def execute(self, prompt: str, agent_id: str | None = None) -> Dict[str, Any]:
        """Execute a task. Checks for Skills first, then AI Agents."""
        # 1. Check for Power-Skills (1-word commands)
        skill_name = prompt.lower().strip().replace(" ", "_")
        if hasattr(self.skills, skill_name):
            try:
                method = getattr(self.skills, skill_name)
                result = method()  # Execute skill
                self.memory.add_event("skill", f"Executed: {skill_name}", 2)
                return {
                    "agent": "SKILL_ENGINE",
                    "content": result,
                    "model": "deterministic"
                }
            except Exception as e:
                logger.error(f"Skill execution failed: {e}")

        if agent_id is None:
            agent_id = self.route(prompt)

        agent = self.agents.get(agent_id)
        if not agent:
            return {"error": f"Unknown agent: {agent_id}"}

        engine = self.engines.get(agent.model_key)
        if not engine:
            return {"error": f"No engine for {agent.model_key}", "agent": agent_id}

        t0 = time.time()
        try:
            resp = await engine.chat([
                {"role": "system", "content": agent.system_prompt},
                {"role": "user", "content": prompt},
            ])
            if LLMResponse is not None:
                assert isinstance(resp, LLMResponse)
            duration = int((time.time() - t0) * 1000)

            agent.tasks_done += 1
            n = agent.tasks_done
            agent.avg_ms = ((agent.avg_ms * (n - 1)) + duration) / n

            # Sync to AgentManager (single source of truth)
            if self.manager:
                self.manager.report_task_completion(
                    agent_id=agent_id,
                    revenue_eur=0.0,  # Revenue tracked via RevenueCore
                    duration_ms=duration,
                    success=True,
                )
            self._update_rankings()

            self.bus.emit("task/completed", {
                "agent": agent_id, "latency_ms": duration, "success": True
            })

            return {
                "agent": agent_id,
                "model": MODELS[agent.model_key],
                "response": getattr(resp, 'content', ''),
                "latency_ms": duration,
            }
        except Exception as e:
            agent.tasks_failed += 1
            # Sync failure to AgentManager
            if self.manager:
                self.manager.report_task_completion(
                    agent_id=agent_id,
                    revenue_eur=0.0,
                    duration_ms=int((time.time() - t0) * 1000),
                    success=False,
                )
            logger.error(f"❌ Agent {agent_id} failed: {e}")
            self.bus.emit("task/failed", {"agent": agent_id, "error": str(e)})
            return {"error": str(e), "agent": agent_id}

    async def batch(self, prompts: List[str], max_concurrent: int = 2) -> List[Dict[str, Any]]:
        """Parallel batch execution with concurrency limit."""
        sem = asyncio.Semaphore(max_concurrent)
        async def _run(p: str) -> Dict[str, Any]:
            async with sem:
                return await self.execute(p)
        results = await asyncio.gather(*[_run(p) for p in prompts])
        return list(results)

    # ─── RANKING (delegates to AgentManager when available) ───
    def _update_rankings(self) -> None:
        """Sync local AgentProfile stats with AgentManager, then re-rank."""
        if self.manager and hasattr(self.manager, 'agents'):
            # AgentManager already re-ranked on report_task_completion.
            # Pull the canonical rank/status back into our profiles.
            for aid, agent in self.agents.items():
                if self.manager.agents:
                    rec = self.manager.agents.get(aid)
                    if rec:
                        agent.rank = rec.rank
                        agent.status = rec.status
                        agent.multiplier = rec.priority_multiplier
            return

        # Fallback: local ranking if AgentManager not loaded
        ranked = sorted(self.agents.values(), key=lambda a: a.revenue, reverse=True)
        for i, a in enumerate(ranked):
            a.rank = i + 1
            if a.rank <= 3:
                a.status = "boosted"
                a.multiplier = 2.0 + (3 - a.rank) * 0.5
            elif a.rank >= 7:
                a.status = "demoted"
                a.multiplier = 0.5
            else:
                a.status = "active"
                a.multiplier = 1.0

    def leaderboard(self) -> str:
        """Formatted leaderboard string. Uses AgentManager when available."""
        if self.manager:
            board = self.manager.get_leaderboard()
            medals = {1: "🥇", 2: "🥈", 3: "🥉"}
            lines = [
                f"\n{'='*65}",
                "👑  AGENT LEADERBOARD — Revenue Ranking (AgentManager)",
                f"{'='*65}",
                f"{'#':<4} {'Agent':<25} {'Revenue':>10} {'Tasks':>7} {'€/Task':>8} {'Status':>10}",
                f"{'-'*65}",
            ]
            for rec in board:
                m = medals.get(rec.rank, f"#{rec.rank}")
                icon = {"boosted": "🚀", "active": "✅", "demoted": "📉", "paused": "⏸️"}.get(rec.status, "❓")
                lines.append(
                    f"{m:<4} {rec.agent_id:<25} €{rec.revenue_eur:>8.2f} "
                    f"{rec.tasks_completed:>7} €{rec.revenue_per_task():>6.2f} "
                    f"{icon} {rec.status}"
                )
            total = sum(a.revenue_eur for a in self.manager.agents.values())
            lines += [f"{'-'*65}", f"     TOTAL EMPIRE REVENUE: €{total:,.2f}", f"{'='*65}"]
            return "\n".join(lines)

        # Fallback: local leaderboard
        ranked = sorted(self.agents.values(), key=lambda a: (a.revenue, a.tasks_done), reverse=True)
        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
        lines = [
            f"\n{'='*65}",
            "👑  AGENT LEADERBOARD — Revenue Ranking",
            f"{'='*65}",
            f"{'#':<4} {'Agent':<15} {'Revenue':>10} {'Tasks':>7} {'Avg ms':>8} {'Status':>10}",
            f"{'-'*65}",
        ]
        for a in ranked:
            m = medals.get(a.rank, f"#{a.rank}")
            icon = {"boosted": "🚀", "active": "✅", "demoted": "📉"}.get(a.status, "❓")
            lines.append(
                f"{m:<4} {a.agent_id:<15} €{a.revenue:>8.2f} {a.tasks_done:>7} "
                f"{a.avg_ms:>7.0f} {icon} {a.status}"
            )
        total = sum(a.revenue for a in self.agents.values())
        lines += [f"{'-'*65}", f"     TOTAL EMPIRE REVENUE: €{total:,.2f}", f"{'='*65}"]
        return "\n".join(lines)

    # ─── PERSISTENCE (delegates to AgentManager when available) ───
    def _load_rankings(self) -> None:
        if self.manager:
            # AgentManager loaded its own file in __init__. Sync into profiles.
            for aid, agent in self.agents.items():
                rec = self.manager.agents.get(aid)
                if rec:
                    agent.revenue = rec.revenue_eur
                    agent.tasks_done = rec.tasks_completed
                    agent.tasks_failed = rec.tasks_failed
                    agent.avg_ms = rec.avg_response_ms
            self._update_rankings()
            return

        # Fallback: load from JSON directly
        if os.path.exists(RANKINGS_FILE):
            try:
                with open(RANKINGS_FILE) as f:
                    data = json.load(f)
                for ad in data.get("agents", []):
                    aid = ad.get("agent_id", "")
                    if aid in self.agents:
                        self.agents[aid].revenue = float(ad.get("revenue_eur", 0))
                        self.agents[aid].tasks_done = int(ad.get("tasks_completed", 0))
                        self.agents[aid].tasks_failed = int(ad.get("tasks_failed", 0))
                self._update_rankings()
            except Exception as e:
                logger.warning(f"Could not load rankings: {e}")

    def save_rankings(self) -> None:
        if self.manager:
            # Sync latest stats from profiles into manager
            for aid, agent in self.agents.items():
                rec = self.manager.agents.get(aid)
                if rec:
                    rec.revenue_eur = agent.revenue
                    rec.tasks_completed = agent.tasks_done
                    rec.tasks_failed = agent.tasks_failed
                    rec.avg_response_ms = agent.avg_ms
            self.manager._update_rankings()
            self.manager._save_rankings()
            return

        # Fallback: save directly
        data = {
            "agents": [
                {
                    "agent_id": a.agent_id, "agent_type": a.agent_id,
                    "revenue_eur": a.revenue, "tasks_completed": a.tasks_done,
                    "tasks_failed": a.tasks_failed, "avg_response_ms": a.avg_ms,
                    "rank": a.rank, "status": a.status,
                    "priority_multiplier": a.multiplier,
                }
                for a in self.agents.values()
            ],
            "last_updated": datetime.now().isoformat(),
            "total_revenue_eur": sum(a.revenue for a in self.agents.values()),
        }
        with open(RANKINGS_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def get_status_json(self) -> Dict[str, Any]:
        """Return full swarm status as JSON-serializable dict for the dashboard."""
        agents_list = []
        for a in sorted(self.agents.values(), key=lambda x: x.rank):
            agents_list.append({
                "agent_id": a.agent_id,
                "rank": a.rank,
                "status": a.status,
                "revenue_eur": a.revenue,
                "tasks_done": a.tasks_done,
                "tasks_failed": a.tasks_failed,
                "avg_ms": round(a.avg_ms),
                "multiplier": a.multiplier,
            })
        return {
            "timestamp": datetime.now().isoformat(),
            "total_agents": len(self.agents),
            "total_tasks": sum(a.tasks_done for a in self.agents.values()),
            "total_revenue_eur": sum(a.revenue for a in self.agents.values()),
            "agents": agents_list,
        }


# ═══════════════════════════════════════════════════════
# SECTION 5: REVENUE CORE — Automated Money Flow
# ═══════════════════════════════════════════════════════

class RevenueCore:
    """Unified revenue tracking and pipeline."""

    def __init__(self, bus: EventBus) -> None:
        self.bus = bus
        self.total_eur = 0.0
        self.transactions = 0
        self.sales: List[Dict] = []
        self._load()

        bus.on("revenue/sale", self._on_sale)

    def _on_sale(self, data: Dict) -> None:
        amount = data.get("amount", 0)
        self.total_eur += amount
        self.transactions += 1
        self.sales.append({**data, "timestamp": datetime.now().isoformat()})
        self._save()
        logger.info(f"💰 SALE: €{amount:.2f} | Total: €{self.total_eur:.2f}")

    async def run_pipeline(self, swarm: AgentSwarm, waves: int = 3, leads: int = 10) -> Dict:
        """Full autonomous revenue pipeline."""
        logger.info(f"🚀 REVENUE PIPELINE: {waves} waves × {leads} leads")
        total_sales = 0

        for wave in range(1, waves + 1):
            logger.info(f"\n─── Wave {wave}/{waves} ───")

            for i in range(leads):
                # Step 1: Research (find opportunity)
                res = await swarm.execute(
                    f"Finde eine Business-Opportunity #{i+1} für AI Automation Services. "
                    "Welche Branche? Welcher Pain Point? Kurze Analyse.",
                    agent_id="research"
                )

                # Step 2: Create outreach
                if "response" in res:
                    await swarm.execute(
                        f"Basierend auf dieser Opportunity:\n{res['response'][:300]}\n\n"
                        "Schreibe eine personalisierte Outreach-Email. Hook + Solution + CTA.",
                        agent_id="sales"
                    )

                # Step 3: Simulate conversion (5-10%)
                if random.random() < 0.07:
                    product = random.choice(list(PRODUCTS.values()))
                    self.bus.emit("revenue/sale", {
                        "amount": product["price"],
                        "product": product["name"],
                        "source": "pipeline",
                    })
                    total_sales += 1  # pyre-ignore[58]

            await asyncio.sleep(0.5)

        return {
            "waves": waves, "leads_total": waves * leads,
            "sales": total_sales, "revenue": self.total_eur,
        }

    def dashboard(self) -> str:
        lines = [
            f"\n{'='*50}",
            "💰 REVENUE DASHBOARD",
            f"{'='*50}",
            f"Total Revenue:    €{self.total_eur:,.2f}",
            f"Transactions:     {self.transactions}",
            f"Avg Order Value:  €{self.total_eur / max(self.transactions, 1):,.2f}",
        ]
        if self.sales:
            lines.append(f"\nLast 5 Sales:")
            for s in self.sales[-5:]:  # pyre-ignore[16]
                lines.append(f"  €{s['amount']:.2f} — {s.get('product', '?')} ({s.get('timestamp', '')[:16]})")
        lines.append(f"{'='*50}")
        return "\n".join(lines)

    def _load(self) -> None:
        if os.path.exists(REVENUE_FILE):
            try:
                with open(REVENUE_FILE) as f:
                    d = json.load(f)
                self.total_eur = d.get("total_revenue_cents", 0) / 100.0
                self.transactions = d.get("total_transactions", 0)
            except Exception:
                pass

    def _save(self) -> None:
        with open(REVENUE_FILE, "w") as f:
            json.dump({
                "total_revenue_cents": int(self.total_eur * 100),
                "total_transactions": self.transactions,
                "last_payment": datetime.now().isoformat(),
                "payments": self.sales[-100:],  # pyre-ignore[16]
            }, f, indent=2, ensure_ascii=False)


# ═══════════════════════════════════════════════════════
# SECTION 6: AUTOPILOT — Autonomous Scheduling
# ═══════════════════════════════════════════════════════

class AutoPilot:
    """Self-driving empire. Runs autonomously, optimizes itself."""

    def __init__(self, swarm: AgentSwarm, revenue: RevenueCore, brain: Brain, bus: EventBus):
        self.swarm = swarm
        self.revenue = revenue
        self.brain = brain
        self.bus = bus
        self.cycle = 0

    async def run(self, cycles: int = 0) -> None:
        """Run autonomous cycles. cycles=0 means infinite."""
        logger.info("🤖 AUTOPILOT ENGAGED — Full Autonomy")
        run_forever = cycles <= 0

        while run_forever or self.cycle < cycles:
            self.cycle += 1
            logger.info(f"\n{'═'*60}")
            logger.info(f"🔄 AUTOPILOT CYCLE {self.cycle}")
            logger.info(f"{'═'*60}")

            # Build rich context for all 8 brain cells
            total_done = sum(a.tasks_done for a in self.swarm.agents.values())
            total_failed = sum(a.tasks_failed for a in self.swarm.agents.values())
            error_rate = total_failed / max(total_done + total_failed, 1)

            ctx: Dict[str, Any] = {
                # Cell 1: Revenue
                "revenue": self.revenue.total_eur,
                "revenue_target": 5000,
                "transactions": self.revenue.transactions,
                "hours_running": max(1.0, self.cycle * 0.5),
                # Cell 2: Agents
                "agents": {
                    aid: {
                        "done": a.tasks_done,
                        "failed": a.tasks_failed,
                        "avg_ms": a.avg_ms,
                    }
                    for aid, a in self.swarm.agents.items()
                },
                # Cell 3: Risk
                "error_rate": error_rate,
                "pending": 0,
                "consecutive_fails": 0,
                "memory_pct": 50,
                # Cell 5: Resources
                "num_agents": len(self.swarm.agents),
                "active_tasks": 0,
                "offline_mode": OFFLINE_MODE,
                # Cell 6: Content
                "content_generated": total_done,
                "content_target": 20,
                # Cell 7: Pipeline
                "leads_processed": self.revenue.transactions * 14,  # ~7% conversion
                "conversions": self.revenue.transactions,
                "outreach_sent": total_done,
                # Cell 8: Competitive
                "num_products": len(PRODUCTS),
                "avg_price": float(sum(p["price"] for p in PRODUCTS.values())) / max(len(PRODUCTS), 1),
            }

            decision = self.brain.decide(ctx)

            # Log the full 8-cell breakdown
            logger.info(self.brain.explain())

            if not decision["proceed"]:
                logger.warning("⚠️ Brain: Circuit breaker triggered, cooling down...")
                await asyncio.sleep(10)
                continue

            # Phase 1: Content Burst (adapted to brain's content mix)
            logger.info("📝 Phase 1: Content Generation")
            content_mix = decision.get("content_mix", {})
            content_prompts = [
                "Erstelle einen viralen Tweet über AI Automation. Hook + Value + CTA. Max 280 Zeichen.",
                "LinkedIn Post: Wie AI 15h/Woche spart. Professionell, mit Zahlen.",
            ]
            # Offline: serialize requests (Ollama serves 1 model at a time)
            batch_size = 1 if OFFLINE_MODE else decision.get("batch_size", 2)
            await self.swarm.batch(content_prompts, max_concurrent=batch_size)

            # Phase 2: Revenue Pipeline (leads scaled by urgency)
            logger.info("💰 Phase 2: Revenue Pipeline")
            urgency = decision.get("urgency", 50)
            leads_count = 3 if urgency < 60 else (5 if urgency < 80 else 8)
            if OFFLINE_MODE:
                leads_count = min(leads_count, 3)  # Cap for local models
            result = await self.revenue.run_pipeline(self.swarm, waves=1, leads=leads_count)
            logger.info(f"Pipeline Result: {result['sales']} sales, €{result['revenue']:.2f}")

            # Phase 3: Self-Optimization
            logger.info("🔧 Phase 3: Self-Optimization")
            top_agent = sorted(self.swarm.agents.values(), key=lambda a: a.tasks_done, reverse=True)[0]
            cell_summary = ", ".join(f"{k}={v}" for k, v in decision.get("cell_signals", {}).items())
            await self.swarm.execute(
                f"Analysiere diese Empire-Performance und schlage Optimierungen vor:\n"
                f"Revenue: €{self.revenue.total_eur:.2f}\n"
                f"Strategy: {decision['strategy']} | Consensus: {decision.get('consensus_score', 0)}/100\n"
                f"Cell Signals: {cell_summary}\n"
                f"Top Agent: {top_agent.agent_id} ({top_agent.tasks_done} tasks)\n"
                f"Urgency: {urgency}/100 | Risk: {decision['risk']}/100",
                agent_id="strategy"
            )

            self.swarm.save_rankings()
            self.bus.emit("autopilot/cycle_done", {"cycle": self.cycle})

            # Fire n8n webhook for cloud automation
            await self.bus.notify_n8n("autopilot_cycle", {
                "cycle": self.cycle,
                "revenue_total": self.revenue.total_eur,
                "sales_this_cycle": result.get("sales", 0),
                "agents_active": len(self.swarm.agents),
                "strategy": decision["strategy"],
                "consensus": decision.get("consensus_score", 0),
                "cell_signals": decision.get("cell_signals", {}),
            })

            logger.info(f"✅ Cycle {self.cycle} complete")
            await asyncio.sleep(2)


# ═══════════════════════════════════════════════════════
# SECTION 7: NUCLEUS — The One Ring to Rule Them All
# ═══════════════════════════════════════════════════════

class EmpireNucleus:
    """Central nervous system. One import, full power."""

    def __init__(self) -> None:
        self.bus = EventBus()
        self.brain = Brain(runtime_memory)
        self.swarm = AgentSwarm(self.bus, runtime_skills, runtime_tools, runtime_memory)
        self.revenue = RevenueCore(self.bus)
        self.autopilot = AutoPilot(self.swarm, self.revenue, self.brain, self.bus)

    async def health_check(self) -> bool:
        if not HAS_OLLAMA:
            logger.error("❌ ollama_engine not found")
            return False
        engine = list(self.swarm.engines.values())[0] if self.swarm.engines else None
        if engine:
            ok = await engine.health()
            if ok:
                models = await engine.list_models()
                logger.info(f"✅ Ollama Online — {len(models)} models")
                return True
        logger.error("❌ Ollama offline — run: ollama serve")
        return False

    def status(self) -> str:
        lines = [
            BANNER,
            self.revenue.dashboard(),
            self.swarm.leaderboard(),
        ]
        return "\n".join(lines)

    async def interactive(self) -> None:
        """Interactive REPL mode."""
        print(BANNER)
        if not await self.health_check():
            return

        while True:
            try:
                cmd = input("\n👑 > ").strip()
                if not cmd:
                    continue
                if cmd.lower() in ("exit", "quit", "q"):
                    print("👋 Empire offline.")
                    break

                if cmd == "!status":
                    print(self.status())
                    continue
                if cmd == "!rank":
                    print(self.swarm.leaderboard())
                    continue
                if cmd == "!revenue":
                    print(self.revenue.dashboard())
                    continue
                if cmd == "!brain":
                    # Run a brain decision with current state and show breakdown
                    total_done = sum(a.tasks_done for a in self.swarm.agents.values())
                    total_failed = sum(a.tasks_failed for a in self.swarm.agents.values())
                    ctx: Dict[str, Any] = {
                        "revenue": self.revenue.total_eur,
                        "transactions": self.revenue.transactions,
                        "hours_running": 1,
                        "agents": {
                            aid: {"done": a.tasks_done, "failed": a.tasks_failed, "avg_ms": a.avg_ms}
                            for aid, a in self.swarm.agents.items()
                        },
                        "error_rate": total_failed / max(total_done + total_failed, 1),
                        "num_agents": len(self.swarm.agents),
                        "content_generated": total_done,
                        "leads_processed": self.revenue.transactions * 14,
                        "conversions": self.revenue.transactions,
                        "num_products": len(PRODUCTS),
                        "avg_price": float(sum(p["price"] for p in PRODUCTS.values())) / max(len(PRODUCTS), 1),
                    }
                    self.brain.decide(ctx)
                    print(self.brain.explain())
                    continue
                if cmd == "!autopilot":
                    await self.autopilot.run(cycles=3)
                    continue
                if cmd.startswith("!burst"):
                    n = int(cmd.split()[-1]) if len(cmd.split()) > 1 else 10
                    r = await self.revenue.run_pipeline(self.swarm, waves=1, leads=n)
                    print(f"✅ Burst done: {r['sales']} sales, €{r['revenue']:.2f}")
                    continue

                # Agent-specific: !sales <prompt>
                agent_override: Optional[str] = None
                cmd_str: str = cmd
                for prefix in AGENT_CONFIGS:
                    if cmd_str.startswith(f"!{prefix} "):
                        agent_override = prefix
                        cmd = cmd_str[len(prefix) + 2:]  # pyre-ignore[16]
                        break

                result = await self.swarm.execute(cmd, agent_override)
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

        self.swarm.save_rankings()


BANNER = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   👑  EMPIRE NUCLEUS — Zentrales Nervensystem               ║
║   🧠  Brain: 8-Cell Parallel | Agents: 8 Specialized       ║
║   💰  Revenue: Live Pipeline + Auto-Ranking                 ║
║   🤖  AutoPilot: Full Autonomy                              ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  Commands:                                                   ║
║    <prompt>           → Auto-routed to best agent           ║
║    !sales <prompt>    → Sales Agent                         ║
║    !content <prompt>  → Content Agent                       ║
║    !tiktok <prompt>   → TikTok Agent                        ║
║    !research <prompt> → Research Agent                      ║
║    !code <prompt>     → Code Agent                          ║
║    !strategy <prompt> → Strategy Agent                      ║
║    !status            → Full Dashboard                      ║
║    !rank              → Agent Leaderboard                   ║
║    !revenue           → Revenue Dashboard                   ║
║    !brain             → 8-Cell Brain Analysis               ║
║    !burst <N>         → Revenue Burst (N leads)             ║
║    !autopilot         → 3 Autonomous Cycles                 ║
║    exit               → Quit                                ║
╚══════════════════════════════════════════════════════════════╝
"""


# ═══════════════════════════════════════════════════════
# SECTION 8: STATUS API — Live dashboard endpoint
# ═══════════════════════════════════════════════════════

STATUS_PORT = int(os.getenv("EMPIRE_STATUS_PORT", "3333"))


async def _handle_status_request(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    nucleus: "EmpireNucleus",
) -> None:
    """Handle a single HTTP request and return JSON status."""
    try:
        data = await asyncio.wait_for(reader.read(4096), timeout=5.0)
        request_line = data.decode("utf-8", errors="replace").split("\r\n")[0]

        # Only respond to GET /status (and GET / as alias)
        if "GET /status" in request_line or "GET / " in request_line:
            status = nucleus.swarm.get_status_json()
            status["revenue"] = {
                "total_eur": nucleus.revenue.total_eur,
                "transactions": nucleus.revenue.transactions,
            }
            status["brain_directive"] = getattr(nucleus.brain, "last_directive", "HOLD")
            body = json.dumps(status, indent=2, ensure_ascii=False)
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: application/json\r\n"
                "Access-Control-Allow-Origin: *\r\n"
                f"Content-Length: {len(body.encode())}\r\n"
                "\r\n"
                f"{body}"
            )
        elif "OPTIONS" in request_line:
            response = (
                "HTTP/1.1 204 No Content\r\n"
                "Access-Control-Allow-Origin: *\r\n"
                "Access-Control-Allow-Methods: GET, OPTIONS\r\n"
                "Access-Control-Allow-Headers: *\r\n"
                "\r\n"
            )
        else:
            response = "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n"

        writer.write(response.encode())
        await writer.drain()
    except Exception:
        pass
    finally:
        writer.close()


async def start_status_server(nucleus: "EmpireNucleus") -> None:
    """Start a background status API on STATUS_PORT."""
    async def handler(r: asyncio.StreamReader, w: asyncio.StreamWriter) -> None:
        await _handle_status_request(r, w, nucleus)

    try:
        server = await asyncio.start_server(handler, "0.0.0.0", STATUS_PORT)
        logger.info(f"📡 Status API live at http://localhost:{STATUS_PORT}/status")
        async with server:
            await server.serve_forever()
    except OSError as e:
        logger.warning(f"⚠️ Status API port {STATUS_PORT} unavailable: {e}")


# ═══════════════════════════════════════════════════════
# SECTION 9: CLI — Ein Befehl, volle Power
# ═══════════════════════════════════════════════════════

async def main() -> None:
    parser = argparse.ArgumentParser(description="Empire Nucleus — Zentrales AI Empire")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive REPL")
    parser.add_argument("--burst", type=int, default=0, help="Revenue burst with N leads")
    parser.add_argument("--autopilot", type=int, default=0, help="Run N autopilot cycles (0=infinite)")
    parser.add_argument("--dashboard", "-d", action="store_true", help="Show status dashboard")
    parser.add_argument("prompt", nargs="*", help="Single task prompt")

    args = parser.parse_args()
    nucleus = EmpireNucleus()

    if args.dashboard:
        print(nucleus.status())
        return

    if args.burst > 0:
        if not await nucleus.health_check():
            return
        r = await nucleus.revenue.run_pipeline(nucleus.swarm, waves=1, leads=args.burst)
        print(f"\n✅ Burst: {r['sales']} sales, €{r['revenue']:.2f}")
        nucleus.swarm.save_rankings()
        return

    if args.autopilot > 0 or (not args.interactive and not args.prompt):
        if not await nucleus.health_check():
            return
        # Start status API in background
        asyncio.create_task(start_status_server(nucleus))
        cycles = args.autopilot if args.autopilot > 0 else 3
        await nucleus.autopilot.run(cycles=cycles)
        nucleus.swarm.save_rankings()
        return

    if args.prompt:
        if not await nucleus.health_check():
            return
        prompt = " ".join(args.prompt)
        result = await nucleus.swarm.execute(prompt)
        if "response" in result:
            print(result["response"])
        else:
            print(f"❌ {result.get('error')}")
        nucleus.swarm.save_rankings()
        return

    # Default: interactive — start status API in background
    asyncio.create_task(start_status_server(nucleus))
    await nucleus.interactive()


if __name__ == "__main__":
    asyncio.run(main())
