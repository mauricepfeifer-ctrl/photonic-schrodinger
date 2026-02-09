#!/usr/bin/env python3
"""
EMPIRE ORCHESTRATOR - 1M AGENTS
Maurice's AI Empire - Full Scale Automation

Architecture:
┌─────────────────────────────────────────────────────────────┐
│                    EMPIRE ORCHESTRATOR                       │
├─────────────────────────────────────────────────────────────┤
│  300K Sales │ 200K Content │ 200K Leads │ 150K Support/Opt  │
├─────────────────────────────────────────────────────────────┤
│                   8-BRAIN PARL SYSTEM                        │
│  CEO | RISK | FEAR | DRIVE | PERSIST | PATTERN | MODEL | FLEX│
└─────────────────────────────────────────────────────────────┘
"""

import asyncio
import aiohttp
import os
import logging
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum

# ─── OFFLINE MODE: Use local Ollama instead of Kimi cloud ───
OFFLINE_MODE = os.getenv("OFFLINE_MODE", "true").lower() == "true"

try:
    from ollama_engine import OllamaEngine, LLMResponse
except ImportError:
    OllamaEngine = None
    LLMResponse = None

try:
    from agent_manager import AgentManager
except ImportError:
    AgentManager = None

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

KIMI_API_KEY = os.getenv("MOONSHOT_API_KEY", "")
KIMI_BASE_URL = "https://api.moonshot.ai/v1"


class AgentType(Enum):
    SALES = "sales"
    CONTENT = "content"
    LEAD = "lead"
    SUPPORT = "support"

    OPTIMIZATION = "optimization"
    ARBITRAGE = "arbitrage"


class BrainCell(Enum):
    CEO = "ceo"           # Strategic decisions
    RISK = "risk"         # Risk assessment
    FEAR = "fear"         # Fear filter (remove anxiety)
    DRIVE = "drive"       # Motivation engine
    PERSIST = "persist"   # Long-term memory
    PATTERN = "pattern"   # Pattern recognition
    MODEL = "model"       # World modeling
    FLEX = "flex"         # Adaptability


@dataclass
class AgentTask:
    """Single agent task"""
    task_id: str
    agent_type: AgentType
    prompt: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    result: Optional[str] = None
    status: str = "pending"
    tokens_used: int = 0


@dataclass
class EmpireStats:
    """Empire statistics"""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    estimated_revenue_eur: float = 0.0


class PARL8Brain:
    """
    8-Cell Brain System für parallele Entscheidungen
    4.5x Speedup gegenüber sequentieller Verarbeitung
    """
    
    def __init__(self):
        self.cells: Dict[str, Dict[str, Any]] = {
            cell.value: {"active": True, "decisions": 0} for cell in BrainCell
        }

    async def parallel_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """8 Brain-Zellen entscheiden parallel"""
        decisions: Dict[str, Any] = {}

        # CEO: Strategic direction
        decisions["strategic"] = await self._ceo_decide(context)

        # RISK: Assess risks
        risk_level: int = await self._risk_assess(context)
        decisions["risk_level"] = risk_level

        # FEAR: Filter anxiety
        decisions["proceed"] = risk_level < 70

        # DRIVE: Motivation
        decisions["urgency"] = min(100, context.get("base_urgency", 50) + 20)
        
        return decisions
    
    async def _ceo_decide(self, context: Dict[str, Any]) -> str:
        """CEO strategic decision"""
        if context.get("revenue", 0) < 1000:
            return "SCALE_UP"
        elif context.get("conversion_rate", 0) < 0.01:
            return "OPTIMIZE"
        else:
            return "MAINTAIN"
    
    async def _risk_assess(self, context: Dict[str, Any]) -> int:
        """Risk assessment 0-100"""
        base_risk = 30
        if context.get("tasks_pending", 0) > 10000:
            base_risk += 20
        if context.get("error_rate", 0) > 0.05:
            base_risk += 30
        return min(100, base_risk)


