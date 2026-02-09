#!/usr/bin/env python3
"""
AGENT MANAGER - Automated Agent Lifecycle & Revenue Ranking

Der Agent der am meisten Geld macht → Platz 1.
Top-Performer bekommen mehr Tasks und Priorität.
Underperformer werden pausiert.

Ranking is persisted to agent_rankings.json.
"""
from __future__ import annotations

import json
import os
import time
import logging
from datetime import datetime
from itertools import islice
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, fields, field, asdict

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RANKINGS_FILE = "agent_rankings.json"
TOP_BOOST_SLOTS = 3      # Top 3 get boosted
DEMOTE_THRESHOLD = 8     # Rank 8-10 get demoted
MAX_RANKED = 10           # Top 10 leaderboard


def _to_int(x: Any, default: int = 0) -> int:
    try:
        return default if x is None else int(x)
    except Exception:
        return default


def _to_float(x: Any, default: float = 0.0) -> float:
    try:
        return default if x is None else float(x)
    except Exception:
        return default


@dataclass
class AgentRecord:
    """Track an agent's performance"""
    agent_id: str
    agent_type: str
    revenue_eur: float = 0.0
    tasks_completed: int = 0
    tasks_failed: int = 0
    avg_response_ms: float = 0.0
    rank: int = 0
    status: str = "active"          # active, boosted, demoted, paused
    priority_multiplier: float = 1.0  # boosted agents get more tasks
    created_at: str = ""
    last_active: str = ""

    def success_rate(self) -> float:
        total = self.tasks_completed + self.tasks_failed
        return self.tasks_completed / max(total, 1)

    def revenue_per_task(self) -> float:
        return self.revenue_eur / max(self.tasks_completed, 1)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> AgentRecord:
        """Type-safe construction from JSON dict (handles str→int/float)"""
        allowed = {f.name for f in fields(cls)}
        clean: Dict[str, Any] = {k: v for k, v in d.items() if k in allowed}

        clean["agent_id"] = str(clean.get("agent_id", "unknown"))
        clean["agent_type"] = str(clean.get("agent_type", "unknown"))
        clean["status"] = str(clean.get("status", "active"))
        clean["created_at"] = str(clean.get("created_at", ""))
        clean["last_active"] = str(clean.get("last_active", ""))

        clean["revenue_eur"] = _to_float(clean.get("revenue_eur"), 0.0)
        clean["avg_response_ms"] = _to_float(clean.get("avg_response_ms"), 0.0)
        clean["priority_multiplier"] = _to_float(clean.get("priority_multiplier"), 1.0)
        clean["tasks_completed"] = _to_int(clean.get("tasks_completed"), 0)
        clean["tasks_failed"] = _to_int(clean.get("tasks_failed"), 0)
        clean["rank"] = _to_int(clean.get("rank"), 0)

        return cls(**clean)


