#!/usr/bin/env python3
"""
👑 POWER LAUNCHER – Ein Befehl, volle Power.

Startet alle lokalen AI Agents mit Ollama (kostenlos, offline).
Kein Docker, kein Redis, kein Cloud API nötig.

Usage:
    python power_launcher.py                     # Interactive Mode
    python power_launcher.py "Create TikTok"     # Single Task Mode
"""
from __future__ import annotations

import asyncio
import json
import sys
import time
import logging
from typing import Any, Dict

from ollama_engine import OllamaEngine, LLMResponse
from agent_manager import AgentManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("PowerLauncher")

# ─── MODEL CONFIG ───────────────────────────────────
MODELS = {
    "reasoning": "deepseek-r1:8b",
    "creative":  "glm-4.7-flash",
    "code":      "qwen2.5-coder:7b",
}

# ─── AGENT DEFINITIONS (simplified, no Redis needed) ─
AGENTS: Dict[str, Dict[str, str]] = {
    "content": {
        "model": MODELS["creative"],
        "system": (
            "Du bist ein Elite Content Creator. Erstelle virale Scripts "
            "für TikTok/YouTube Shorts/X Posts. Hook + Body + CTA. Deutsch."
        ),
    },
    "sales": {
        "model": MODELS["reasoning"],
        "system": (
            "Du bist ein Top Sales Agent. Schreibe überzeugende Verkaufs-Emails "
            "und Outreach Messages für AI Automation Services. Kurz, freundlich, klarer CTA."
        ),
    },
    "research": {
        "model": MODELS["reasoning"],
        "system": (
            "Du bist ein Research Agent. Analysiere Trends, Märkte, Technologien. "
            "Gib strukturierte, faktenbasierte Antworten mit Opportunities."
        ),
    },
    "tiktok": {
        "model": MODELS["creative"],
        "system": (
            "Du bist ein viraler TikTok Experte. Max 60 Sekunden Sprechtext. "
            "Hook + Script + CTA für maximale Views. Kurz, punchy, emotional."
        ),
    },
    "code": {
        "model": MODELS["code"],
        "system": (
            "You are an expert Python/Go developer. Write clean, production-ready code. "
            "Include error handling and type hints."
        ),
    },
    "strategy": {
        "model": MODELS["reasoning"],
        "system": (
            "Du bist ein Business-Stratege. Analysiere Monetarisierungs-Möglichkeiten, "
            "erstelle Action Plans, und identifiziere den schnellsten Weg zu Revenue."
        ),
    },
}


class PowerLauncher:
    """Unified launcher – routes commands to agents, tracks revenue."""

    def __init__(self) -> None:
        self.engines: Dict[str, OllamaEngine] = {}
        self.manager = AgentManager()
        # Register all agents
        for agent_id, cfg in AGENTS.items():
            self.manager.register_agent(agent_id, agent_id)
            if cfg["model"] not in self.engines:
                self.engines[cfg["model"]] = OllamaEngine(model=cfg["model"])

    def _route(self, text: str) -> str:
        """Smart routing based on keywords."""
        t = text.lower()
        if any(w in t for w in ["tiktok", "short", "viral", "hook"]):
            return "tiktok"
        if any(w in t for w in ["sell", "sales", "email", "outreach", "verkauf", "mail"]):
            return "sales"
        if any(w in t for w in ["research", "trend", "markt", "analyse", "market"]):
            return "research"
        if any(w in t for w in ["code", "python", "script", "function", "class", "bug"]):
            return "code"
        if any(w in t for w in ["strateg", "money", "geld", "revenue", "plan", "monetar"]):
            return "strategy"
        return "content"  # Default: content creation

    async def execute(self, prompt: str, agent_type: str | None = None) -> Dict[str, Any]:
        """Execute a task with the right agent."""
        if agent_type is None:
            agent_type = self._route(prompt)

        cfg = AGENTS[agent_type]
        engine = self.engines[cfg["model"]]

        print(f"\n🤖 Agent: {agent_type.upper()} | Model: {cfg['model']}")
        print(f"📝 Prompt: {prompt}")
        print("⏳ Generating...\n")

        t0 = time.time()
        resp = await engine.chat([
            {"role": "system", "content": cfg["system"]},
            {"role": "user", "content": prompt},
        ])
        assert isinstance(resp, LLMResponse)
        duration = int((time.time() - t0) * 1000)

        # Track in agent manager
        self.manager.report_task_completion(
            agent_id=agent_type,
            revenue_eur=0.0,  # User tracks real revenue manually
            duration_ms=float(duration),
            success=bool(resp.content),
        )

        return {
            "agent": agent_type,
            "model": resp.model,
            "response": resp.content,
            "latency_ms": duration,
            "cost": "$0.00",
        }

    async def batch(self, prompts: list[str], max_concurrent: int = 2) -> list[Dict[str, Any]]:
        """Execute multiple prompts in parallel with concurrency limit."""
        sem = asyncio.Semaphore(max_concurrent)

        async def _run(p: str):
            async with sem:
                return await self.execute(p)

        tasks = [_run(p) for p in prompts]
        return await asyncio.gather(*tasks)