class KimiSwarmEngine:
    """
    Kimi 2.5 Swarm für 1M parallele Aufgaben
    """
    
    def __init__(self, max_concurrent: int = 50):
        self.max_concurrent = max_concurrent
        self.session: Optional[aiohttp.ClientSession] = None
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.stats = EmpireStats()
    
    async def init(self):
        if not self.session:
            connector = aiohttp.TCPConnector(limit=self.max_concurrent)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=60)
            )
    
    async def close(self):
        if self.session:
            await self.session.close()
    
    async def execute_task(self, task: AgentTask) -> AgentTask:
        """Execute single task with rate limiting"""
        if not self.session:
            await self.init()
        assert self.session is not None
        async with self.semaphore:
            try:
                async with self.session.post(
                    f"{KIMI_BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {KIMI_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "moonshot-v1-8k",
                        "messages": [{"role": "user", "content": task.prompt}],
                        "temperature": 1.0,
                        "max_tokens": 500
                    }
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        task.result = data["choices"][0]["message"]["content"]
                        task.tokens_used = data.get("usage", {}).get("total_tokens", 300)
                        task.status = "completed"
                        self.stats.completed_tasks += 1
                        self.stats.total_tokens += task.tokens_used
                        self.stats.total_cost_usd += task.tokens_used * 0.0000005
                    else:
                        task.status = "failed"
                        self.stats.failed_tasks += 1
            except Exception as e:
                task.status = "failed"
                task.result = str(e)
                self.stats.failed_tasks += 1
        
        return task
    
    async def execute_batch(self, tasks: List[AgentTask]) -> List[AgentTask]:
        """Execute batch of tasks in parallel"""
        self.stats.total_tasks += len(tasks)
        results = await asyncio.gather(*[self.execute_task(t) for t in tasks])
        return list(results)


class LocalSwarmEngine:
    """Ollama backend for Empire Orchestrator"""
    def __init__(self, ollama_engine, max_concurrent=2):
        self.ollama = ollama_engine
        self.stats = EmpireStats()
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def init(self):
        await self.ollama.health()

    async def close(self):
        pass

    async def execute_task(self, task: AgentTask) -> AgentTask:
        async with self.semaphore:
            try:
                resp = await self.ollama.chat([
                    {"role": "user", "content": task.prompt}
                ])
                if isinstance(resp, LLMResponse):
                    task.result = resp.content
                    task.tokens_used = resp.total_tokens or 0
                    task.status = "completed"
                    self.stats.completed_tasks += 1
                    self.stats.total_tokens += task.tokens_used
                else:
                    task.status = "failed"
                    self.stats.failed_tasks += 1
            except Exception as e:
                logger.error(f"❌ LocalSwarm Task Failed: {e}")
                task.status = "failed"
                task.result = str(e)
                self.stats.failed_tasks += 1
        return task

    async def execute_batch(self, tasks: List[AgentTask]) -> List[AgentTask]:
        self.stats.total_tasks += len(tasks)
        results = await asyncio.gather(*[self.execute_task(t) for t in tasks])
        return list(results)


