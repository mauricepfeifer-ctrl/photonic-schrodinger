#!/usr/bin/env python3
"""
⚡ CONTENT BLITZ — MASSIVE CONTENT GENERATION ENGINE
Maurice's AI Empire

Generates high-volume, high-quality content for:
- TikTok / Reels (Viral Scripts)
- LinkedIn (Thought Leadership)
- X / Twitter (Threads)
- Blog (SEO Articles)

Usage:
    python content_blitz.py --count 5
"""
import argparse
import asyncio
import logging
import os
import time
from datetime import datetime

# Setup Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ContentBlitz")

OUTPUT_DIR = "content_output"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Import SalesForce to reuse the AI Engine
try:
    from sales_force import SalesForce
except ImportError:
    print("❌ Error: sales_force.py not found. Please run sales_force.py first.")
    exit(1)

TOPICS = [
    "Wie AI Agents deinen Job retten (nicht killen)",
    "3 Tools die ich nutze um 20h/Woche zu sparen",
    "Warum ChatGPT out ist (und was du stattdessen nutzen solltest)",
    "Anleitung: Dein erster AI Mitarbeiter in 10 Minuten",
    "Case Study: €5000 Umsatz mit einem einzigen Prompt",
    "Die Wahrheit über 'Passive Income' mit AI",
]

class ContentBlitz:
    def __init__(self, dry_run=False):
        self.sf = SalesForce(dry_run=dry_run)
    
    async def generate_tiktok(self, topic):
        prompt = f"Erstelle ein virales TikTok Skript (max 60 sek) zum Thema: '{topic}'. Nutze einen starken Hook am Anfang. Format: Sprecher-Text und Visuelle Anweisungen."
        return await self.sf.run_agent("content_sniper", prompt)

    async def generate_linkedin(self, topic):
        prompt = f"Schreibe einen LinkedIn Post über '{topic}'. Stil: Professionell aber persönlich. Nutze Bullet Points und eine klare Call to Action. Keine Hashtag-Wüste."
        return await self.sf.run_agent("seo_hunter", prompt) # Reusing SEO hunter for long-form text

    async def generate_twitter(self, topic):
        prompt = f"Erstelle einen X (Twitter) Thread (5 Tweets) über '{topic}'. Der erste Tweet muss ein unwiderstehlicher Hook sein."
        return await self.sf.run_agent("social_striker", prompt)

    async def run_blitz(self, count=3):
        logger.info(f"⚡ STARTING CONTENT BLITZ (Target: {count} pieces per platform)...")
        
        tasks = []
        for i in range(count):
            topic = TOPICS[i % len(TOPICS)]
            logger.info(f"🎨 Generating content for: {topic}")
            
            tasks.append(self.generate_tiktok(topic))
            tasks.append(self.generate_linkedin(topic))
            tasks.append(self.generate_twitter(topic))
        
        results = await asyncio.gather(*tasks)
        logger.info(f"✅ BLITZ COMPLETE. Generated {len(results)} content pieces in '{OUTPUT_DIR}'")

def main():
    parser = argparse.ArgumentParser(description="Content Blitz Machine")
    parser.add_argument("--count", type=int, default=3, help="Number of content pieces per platform")
    parser.add_argument("--dry-run", action="store_true", help="Simulate AI calls")
    args = parser.parse_args()
    
    blitz = ContentBlitz(dry_run=args.dry_run)
    asyncio.run(blitz.run_blitz(count=args.count))

if __name__ == "__main__":
    main()
