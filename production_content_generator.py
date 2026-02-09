#!/usr/bin/env python3
import json
import os
import sys
import glob
import asyncio
from datetime import datetime

# Import Kimi Engine
try:
    from youtube_automation import KimiScriptGenerator, VideoNiche, VideoContent
except ImportError:
    print("❌ Error: youtube_automation.py not found.")
    sys.exit(1)

SWARM_OUTPUT_DIR = "swarm_output"
CANDIDATE_DIR = os.path.join(SWARM_OUTPUT_DIR, "candidate_ideas")
FINAL_CONTENT_DIR = os.path.join(SWARM_OUTPUT_DIR, "final_content")

os.makedirs(FINAL_CONTENT_DIR, exist_ok=True)

async def process_candidates():
    print("========================================")
    print("🧠 KIMI 2.5: CONTENT FACTORY")
    print("========================================")

    # 1. Find latest batch
    files = glob.glob(os.path.join(CANDIDATE_DIR, "batch_*.json"))
    if not files:
        print("📭 No candidate batches found. Run the Go Swarm first!")
        return

    latest_file = max(files, key=os.path.getctime)
    print(f"📂 Processing: {os.path.basename(latest_file)}")

    with open(latest_file, 'r') as f:
        candidates = json.load(f)

    if not candidates:
        print("⚠️ No candidates in file.")
        return

    # 2. Sort by Viral Score and Pick Top 3
    candidates.sort(key=lambda x: x.get('ViralScore', 0), reverse=True)
    top_picks = candidates[:3]

    print(f"💎 Selected Top {len(top_picks)} candidates from {len(candidates)} raw ideas.")

    # 3. Initialize AI
    kimi = KimiScriptGenerator()
    await kimi.init()

    # 4. Generate Content
    for i, idea in enumerate(top_picks):
        topic = idea.get('Topic')
        niche_str = idea.get('Niche')
        score = idea.get('ViralScore')

        print(f"\n[{i+1}/{len(top_picks)}] Generatring: {topic} (Score: {score:.2f})")
        
        # Map niche string to Enum if possible, else default
        niche_enum = VideoNiche.MOTIVATION # Default
        if "Money" in niche_str: niche_enum = VideoNiche.FINANCE
        elif "AI" in niche_str: niche_enum = VideoNiche.AI_NEWS
        elif "Psychology" in niche_str: niche_enum = VideoNiche.MOTIVATION
        elif "History" in niche_str: niche_enum = VideoNiche.CRIME_DOCS

        content = await kimi.generate_script(niche_enum, topic)

        if content:
            # Save Final Content
            safe_title = "".join([c for c in content.title if c.isalnum() or c in (' ', '-', '_')]).strip().replace(' ', '_')
            filename = f"{FINAL_CONTENT_DIR}/{safe_title}.txt"
            
            with open(filename, 'w') as f:
                f.write(f"TITLE: {content.title}\n")
                f.write(f"NICHE: {niche_str}\n")
                f.write(f"VIRAL SCORE: {score:.4f}\n")
                f.write(f"GENERATED: {datetime.now()}\n")
                f.write("="*40 + "\n")
                f.write(f"HOOK: {content.description}\n")
                f.write("="*40 + "\n")
                f.write(f"SCRIPT:\n{content.script}\n")
                f.write("="*40 + "\n")
                f.write(f"TAGS: {', '.join(content.tags)}\n")
            
            print(f"✅ Saved: {filename}")
        
        await asyncio.sleep(2)

    await kimi.close()
    print("\n🎉 Production Run Complete!")

if __name__ == "__main__":
    asyncio.run(process_candidates())
