#!/usr/bin/env python3
"""
TIKTOK MINDSET BOT
Maurice's AI Empire

Automates the technical side of running a "Mindset/Motivation" theme page.
1. Reads URLs from mindset_urls.txt
2. Downloads video (Clean, no watermark) using content_arbitrage logic
3. Remixes video (Speed up, safe metadata)
4. Saves to mindset_content/ready_to_upload
"""

import asyncio
import os
import logging
import sys
from datetime import datetime

# Import existing tools
try:
    from content_arbitrage import VideoHarvester, ContentTransformer, Platform, ViralClip
except ImportError:
    print("❌ Error: content_arbitrage.py not found. Please make sure it is in the same directory.")
    sys.exit(1)

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
URLS_FILE = os.path.join(BASE_DIR, "mindset_urls.txt")
CONTENT_DIR = os.path.join(BASE_DIR, "mindset_content")
DOWNLOAD_DIR = os.path.join(CONTENT_DIR, "downloads")
UPLOAD_DIR = os.path.join(CONTENT_DIR, "ready_to_upload")

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [MINDSET] %(message)s")
logger = logging.getLogger("MindsetBot")

# Ensure directories
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Patching paths in content_arbitrage classes if needed or just using them
# content_arbitrage uses global vars for paths, so we might need to handle file movement manually
# or just accept they go to the arbitrage folder and we move them.
# Better: Let's subclass or just use them and move files after.

class MindsetBot:
    def __init__(self):
        self.harvester = VideoHarvester()
        self.transformer = ContentTransformer()
        # Override output dir for transformer if possible, or just move file later
        # content_arbitrage.OUTPUT_DIR is global. We will move files after processing.

    def load_urls(self):
        if not os.path.exists(URLS_FILE):
            logger.error(f"❌ File not found: {URLS_FILE}")
            return []
        
        with open(URLS_FILE, "r") as f:
            lines = f.readlines()
        
        urls = [line.strip() for line in lines if line.strip() and not line.startswith("#")]
        return urls

    def detect_platform(self, url):
        if "tiktok.com" in url:
            return Platform.TIKTOK
        elif "youtube.com" in url or "youtu.be" in url:
            return Platform.YOUTUBE
        elif "instagram.com" in url:
            return Platform.INSTAGRAM
        else:
            return Platform.TIKTOK # Default fallback

    async def process_batch(self):
        urls = self.load_urls()
        if not urls:
            logger.info("📭 No URLs found in mindset_urls.txt")
            return

        logger.info(f"🚀 Found {len(urls)} videos to process...")

        for i, url in enumerate(urls):
            logger.info(f"▶️  Processing {i+1}/{len(urls)}: {url}")
            platform = self.detect_platform(url)
            
            # 1. Download
            clip = await self.harvester.download_video(url, platform)
            if not clip or not clip.local_path:
                logger.error(f"❌ Failed to download: {url}")
                continue

            # 2. Transform (Remix)
            # transformation saves to content_arbitrage output dir by default
            # We will use the transformer, then move the result to our mindset folder
            processed_clip = await self.transformer.transform_clip(clip)
            
            if processed_clip and processed_clip.processed_path:
                # Move to our specific output folder
                filename = os.path.basename(processed_clip.processed_path)
                final_path = os.path.join(UPLOAD_DIR, filename)
                os.rename(processed_clip.processed_path, final_path)
                
                logger.info(f"✅ Ready for Upload: {final_path}")
                
                # Create a simple metadata text file for the user
                meta_file = final_path + ".txt"
                with open(meta_file, "w") as f:
                    f.write(f"Source: {url}\n")
                    f.write(f"Original Title: {clip.title}\n")
                    f.write(f"Processed: {datetime.now()}\n")
                    f.write(f"Niche: Mindset/Motivation\n")
                    f.write("\nSuggested Hashtags:\n#mindset #motivation #success #hustle #wealth\n")
            
            logger.info("-------------")
            await asyncio.sleep(2) # Politeness delay

        logger.info("🎉 Batch processing complete!")

if __name__ == "__main__":
    bot = MindsetBot()
    asyncio.run(bot.process_batch())
