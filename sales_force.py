#!/usr/bin/env python3
"""
🚀 AI SALES FORCE — ELITE VERTRIEBSTEAM
Maurice's AI Empire — Maximum Revenue Generation

6 Specialized Agents working in parallel:
1. PROSPECTOR    — Finds high-value leads
2. CLOSER        — Writes Dirk Kreuter style proposals
3. CONTENT SNIPER— Generates viral hooks (TikTok/Reels)
4. SEO HUNTER    — Writes traffic-generating blog posts
5. EMAIL BLASTER — Personalised cold outreach
6. SOCIAL STRIKER— Engages on X/LinkedIn

Usage:
    python sales_force.py --mode all
    python sales_force.py --agent closer --input "Lead: Real Estate Agent"
"""
import asyncio
import aiohttp
import argparse
import json
import logging
import os
import random
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional

# Setup Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("SalesForce")

# ─── CONFIGURATION ────────────────────────────────
OUTPUT_DIR = "sales_output"
KIMI_API_KEY = os.getenv("MOONSHOT_API_KEY", "")
KIMI_BASE_URL = "https://api.moonshot.ai/v1/chat/completions"
MODEL_KIMI = "moonshot-v1-8k"
MODEL_OLLAMA = "deepseek-r1:8b" 

# Dirk Kreuter Principles
DIRK_KREUTER_PROMPT = """
DU BIST EIN ELITE-VERKÄUFER NACH DIRK KREUTER.
Deine Prinzipien:
1. GEISTIGE BRANDSTIFTUNG: Stelle Fragen, die den Kunden das Problem selbst erkennen lassen.
2. SCHMERZ & LÖSUNG: Finde den Schmerzpunkt und biete sofort die Lösung.
3. VERKNAPPUNG: Das Angebot ist nicht ewig verfügbar.
4. COMMITMENT: Hole dir kleine Jas ab.
5. HANDLUNGSAUFFORDERUNG: Sag dem Kunden genau, was er tun soll.
Kein Weichspüler-Deutsch. Klar, direkt, abschlussstark.
"""

SALES_ROLES = {
    "prospector": {
        "name": "🕵️ PROSPECTOR",
        "desc": "Findet und qualifiziert Leads",
        "system": "Du bist ein Lead-Researcher. Finde Firmen, die AI Automation brauchen. Analysiere deren Website-Lücken."
    },
    "closer": {
        "name": "🤝 CLOSER",
        "desc": "Schreibt unwiderstehliche Angebote",
        "system": DIRK_KREUTER_PROMPT + "\nSchreibe ein Proposal für diesen Lead. Fokus: ROI und Zeitersparnis."
    },
    "content_sniper": {
        "name": "🎯 CONTENT SNIPER",
        "desc": "Erstellt virale Hooks für TikTok/Reels",
        "system": "Du bist ein Viral-Expert. Erstelle 3 Skripte für 30-Sekunden Videos. Hook muss in den ersten 2 Sekunden sitzen. Thema: AI Automation."
    },
    "seo_hunter": {
        "name": "🔎 SEO HUNTER",
        "desc": "Schreibt SEO-optimierte Artikel",
        "system": "Schreibe einen 800-Wörter Blogpost über 'Wie AI Agents Geld sparen'. Nutze Keywords: AI Automation, Business Skalierung, Zeit sparen."
    },
    "email_blaster": {
        "name": "📧 EMAIL BLASTER",
        "desc": "Kaltakquise-Emails die konvertieren",
        "system": DIRK_KREUTER_PROMPT + "\nSchreibe eine Cold-Email Sequenz (3 Mails). Betreff muss klickstark sein."
    },
    "social_striker": {
        "name": "🐦 SOCIAL STRIKER",
        "desc": "Engagement auf X und LinkedIn",
        "system": "Erstelle 5 provozierende Tweets/Posts über die Zukunft von Arbeit ohne AI. Sei kontrovers."
    }
}

@dataclass
class AgentResult:
    agent: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    model_used: str = ""

