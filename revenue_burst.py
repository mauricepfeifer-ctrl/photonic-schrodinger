#!/usr/bin/env python3
"""
🚀 revenue_burst.py

Automated "Money Printer" — Proposal Generator for Freelance Gigs.

Sources (priority order):
  1. 📡 REAL RSS Feeds — Upwork, Freelancer, and custom feeds
  2. ⌨️  CLI Manual Entry — Add gigs by hand
  3. 🎯 Fallback Seed Data — Pre-loaded niche gigs

Proposals are generated via Ollama (DeepSeek-R1) and saved to
'revenue_drafts/' for one-click sending.

Usage:
  python revenue_burst.py              # Auto-scan RSS feeds
  python revenue_burst.py --manual     # Enter gigs manually via CLI
  python revenue_burst.py --demo       # Use seed data (old mock mode)
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any, Dict, List, Optional

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_DIR)

try:
    from ollama_engine import OllamaEngine, LLMResponse
    HAS_OLLAMA = True
except ImportError:
    HAS_OLLAMA = False
    OllamaEngine = None   # type: ignore
    LLMResponse = None     # type: ignore

try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

# ─── CONFIG ─────────────────────────────────────────
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "revenue_drafts")
MODEL_SALES = os.getenv("MODEL_SALES", "deepseek-r1:8b")

# ─── RSS FEED SOURCES ──────────────────────────────
# Upwork publishes public RSS feeds for searches.
# Format: https://www.upwork.com/ab/feed/jobs/rss?q=KEYWORDS&sort=recency
RSS_FEEDS: List[Dict[str, str]] = [
    {
        "name": "Upwork — AI Automation",
        "url": "https://www.upwork.com/ab/feed/jobs/rss?q=AI+automation&sort=recency",
        "platform": "Upwork",
    },
    {
        "name": "Upwork — Chatbot Development",
        "url": "https://www.upwork.com/ab/feed/jobs/rss?q=chatbot+development&sort=recency",
        "platform": "Upwork",
    },
    {
        "name": "Upwork — n8n Automation",
        "url": "https://www.upwork.com/ab/feed/jobs/rss?q=n8n+automation&sort=recency",
        "platform": "Upwork",
    },
    {
        "name": "Upwork — Python AI Script",
        "url": "https://www.upwork.com/ab/feed/jobs/rss?q=python+AI+script&sort=recency",
        "platform": "Upwork",
    },
]

# ─── SEED GIGS (fallback / demo) ───────────────────
SEED_GIGS: List[Dict[str, Any]] = [
    {
        "id": "seed_101",
        "platform": "Upwork",
        "title": "Need AI Chatbot for Real Estate Agency",
        "description": "Looking for a developer to build a chatbot that qualifies leads for my real estate agency. Must connect to KVCore.",
        "budget": "$500 - $1000",
        "client": "Potential Client",
    },
    {
        "id": "seed_102",
        "platform": "Fiverr",
        "title": "Automate my Instagram Content Creation",
        "description": "I need a system that takes my blog posts and turns them into IG captions and images automatically.",
        "budget": "$200",
        "client": "Potential Client",
    },
    {
        "id": "seed_103",
        "platform": "Upwork",
        "title": "Build n8n workflow for CRM + Email automation",
        "description": "Need an n8n expert to connect HubSpot CRM to Mailchimp, with automated follow-ups.",
        "budget": "$300 - $600",
        "client": "Potential Client",
    },
    {
        "id": "seed_104",
        "platform": "Upwork",
        "title": "AI Sales Email Writer using LLM",
        "description": "Create a Python tool that generates personalized cold emails using locally-hosted LLM.",
        "budget": "$400",
        "client": "Potential Client",
    },
]

SYSTEM_PROMPT = (
    "You are an Elite Upwork/Fiverr Proposal Writer for an AI Automation agency. "
    "Write high-converting, personalized proposals. "
    "Structure: 1. Hook (Address pain point directly) 2. Solution (Specific tech & approach) "
    "3. Proof/Authority (Mention experience with similar projects) 4. CTA (Call to Action with timeline). "
    "Keep it under 150 words. Professional but punchy. No fluff."
)


# ═══════════════════════════════════════════════════════
# RSS FEED SCANNER — Real gig data
# ═══════════════════════════════════════════════════════

def _strip_html(raw: str) -> str:
    """Remove HTML tags from RSS content."""
    return re.sub(r"<[^>]+>", "", raw).strip()


async def fetch_rss_gigs(max_per_feed: int = 5) -> List[Dict[str, Any]]:
    """Fetch real gigs from RSS feeds. Returns empty list if no network."""
    if not HAS_AIOHTTP:
        print("  ⚠️  aiohttp not installed — skipping RSS feeds")
        return []

    gigs: List[Dict[str, Any]] = []
    timeout = aiohttp.ClientTimeout(total=15)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        for feed in RSS_FEEDS:
            try:
                print(f"  📡 Scanning: {feed['name']}...")
                async with session.get(feed["url"]) as resp:
                    if resp.status != 200:
                        print(f"     ⚠️  HTTP {resp.status} — skipped")
                        continue
                    body = await resp.text()

                # Parse RSS XML
                root = ET.fromstring(body)
                # Explicit list conversion to avoid type confusion
                all_items = list(root.findall(".//item"))
                items = all_items[:max_per_feed]

                for i, item in enumerate(items):
                    title_el = item.find("title")
                    desc_el = item.find("description")
                    link_el = item.find("link")
                    pub_el = item.find("pubDate")

                    title = title_el.text if title_el is not None and title_el.text else "Untitled"
                    desc = _strip_html(desc_el.text if desc_el is not None and desc_el.text else "")
                    link = link_el.text if link_el is not None and link_el.text else ""

                    # Try to extract budget from description
                    budget_match = re.search(r"\$[\d,]+(?:\s*[-–]\s*\$[\d,]+)?", desc)
                    budget = budget_match.group(0) if budget_match else "Not specified"

                    gig_id = f"rss_{feed['platform'].lower()}_{int(time.time())}_{i}"
                    gigs.append({
                        "id": gig_id,
                        "platform": feed["platform"],
                        "title": title[:120],
                        "description": desc[:500],
                        "budget": budget,
                        "client": "Potential Client",
                        "link": link,
                        "source": "RSS",
                        "fetched_at": datetime.now().isoformat(),
                    })

                print(f"     ✅ Found {len(items)} gigs")

            except asyncio.TimeoutError:
                print(f"     ⏰ Timeout — skipped")
            except ET.ParseError:
                print(f"     ⚠️  Invalid RSS XML — skipped")
            except Exception as e:
                print(f"     ❌ Error: {e}")

    return gigs


# ═══════════════════════════════════════════════════════
# CLI MANUAL ENTRY
# ═══════════════════════════════════════════════════════

def cli_add_gigs() -> List[Dict[str, Any]]:
    """Interactively add gigs via CLI."""
    gigs: List[Dict[str, Any]] = []
    print("\n⌨️  MANUAL GIG ENTRY — Type 'done' to finish\n")

    idx = 1
    while True:
        print(f"── Gig #{idx} ──")
        title = input("  Title: ").strip()
        if title.lower() in ("done", "exit", "q", ""):
            break
        desc = input("  Description: ").strip()
        budget = input("  Budget (e.g. $500): ").strip() or "Not specified"
        platform = input("  Platform [Upwork/Fiverr/Other]: ").strip() or "Upwork"

        gigs.append({
            "id": f"manual_{int(time.time())}_{idx}",
            "platform": platform,
            "title": title,
            "description": desc,
            "budget": budget,
            "client": "Potential Client",
            "source": "manual",
        })
        idx += 1
        print(f"  ✅ Added!\n")

    return gigs


# ═══════════════════════════════════════════════════════
# REVENUE BURST ENGINE
# ═══════════════════════════════════════════════════════

class RevenueBurst:
    def __init__(self, model: str = MODEL_SALES):
        self.model = model
        self.llm: Optional[Any] = None
        if HAS_OLLAMA and OllamaEngine is not None:
            self.llm = OllamaEngine(model=model)
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    async def generate_proposal(self, gig: Dict[str, Any]) -> str:
        """Generate a killer proposal for a specific gig."""
        if not self.llm:
            return self._template_proposal(gig)

        print(f"  ⚡ Generating proposal for: {gig['title'][:60]}...")

        prompt = (
            f"Write a proposal for this freelance gig:\n"
            f"Title: {gig['title']}\n"
            f"Description: {gig['description']}\n"
            f"Platform: {gig['platform']}\n"
            f"Budget: {gig['budget']}\n\n"
            f"Focus on the client's specific goal. Don't be generic. "
            f"Mention relevant tech (Python, n8n, AI/LLM, automation)."
        )

        try:
            resp = await self.llm.chat([
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ])
            return getattr(resp, "content", "") or self._template_proposal(gig)
        except Exception as e:
            print(f"  ⚠️  LLM failed ({e}), using template")
            return self._template_proposal(gig)

    def _template_proposal(self, gig: Dict[str, Any]) -> str:
        """Fallback: structured template when LLM isn't available."""
        return (
            f"Hi,\n\n"
            f"I noticed your project: \"{gig['title']}\" — this is exactly the kind of "
            f"AI automation work I specialize in.\n\n"
            f"I can deliver a production-ready solution using Python + AI/LLM integration, "
            f"fully tested and documented. My approach:\n\n"
            f"1. Quick discovery call (15 min) to nail down requirements\n"
            f"2. Working prototype within 3-5 days\n"
            f"3. Full delivery with documentation within 1-2 weeks\n\n"
            f"I've completed 50+ similar automation projects. Happy to share references.\n\n"
            f"Let's talk?\n"
            f"— Maurice | AI Automation Specialist"
        )

    async def run(self, gigs: List[Dict[str, Any]]):
        """Main pipeline: generate proposals for all gigs."""
        if not gigs:
            print("❌ No gigs to process. Try --manual or check your feeds.")
            return

        print(f"\n{'='*60}")
        print(f"💰  REVENUE BURST — {len(gigs)} Gigs Loaded")
        print(f"{'='*60}")
        print(f"  🤖 Model: {self.model}")
        print(f"  📁 Output: {OUTPUT_DIR}\n")

        for gig in gigs:
            await self._process_gig(gig)

        # Save gig index
        index_path = os.path.join(OUTPUT_DIR, "_gig_index.json")
        with open(index_path, "w") as f:
            json.dump({
                "generated_at": datetime.now().isoformat(),
                "total_gigs": len(gigs),
                "gigs": gigs,
            }, f, indent=2, ensure_ascii=False)

        print(f"\n{'='*60}")
        print(f"✅  DONE! {len(gigs)} proposals in '{OUTPUT_DIR}'")
        print(f"📋  Gig index: {index_path}")
        print(f"{'='*60}\n")

    async def _process_gig(self, gig: Dict[str, Any]):
        """Pipeline: Generate Proposal → Save File."""
        try:
            proposal = await self.generate_proposal(gig)
            self._save_draft(gig, proposal)
        except Exception as e:
            print(f"  ❌ Failed {gig.get('id', '?')}: {e}")

    def _save_draft(self, gig: Dict[str, Any], proposal: str):
        safe_title = re.sub(r"[^a-zA-Z0-9_-]", "_", gig["title"][:40])
        filename = f"{gig['platform']}_{gig['id']}_{safe_title}.md"
        filepath = os.path.join(OUTPUT_DIR, filename)

        link = gig.get("link", "[paste link here]")
        source = gig.get("source", "unknown")

        with open(filepath, "w") as f:
            f.write(f"# Proposal: {gig['title']}\n\n")
            f.write(f"| Field | Value |\n|---|---|\n")
            f.write(f"| Platform | {gig['platform']} |\n")
            f.write(f"| Budget | {gig['budget']} |\n")
            f.write(f"| Source | {source} |\n")
            f.write(f"| Link | {link} |\n")
            f.write(f"| Generated | {datetime.now().strftime('%Y-%m-%d %H:%M')} |\n\n")
            f.write(f"---\n\n")
            f.write(proposal)
            f.write(f"\n")

        print(f"  📝 Saved: {filename}")


# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════

async def main():
    mode = "auto"
    if "--manual" in sys.argv:
        mode = "manual"
    elif "--demo" in sys.argv:
        mode = "demo"

    burst = RevenueBurst()

    if mode == "manual":
        gigs = cli_add_gigs()
    elif mode == "demo":
        print("🎯 Demo mode — using seed gig data")
        gigs = SEED_GIGS
    else:
        # Auto: try RSS feeds first, fall back to seeds if empty
        print("📡 Scanning RSS feeds for real gigs...\n")
        gigs = await fetch_rss_gigs(max_per_feed=5)
        if not gigs:
            print("\n⚠️  No RSS gigs found. Using seed data as fallback.\n")
            gigs = SEED_GIGS

    await burst.run(gigs)


if __name__ == "__main__":
    asyncio.run(main())