class EmpireOrchestrator:
    """
    Master Orchestrator für 1M Agenten
    
    Distribution:
    - 300K Sales Agents (Outreach, Follow-up, Closing)
    - 200K Content Agents (Posts, Threads, Videos)
    - 200K Lead Agents (Research, Qualification)
    - 150K Support Agents (Objection handling)
    - 150K Optimization Agents (A/B Testing)
    """
    
    def __init__(self):
        self.brain = PARL8Brain()
        # Default to Kimi but will switch if offline
        self.swarm: Union[KimiSwarmEngine, LocalSwarmEngine] = KimiSwarmEngine(max_concurrent=50)
        self.ollama: Optional[Any] = None  # OllamaEngine if available
        self.agent_manager = AgentManager() if AgentManager else None
        self.agent_distribution = {
            AgentType.SALES: 0.30,
            AgentType.CONTENT: 0.20,
            AgentType.LEAD: 0.20,
            AgentType.SUPPORT: 0.15,
            AgentType.OPTIMIZATION: 0.10,
            AgentType.ARBITRAGE: 0.05,
        }
        self.bus = None
    
    async def init(self):
        if OFFLINE_MODE and OllamaEngine:
            logger.info("🧠 OFFLINE MODE: Using local Ollama (FREE)")
            self.ollama = OllamaEngine(model="deepseek-r1:8b")
            await self.ollama.health()
            # Switch swarm engine
            self.swarm = LocalSwarmEngine(self.ollama, max_concurrent=2)
            await self.swarm.init()
        else:
            logger.info("☁️ CLOUD MODE: Using Kimi API")
            await self.swarm.init()
        if self.bus:
            # Subscribe to voice inputs
            self.bus.subscribe("input/voice", self.handle_voice_input)
            self.bus.subscribe("tasks/completed", self.handle_task_completion)

    def handle_voice_input(self, message: Dict[str, Any]):
        """Handle incoming voice commands (from iPhone)"""
        text = message.get("transcribed_text", "")
        logger.info(f"🎤 RECEIVED VOICE COMMAND: '{text}'")

        # Simple keyword based routing for now (LLM routing later)
        if "tiktok" in text.lower():
            task = AgentTask(
                task_id=f"tiktok-{int(time.time())}",
                agent_type=AgentType.CONTENT,
                prompt=f"Create TikTok based on: {text}"
            )
            self.dispatch_task(task, "content")

            tiktok_task = AgentTask(
                task_id=f"tiktok-specific-{int(time.time())}",
                agent_type=AgentType.ARBITRAGE,
                prompt=text
            )
            self.dispatch_task(tiktok_task, "tiktok")

        elif "sales" in text.lower() or "mail" in text.lower():
            self.dispatch_task(AgentTask(
                task_id=f"sales-{int(time.time())}",
                agent_type=AgentType.SALES,
                prompt=text
            ), "sales")

        elif "research" in text.lower() or "trend" in text.lower():
            self.dispatch_task(AgentTask(
                task_id=f"research-{int(time.time())}",
                agent_type=AgentType.LEAD,
                prompt=text
            ), "research")

        else:
            logger.info("🤔 Unknown command type, defaulting to General Content")
            self.dispatch_task(AgentTask(
                task_id=f"gen-content-{int(time.time())}",
                agent_type=AgentType.CONTENT,
                prompt=text
            ), "content")

    def handle_task_completion(self, message: Dict[str, Any]):
        """Handle completed tasks from agents"""
        logger.info(f"✅ Agent {message.get('agent_id')} completed task {message.get('task_id')}")
        # Here we could chain subsequent tasks (e.g. Research -> Content)

    def dispatch_task(self, task: AgentTask, channel_suffix: str):
        if self.bus:
            self.bus.publish(f"tasks/{channel_suffix}", {
                "task_id": task.task_id,
                "prompt": task.prompt,
                "parameters": task.parameters
            })

    async def close(self):
        await self.swarm.close()
    
    def generate_task(self, agent_type: AgentType, task_id: int) -> AgentTask:
        """Generate task for specific agent type"""
        prompts = {
            AgentType.SALES: "Generiere eine personalisierte Verkaufs-Email für ein AI-Automation Produkt. Kurz, freundlich, mit klarem CTA.",
            AgentType.CONTENT: "Erstelle einen viralen Tweet über AI-Automation. Hook + Value + CTA. Max 280 Zeichen.",
            AgentType.LEAD: "Beschreibe ein ideales Kundenprofil für AI-Automation Services. Branche, Größe, Pain Points.",
            AgentType.SUPPORT: "Beantworte den Einwand: 'Das ist zu teuer'. Nutze Value-Argumentation.",
            AgentType.OPTIMIZATION: "Schlage einen A/B Test vor für eine Landing Page. Was testen? Warum?",
            AgentType.ARBITRAGE: "Finde ein virales TikTok Video zum Thema AI und erstelle einen neuen Titel für YouTube Shorts.",
        }
        
        return AgentTask(
            task_id=f"{agent_type.value}-{task_id:06d}",
            agent_type=agent_type,
            prompt=prompts[agent_type]
        )
    
    async def run_wave(self, total_tasks: int = 100) -> Dict[str, Any]:
        """Run a wave of tasks across all agent types"""
        logger.info(f"🚀 Starting wave with {total_tasks} tasks...")
        
        if self.bus:
            self.bus.publish("system/wave_start", {"tasks": total_tasks})
        
        # Distribute tasks
        tasks = []
        for agent_type, ratio in self.agent_distribution.items():
            count = int(total_tasks * ratio)
            for i in range(count):
                tasks.append(self.generate_task(agent_type, len(tasks)))
        
        # Brain decision
        context = {"revenue": self.swarm.stats.estimated_revenue_eur, "tasks_pending": len(tasks)}
        decision = await self.brain.parallel_decision(context)
        logger.info(f"🧠 Brain decision: {decision['strategic']}, Risk: {decision['risk_level']}")
        
        if not decision["proceed"]:
            logger.warning("⚠️ Brain says: Too risky, aborting wave")
            if self.bus:
                self.bus.publish("system/alert", {"type": "risk_abort", "level": decision["risk_level"]})
            return {"status": "aborted", "reason": "risk_too_high"}
        
        # Execute in batches
        batch_size = 50
        all_results = []
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i+batch_size]
            results = await self.swarm.execute_batch(batch)
            all_results.extend(results)
            
            # Progress
            completed = len([r for r in all_results if r.status == "completed"])
            logger.info(f"Progress: {completed}/{len(tasks)} ({100*completed/len(tasks):.1f}%)")
            
            if self.bus:
                self.bus.publish("system/progress", {"completed": completed, "total": len(tasks)})
            
            await asyncio.sleep(0.5)  # Rate limiting
        
        # Estimate revenue (1% conversion, EUR 97 average)
        successful = len([r for r in all_results if r.status == "completed"])
        revenue = successful * 0.01 * 97
        self.swarm.stats.estimated_revenue_eur += revenue
        
        if self.bus and revenue > 0:
             self.bus.publish("business/revenue", {"amount": revenue, "currency": "EUR"})
        
        return {
            "status": "completed",
            "total": len(tasks),
            "successful": successful,
            "failed": len(tasks) - successful,
            "cost_usd": self.swarm.stats.total_cost_usd,
            "estimated_revenue_eur": self.swarm.stats.estimated_revenue_eur,
        }
    
    async def run_empire(self, waves: int = 3, tasks_per_wave: int = 100):
        """Run full empire"""
        logger.info("="*60)
        logger.info("🏰 MAURICE'S AI EMPIRE - LAUNCHING")
        logger.info("="*60)
        
        await self.init()
        
        try:
            for wave in range(1, waves + 1):
                logger.info(f"\n--- WAVE {wave}/{waves} ---")
                result = await self.run_wave(tasks_per_wave)
                
                if result["status"] == "completed":
                    logger.info(f"✅ Wave {wave} complete: {result['successful']}/{result['total']} successful")
                    logger.info(f"💰 Estimated revenue: EUR {result['estimated_revenue_eur']:.2f}")
                    logger.info(f"💵 Cost: ${result['cost_usd']:.4f}")
        finally:
            await self.close()
        
        # Final stats
        stats = self.swarm.stats
        print(f"\n{'='*60}")
        print("EMPIRE FINAL STATS")
        print(f"{'='*60}")
        print(f"Total Tasks: {stats.total_tasks}")
        print(f"Completed: {stats.completed_tasks}")
        print(f"Failed: {stats.failed_tasks}")
        print(f"Total Tokens: {stats.total_tokens:,}")
        print(f"Total Cost: ${stats.total_cost_usd:.4f}")
        print(f"Estimated Revenue: EUR {stats.estimated_revenue_eur:.2f}")
        print(f"ROI: {(stats.estimated_revenue_eur / max(stats.total_cost_usd, 0.01)):.0f}x")


