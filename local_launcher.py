#!/usr/bin/env python3
"""
🚀 MAURICE'S AI IMPERIUM - GOD MODE LAUNCHER
Runs the entire Swarm Infrastructure LOCALLY (No Docker required).
Leverages Google Antigravity Architecture.
"""

import threading
import time
import logging
import sys
import asyncio

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("Launcher")

# Import Core Components
from redis_bus import LocalMemoryBus
from empire_orchestrator import EmpireOrchestrator, AgentType
from agents.content_agent import ContentAgent
from agents.sales_agent import SalesAgent
from agents.research_agent import ResearchAgent
from agents.tiktok_agent import TikTokAgent

def run_agent_thread(agent_class, bus):
    """Refactored helper to run an agent in a thread"""
    try:
        agent = agent_class() # Instantiate with default, then inject bus or modify init
        # Hack: Since we didn't update sub-classes __init__ to pass kwargs directly in this step,
        # we manually swap the bus before starting.
        agent.bus = bus 
        agent.start()
    except Exception as e:
        logger.error(f"❌ Error in agent thread: {e}")

def main():
    print("\n\n")
    print("╔════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                          ║")
    print("║          👑 AI IMPERIUM - GOOGLE ANTIGRAVITY EDITION                    ║")
    print("║             >> LOCAL SWARM MODE ACTIVATED <<                             ║")
    print("║                                                                          ║")
    print("╚════════════════════════════════════════════════════════════════════════╝")
    print("\n")

    # 1. Initialize Central Nervous System
    logger.info("🧠 Initializing In-Memory Hive Mind (LocalBus)...")
    bus = LocalMemoryBus()
    bus.connect()

    # 2. Initialize Orchestrator
    logger.info("🎼 Initializing Empire Orchestrator...")
    orchestrator = EmpireOrchestrator()
    orchestrator.bus = bus # Inject Local Bus
    # We need to run the orchestrator's init loop. Since it's async, we need a wrapper.
    
    def run_orchestrator():
        async def _run():
            await orchestrator.init()
            # Keep alive
            while True:
                await asyncio.sleep(1)
        asyncio.run(_run())

    threading.Thread(target=run_orchestrator, daemon=True, name="Orchestrator").start()

    # 3. Spawn Agents
    logger.info("🤖 Spawning Agents...")
    
    agents = [
        (ContentAgent, "Content"),
        (SalesAgent, "Sales"),
        (ResearchAgent, "Research"),
        (TikTokAgent, "TikTok")
    ]
    
    for AgentClass, name in agents:
        logger.info(f"   ↳ Spawning {name} Agent...")
        t = threading.Thread(target=run_agent_thread, args=(AgentClass, bus), daemon=True, name=name)
        t.start()
        time.sleep(0.5)

    print("\n✅ SYSTEM ONLINE. WAITING FOR COMMANDS.\n")
    print("commands: 'status', 'exit', or just type a request (e.g. 'Create a TikTok')\n")

    # 4. Command Loop
    while True:
        try:
            cmd = input("🎤 COMMAND > ")
            
            if cmd.lower() in ["exit", "quit"]:
                print("Shutting down...")
                sys.exit(0)
                
            elif cmd.lower() == "status":
                bus.publish("system/status_request", {})
                
            elif cmd.strip():
                # Simulate Voice Input
                payload = {
                    "source": "local_terminal",
                    "transcribed_text": cmd,
                    "timestamp": time.time(),
                    "user": "Maurice"
                }
                bus.publish("input/voice", payload)
                
        except KeyboardInterrupt:
            print("\nShutting down...")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Error: {e}")

if __name__ == "__main__":
    main()
