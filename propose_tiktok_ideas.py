#!/usr/bin/env python3
import asyncio
import logging
from youtube_automation import KimiScriptGenerator, VideoNiche

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("TikTokGen")

async def generate_proposals():
    print("🧠 Thinking up viral TikTok Mindset ideas...\n")
    
    kimi = KimiScriptGenerator()
    await kimi.init()
    
    # Custom prompt for TikTok specific structure
    # We override the generate_script method or just use it and rely on the Niche instructions reducing length?
    # The existing class produces long youtube scripts. We might need a small adjustment or just ask for SHORT scripts via topic.
    
    topics = [
        "The 1% Rule of Success",
        "Why You Stay Poor",
        "Stop Wasting Your 20s"
    ]
    
    for topic in topics:
        print(f"⏳ Generating: {topic}...")
        content = await kimi.generate_script(VideoNiche.MOTIVATION, topic)
        
        if content:
            print(f"\n{'='*40}")
            print(f"🎥 OPTION: {content.title}")
            print(f"{'='*40}")
            print(f"HOOK: {content.description[:100]}...")
            print(f"SCRIPT PREVIEW:\n{content.script[:300]}...")
            print(f"\nTAGS: {content.tags}")
            print("\n")
            
            # Save to file for review
            with open(f"mindset_content/proposal_{topic.replace(' ', '_')}.txt", "w") as f:
                f.write(f"TITLE: {content.title}\n")
                f.write(f"HOOK: {content.description}\n")
                f.write(f"SCRIPT:\n{content.script}\n")
        
        await asyncio.sleep(2)

    await kimi.close()
    print("✅ Proposals ready! Check the output above or the text files.")

if __name__ == "__main__":
    asyncio.run(generate_proposals())
