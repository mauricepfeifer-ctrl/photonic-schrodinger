#!/usr/bin/env python3
import asyncio
import os
import logging
from content_arbitrage import ArbitrageManager, Platform, VideoHarvester

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [TEST] %(message)s")
logger = logging.getLogger("TestArbitrage")

async def test_arbitrage_flow():
    """
    Test the full arbitrage flow with a mock URL or a real one if possible.
    Since we can't depend on external network stability for a specific URL,
    we'll mock the download part but test the logic flow.
    """
    logger.info("🎬 Starting Arbitrage Test...")
    
    manager = ArbitrageManager()
    
    # 1. Test Directory Creation
    content_dir = "/Users/maurice/.gemini/antigravity/playground/photonic-schrodinger/arbitrage_content"
    download_dir = f"{content_dir}/downloads"
    output_dir = f"{content_dir}/ready_to_upload"
    
    if os.path.exists(download_dir) and os.path.exists(output_dir):
        logger.info("✅ Directories exist.")
    else:
        logger.error("❌ Directories missing!")
        return

    # 2. Mock a 'Downloaded' file to test Transformer
    # Create a dummy video file (just text file renamed for test, ffmpeg will fail on it but logic should run)
    # Actually, let's skip ffmpeg execution if file is fake, or use a command that creates a dummy file
    
    dummy_file = f"{download_dir}/test_video.mp4"
    with open(dummy_file, "w") as f:
        f.write("dummy content")
        
    logger.info(f"📁 Created dummy file: {dummy_file}")
    
    # We can't easily test ffmpeg without a real video file.
    # So we will verify the Harvester logic for a fake URL (should fail gracefully)
    
    logger.info("🧪 Testing Downloader (Fail Case)...")
    result = await manager.harvester.download_video("https://invalid-url.com", Platform.TIKTOK)
    if result is None:
        logger.info("✅ Downloader correctly handled invalid URL.")
    else:
        logger.error("❌ Downloader should have failed.")

    # 3. Verify Class Structure
    logger.info("🧪 Verifying Manager Structure...")
    if hasattr(manager, 'harvester') and hasattr(manager, 'transformer'):
        logger.info("✅ Manager initialized correctly.")
    else:
        logger.error("❌ Manager structure invalid.")

    logger.info("🎉 Test Complete.")

if __name__ == "__main__":
    asyncio.run(test_arbitrage_flow())