BANNER = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   👑  POWER LAUNCHER – MAURICE'S AI EMPIRE                  ║
║   🧠  3 Models: DeepSeek-R1 + GLM-4.7 + Qwen2.5-Coder     ║
║   💰  Cost: $0.00 (Forever Free, Offline)                   ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  Commands:                                                   ║
║    Just type anything → auto-routed to best agent           ║
║    !content <prompt>  → Content Agent                       ║
║    !sales <prompt>    → Sales Agent                         ║
║    !research <prompt> → Research Agent                      ║
║    !tiktok <prompt>   → TikTok Agent                        ║
║    !code <prompt>     → Code Agent                          ║
║    !strategy <prompt> → Strategy Agent                      ║
║    !rank              → Show Agent Leaderboard              ║
║    !batch             → Batch mode (multiple prompts)       ║
║    exit               → Quit                                ║
╚══════════════════════════════════════════════════════════════╝
"""


async def interactive(launcher: PowerLauncher) -> None:
    """Interactive REPL mode."""
    print(BANNER)

    # Health check
    engine = list(launcher.engines.values())[0]
    ok = await engine.health()
    if ok:
        models = await engine.list_models()
        print(f"✅ Ollama Online – {len(models)} Models loaded: {', '.join(models[:5])}")
    else:
        print("❌ Ollama nicht erreichbar! Starte: ollama serve")
        return

    print()

    while True:
        try:
            cmd = input("👑 > ").strip()

            if not cmd:
                continue
            if cmd.lower() in ("exit", "quit", "q"):
                print("👋 Empire shutting down.")
                break

            # Special commands
            if cmd == "!rank":
                launcher.manager.print_leaderboard()
                continue

            if cmd.startswith("!batch"):
                print("Enter prompts (one per line, empty line to execute):")
                prompts = []
                while True:
                    line = input("  > ").strip()
                    if not line:
                        break
                    prompts.append(line)
                if prompts:
                    results = await launcher.batch(prompts)
                    for r in results:
                        print(f"\n--- {r['agent'].upper()} ({r['latency_ms']}ms) ---")
                        print(r["response"][:500])
                continue

            # Agent-specific commands
            agent_type = None
            for prefix in AGENTS:
                if cmd.startswith(f"!{prefix} "):
                    agent_type = prefix
                    cmd = cmd[len(prefix) + 2:]
                    break

            result = await launcher.execute(cmd, agent_type)
            print(f"\n{'─'*60}")
            print(result["response"])
            print(f"{'─'*60}")
            print(f"⚡ {result['latency_ms']}ms | 🤖 {result['agent']} | 💰 {result['cost']}")
            print()

        except KeyboardInterrupt:
            print("\n👋 Empire shutting down.")
            break
        except Exception as e:
            logger.error(f"Error: {e}")


async def main() -> None:
    launcher = PowerLauncher()

    if len(sys.argv) > 1:
        # Single task mode
        prompt = " ".join(sys.argv[1:])
        result = await launcher.execute(prompt)
        print(result["response"])
    else:
        await interactive(launcher)


if __name__ == "__main__":
    asyncio.run(main())