class SalesForce:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
        
        # Check for Models
        self.use_kimi = bool(KIMI_API_KEY) and not dry_run
        if self.use_kimi:
            logger.info(f"🟢 Using Kimi API (Cloud Power)")
        else:
            logger.info(f"🟡 Using Ollama (Local/Simulated)")

    async def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Central LLM caller: Kimi -> Ollama -> Mock"""
        if self.dry_run:
            await asyncio.sleep(1)
            return f"[DRY RUN OUTPUT] Simulated response for: {user_prompt[:50]}..."

        if self.use_kimi:
            try:
                async with aiohttp.ClientSession() as session:
                    payload = {
                        "model": MODEL_KIMI,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.7
                    }
                    headers = {
                        "Authorization": f"Bearer {KIMI_API_KEY}",
                        "Content-Type": "application/json"
                    }
                    async with session.post(KIMI_BASE_URL, json=payload, headers=headers) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            return data["choices"][0]["message"]["content"]
                        else:
                            logger.error(f"Kimi API Error: {await resp.text()}")
            except Exception as e:
                logger.error(f"Kimi connection failed: {e}")
        
        # Fallback to Ollama (via simulated local call for this script to keep it simple self-contained)
        # OR actually calling local ollama if possible. For robustnes in this script, 
        # let's assume if Kimi fails, we might just use a placeholder or use the ollama_engine if imported.
        # Here we simulate the fallback to keep dependency low, or we could try to import.
        
        try:
            from ollama_engine import OllamaEngine
            engine = OllamaEngine(model=MODEL_OLLAMA)
            resp = await engine.chat([
               {"role": "system", "content": system_prompt},
               {"role": "user", "content": user_prompt} 
            ])
            return resp.class_content if hasattr(resp, 'content') else str(resp)
        except ImportError:
            return f"[OFFLINE BACKUP] Simulated AI response. Imagine brilliant text here for: {user_prompt[:30]}..."
        except Exception as e:
            return f"[ERROR] Both Cloud & Local AI failed: {e}"

    async def run_agent(self, agent_key: str, input_data: str = "") -> AgentResult:
        """Executes a single agent's mission"""
        role = SALES_ROLES.get(agent_key)
        if not role:
            raise ValueError(f"Unknown agent: {agent_key}")

        logger.info(f"🚀 {role['name']} starting mission...")
        
        prompt = input_data if input_data else "Generiere deine beste Arbeit basierend auf deiner Rolle. Sei kreativ und profitabel."
        
        content = await self._call_llm(role["system"], prompt)
        
        # Save output
        filename = f"{OUTPUT_DIR}/{agent_key}_{int(time.time())}.md"
        with open(filename, "w") as f:
            f.write(f"# OUTPUT: {role['name']}\n")
            f.write(f"Date: {datetime.now()}\n")
            f.write(f"Prompt: {prompt}\n")
            f.write("-" * 40 + "\n\n")
            f.write(content)
        
        logger.info(f"✅ {role['name']} finished. Output saved to {filename}")
        return AgentResult(agent=agent_key, content=content, model_used=MODEL_KIMI if self.use_kimi else MODEL_OLLAMA)

    async def run_all(self):
        """Runs the entire team in parallel"""
        logger.info("🔥 ACTIVATING FULL SALES FORCE...")
        tasks = []
        for key in SALES_ROLES.keys():
            # Give each agent a generic starter task if running all
            context = "Focus on the AI Automation Agency niche. We sell 'AI Employees' to small businesses."
            tasks.append(self.run_agent(key, context))
        
        results = await asyncio.gather(*tasks)
        logger.info("🏆 ALL MISSIONS ACCOMPLISHED.")
        return results

def main():
    parser = argparse.ArgumentParser(description="AI Sales Force")
    parser.add_argument("--agent", choices=list(SALES_ROLES.keys()), help="Run specific agent")
    parser.add_argument("--mode", choices=["single", "all"], default="all", help="Execution mode")
    parser.add_argument("--input", help="Specific instruction for the agent")
    parser.add_argument("--dry-run", action="store_true", help="Simulate AI calls")
    
    args = parser.parse_args()
    
    sf = SalesForce(dry_run=args.dry_run)
    
    sf = SalesForce(dry_run=args.dry_run)
    
    if args.agent:
        asyncio.run(sf.run_agent(args.agent, args.input))
    else:
        asyncio.run(sf.run_all())

if __name__ == "__main__":
    main()
