
import os
import json
import logging
import asyncio
import aiohttp
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class N8nConnector:
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url or os.getenv("N8N_WEBHOOK_URL", "https://ai1337empire.app.n8n.cloud/webhook/monster-machine")
        self.session = None

    async def init(self):
        self.session = aiohttp.ClientSession()

    async def close(self):
        if self.session:
            await self.session.close()

    async def send_data(self, data: Dict[str, Any], workflow_path: str = ""):
        """
        Send data to n8n webhook.
        :param data: JSON payload
        :param workflow_path: Optional path to append to base URL (e.g., 'new-content')
        """
        if not self.session:
            await self.init()

        url = f"{self.webhook_url}/{workflow_path}" if workflow_path else self.webhook_url
        
        try:
            async with self.session.post(url, json=data) as resp:
                if resp.status == 200:
                    logger.info(f"✅ Data sent to n8n: {url}")
                    return True
                else:
                    logger.error(f"❌ n8n Error {resp.status}: {await resp.text()}")
                    return False
        except Exception as e:
            logger.error(f"❌ n8n Connection Failed: {e}")
            return False

# Quick test
async def main():
    connector = N8nConnector()
    await connector.send_data({"message": "Hello from Monster Machine", "status": "booting"}, "log")
    await connector.close()

if __name__ == "__main__":
    asyncio.run(main())