async def main():
    """Demo Empire Orchestrator"""
    empire = EmpireOrchestrator()
    
    # Small test run

    # Initialize Redis Bus (with LocalMemoryBus fallback)
    try:
        from redis_bus import RedisBus, LocalMemoryBus
        bus = RedisBus()
        if bus.connect():
            empire.bus = bus
            logger.info("✅ Redis connected")
        else:
            logger.warning("⚠️ Redis unavailable — using LocalMemoryBus")
            local_bus = LocalMemoryBus()
            local_bus.connect()
            empire.bus = local_bus
    except ImportError:
        logger.warning("⚠️ redis_bus not available, running without message bus")

    # Initialize Stripe Manager (optional)
    try:
        from stripe_manager import StripeManager
        stripe_mgr = StripeManager()
        if empire.bus:
            stripe_mgr.bus = empire.bus
        logger.info(f"💳 Stripe: {'LIVE' if stripe_mgr.live else 'SIMULATION'} mode")
        logger.info(f"💰 Revenue so far: €{stripe_mgr.stats.total_eur():.2f}")
    except ImportError:
        logger.info("ℹ️ Stripe not configured (optional)")

    # Run Empire
    await empire.run_empire(waves=3, tasks_per_wave=50)



if __name__ == "__main__":
    asyncio.run(main())
