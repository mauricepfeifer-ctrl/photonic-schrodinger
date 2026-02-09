#!/usr/bin/env python3
"""
🚀 revenue_burst.py

Automated "Money Printer" Script.
1. Scans (Simulated) Upwork/Fiverr for AI Automation Gigs.
2. Uses DeepSeek-R1 (Sales Agent) to write hyper-personalized proposals.
3. Saves drafts to 'revenue_drafts/' for one-click sending.

Usage:
  python revenue_burst.py
"""
import asyncio
import json
import os
import time
from datetime import datetime
from typing import List, Dict, Any

from ollama_engine import OllamaEngine, LLMResponse

# ─── CONFIG ─────────────────────────────────────────
OUTPUT_DIR = "revenue_drafts"
MODEL_SALES = "deepseek-r1:8b"  # Reasoning model for high-conversion copy

# ─── MOCKED GIG DATA (Real scraping is hard without API) ──
# In a real version, we'd use `requests` to scrape RSS feeds or APIs.
MOCK_GIGS = [
    {
        "id": "gig_101",
        "platform": "Upwork",
        "title": "Need AI Chatbot for Real Estate Agency",
        "description": "Looking for a developer to build a chatbot that qualifies leads for my real estate agency. Must connect to KVCore.",
        "budget": "$500 - $1000",
        "client": "Marcus R."
    },
    {
        "id": "gig_102",
        "platform": "Fiverr",
        "title": "Automate my Instagram Content Creation",
        "description": "I need a system that takes my blog posts and turns them into IG captions and images automatically.",
        "budget": "$200",
        "client": "Sarah L."
    },
    {
        "id": "gig_103",
        "platform": "Upwork",
        "title": "Scrape emails from LinkedIn and enrich data",
        "description": "Need a python script to scrape leads and find emails. Export to CSV.",
        "budget": "$150",
        "client": "TechFlow Inc."
    }
]

SYSTEM_PROMPT = (
    "You are an Elite Upwork/Fiverr Proposal Writer. "
    "Write high-converting, personalized proposals. "
    "Structure: 1. Hook (Address pain point) 2. Solution (How you fix it) 3. Proof/Authority 4. CTA (Call to Action). "
    "Keep it under 150 words. Professional but punchy."
)


class RevenueBurst:
    def __init__(self):
        self.llm = OllamaEngine(model=MODEL_SALES)
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)

    async def generate_proposal(self, gig: Dict[str, Any]) -> str:
        """Generates a proposal for a specific gig."""
        print(f"⚡ Generating proposal for: {gig['title']} ({gig['budget']})...")
        
        prompt = (
            f"Write a proposal for this gig:\n"
            f"Title: {gig['title']}\n"
            f"Description: {gig['description']}\n"
            f"Client: {gig['client']}\n"
            f"Platform: {gig['platform']}\n"
            f"Budget: {gig['budget']}\n\n"
            f"Focus on the client's goal. Don't be generic."
        )

        resp = await self.llm.chat([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ])
        assert isinstance(resp, LLMResponse)
        return resp.content

    async def run(self):
        print(f"💰 STARTING REVENUE BURST SCAN...")
        print(f"🎯 Target: Lead Generation & Automation Gigs")
        print(f"🤖 Model: {MODEL_SALES} (DeepSeek-R1)\n")

        tasks = []
        for gig in MOCK_GIGS:
            tasks.append(self.process_gig(gig))
        
        await asyncio.gather(*tasks)
        print(f"\n✅ DONE! Check '{OUTPUT_DIR}' for your proposals.")

    async def process_gig(self, gig: Dict[str, Any]):
        """Pipeline: Gen Proposal -> Save File"""
        try:
            proposal = await self.generate_proposal(gig)
            self._save_draft(gig, proposal)
        except Exception as e:
            print(f"❌ Failed {gig['id']}: {e}")

    def _save_draft(self, gig: Dict[str, Any], proposal: str):
        filename = f"{OUTPUT_DIR}/{gig['platform']}_{gig['id']}.txt"
        with open(filename, "w") as f:
            f.write(f"--- GIG DETAILS ---\n")
            f.write(f"Title: {gig['title']}\n")
            f.write(f"Budget: {gig['budget']}\n")
            f.write(f"Link: [Insert Link]\n")
            f.write(f"-------------------\n\n")
            f.write(proposal)
        print(f"📝 Saved draft: {filename}")


if __name__ == "__main__":
    asyncio.run(RevenueBurst().run())