class AgentManager:
    """
    Automated Agent Lifecycle Manager with Revenue Ranking.

    Features:
    - Revenue-based Top 10 leaderboard
    - Auto-boost top performers (more tasks, higher priority)
    - Auto-demote underperformers
    - Persistent rankings
    """

    def __init__(self, rankings_file: str = RANKINGS_FILE):
        self.rankings_file = rankings_file
        self.agents: Dict[str, AgentRecord] = {}
        self._load_rankings()

    # ─── PERSISTENCE ────────────────────────────────────
    def _load_rankings(self) -> None:
        if os.path.exists(self.rankings_file):
            try:
                with open(self.rankings_file, "r") as f:
                    data = json.load(f)
                for agent_data in data.get("agents", []):
                    record = AgentRecord.from_dict(agent_data)
                    self.agents[record.agent_id] = record
                logger.info(f"📊 Loaded {len(self.agents)} agent records")
            except Exception as e:
                logger.error(f"❌ Failed to load rankings: {e}")

    def _save_rankings(self):
        data = {
            "agents": [asdict(a) for a in self.agents.values()],
            "last_updated": datetime.now().isoformat(),
            "total_revenue_eur": sum(a.revenue_eur for a in self.agents.values()),
        }
        with open(self.rankings_file, "w") as f:
            json.dump(data, f, indent=2)

    # ─── AGENT LIFECYCLE ────────────────────────────────
    def register_agent(self, agent_id: str, agent_type: str) -> AgentRecord:
        """Register a new agent or return existing"""
        if agent_id not in self.agents:
            self.agents[agent_id] = AgentRecord(
                agent_id=agent_id,
                agent_type=agent_type,
                created_at=datetime.now().isoformat(),
                last_active=datetime.now().isoformat(),
            )
            logger.info(f"🆕 Agent registered: {agent_id} ({agent_type})")
        return self.agents[agent_id]

    def report_task_completion(self, agent_id: str, revenue_eur: float = 0.0,
                                duration_ms: float = 0.0, success: bool = True):
        """Report task result – updates stats and triggers re-ranking"""
        if agent_id not in self.agents:
            logger.warning(f"⚠️ Unknown agent: {agent_id}")
            return

        agent = self.agents[agent_id]
        agent.last_active = datetime.now().isoformat()

        if success:
            agent.tasks_completed += 1
            agent.revenue_eur += revenue_eur
            # Running average for response time
            n = agent.tasks_completed
            agent.avg_response_ms = ((agent.avg_response_ms * (n - 1)) + duration_ms) / n
        else:
            agent.tasks_failed += 1

        self._update_rankings()
        self._save_rankings()

    # ─── RANKING ENGINE ─────────────────────────────────
    def _update_rankings(self):
        """Re-rank all agents by revenue and apply boost/demotion"""
        sorted_agents = sorted(
            self.agents.values(),
            key=lambda a: a.revenue_eur,
            reverse=True
        )

        for i, agent in enumerate(sorted_agents):
            agent.rank = i + 1

            if agent.rank <= TOP_BOOST_SLOTS:
                # 🚀 TOP PERFORMER – boost
                agent.status = "boosted"
                agent.priority_multiplier = 2.0 + (TOP_BOOST_SLOTS - agent.rank) * 0.5
                # Rank 1 = 3.0x, Rank 2 = 2.5x, Rank 3 = 2.0x
            elif agent.rank >= DEMOTE_THRESHOLD and agent.rank <= MAX_RANKED:
                # 📉 UNDERPERFORMER – demote
                agent.status = "demoted"
                agent.priority_multiplier = 0.5
            elif agent.rank > MAX_RANKED:
                # ⏸️ OUT OF TOP 10 – pause
                agent.status = "paused"
                agent.priority_multiplier = 0.1
            else:
                # Normal operation
                agent.status = "active"
                agent.priority_multiplier = 1.0

    def get_leaderboard(self, top_n: int = MAX_RANKED) -> List[AgentRecord]:
        """Get Top N agents by revenue"""
        ranked = sorted(
            self.agents.values(),
            key=lambda a: (a.revenue_eur, a.tasks_completed, -a.tasks_failed),
            reverse=True
        )
        return list(islice(ranked, top_n))

    def get_task_allocation(self, total_tasks: int) -> Dict[str, int]:
        """
        Distribute tasks based on ranking.
        Top agents get proportionally more tasks.
        """
        if not self.agents:
            return {}

        # Calculate total priority weight
        active_agents = [a for a in self.agents.values() if a.status != "paused"]
        total_weight = sum(a.priority_multiplier for a in active_agents)

        if total_weight == 0:
            return {}

        allocation = {}
        for agent in active_agents:
            share = agent.priority_multiplier / total_weight
            allocation[agent.agent_id] = max(1, int(total_tasks * share))

        return allocation

    def print_leaderboard(self):
        """Print the Top 10 leaderboard"""
        leaderboard = self.get_leaderboard()

        print(f"\n{'='*70}")
        print("👑  AGENT LEADERBOARD  –  Top Revenue Earners")
        print(f"{'='*70}")
        print(f"{'#':<4} {'Agent':<25} {'Revenue':>10} {'Tasks':>7} {'€/Task':>8} {'Status':>10} {'Prio':>6}")
        print(f"{'-'*70}")

        medals = {1: "🥇", 2: "🥈", 3: "🥉"}

        for agent in leaderboard:
            medal = medals.get(agent.rank, f"#{agent.rank}")
            status_icons = {
                "boosted": "🚀",
                "active": "✅",
                "demoted": "📉",
                "paused": "⏸️",
            }
            icon = status_icons.get(agent.status, "❓")

            print(f"{medal:<4} {agent.agent_id:<25} "
                  f"€{agent.revenue_eur:>8.2f} "
                  f"{agent.tasks_completed:>7} "
                  f"€{agent.revenue_per_task():>6.2f} "
                  f"{icon} {agent.status:>8} "
                  f"{agent.priority_multiplier:>5.1f}x")

        total_rev = sum(a.revenue_eur for a in self.agents.values())
        print(f"{'-'*70}")
        print(f"     TOTAL EMPIRE REVENUE: €{total_rev:,.2f}")
        print(f"{'='*70}\n")


# ─── STANDALONE TEST ──────────────────────────────────
def main():
    """Simulate agents with revenue to demo the ranking system"""
    manager = AgentManager(rankings_file="agent_rankings_test.json")

    # Register agents
    agents_config = [
        ("content-alpha",  "content"),
        ("sales-beast",    "sales"),
        ("research-pro",   "research"),
        ("tiktok-viral",   "tiktok"),
        ("content-beta",   "content"),
        ("sales-closer",   "sales"),
        ("lead-hunter",    "lead"),
        ("support-ace",    "support"),
        ("arbitrage-king", "arbitrage"),
        ("optimizer-x",    "optimization"),
        ("content-gamma",  "content"),
        ("sales-sniper",   "sales"),
    ]

    for agent_id, agent_type in agents_config:
        manager.register_agent(agent_id, agent_type)

    # Simulate revenue generation (different performance levels)
    import random
    random.seed(42)

    revenue_weights = {
        "sales-beast": 150,    # 🥇 Top earner
        "arbitrage-king": 120, # 🥈
        "sales-closer": 95,    # 🥉
        "content-alpha": 70,
        "tiktok-viral": 55,
        "lead-hunter": 40,
        "research-pro": 30,
        "content-beta": 20,
        "optimizer-x": 10,     # 📉 Demoted zone
        "support-ace": 5,      # 📉
        "content-gamma": 2,    # ⏸️ Paused
        "sales-sniper": 1,     # ⏸️
    }

    print("🎮 Simulating 50 task rounds...\n")

    for round_num in range(50):
        for agent_id, base_rev in revenue_weights.items():
            rev = base_rev * random.uniform(0.5, 1.5) / 50
            success = random.random() > 0.05
            manager.report_task_completion(
                agent_id=agent_id,
                revenue_eur=rev if success else 0,
                duration_ms=random.uniform(100, 2000),
                success=success
            )

    # Show results
    manager.print_leaderboard()

    # Show task allocation for 100 tasks
    allocation = manager.get_task_allocation(100)
    print("📋 Task Allocation (100 tasks):")
    for agent_id, tasks in sorted(allocation.items(), key=lambda x: -x[1]):
        print(f"  {agent_id:<25} → {tasks} tasks")

    # Cleanup test file
    if os.path.exists("agent_rankings_test.json"):
        os.remove("agent_rankings_test.json")


if __name__ == "__main__":
    main()
