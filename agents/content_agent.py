import sys
import os
import logging
import asyncio
import aiohttp
import json
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_agent import BaseAgent

# Config
KIMI_API_KEY = os.getenv("MOONSHOT_API_KEY", "sk-e57Q5aDfcpXpHkYfgeWCU3xjuqf2ZPoYxhuRH0kEZXGBeoMF")

class ContentAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="content-001", agent_type="content")
        
    def process_task(self, task: Dict[str, Any]) -> Any:
        self.logger.info(f"🎥 Generating content for task: {task.get('prompt')}")
        
        prompt = task.get("prompt", "")
        # Run async generation in a sync wrapper or change BaseAgent to async (BaseAgent is sync loop)
        # For simplicity in this loop, we'll use a sync approach or run_until_complete if BaseAgent allows.
        # However, BaseAgent calls this from a sync method. 
        # Best practice here: Use requests for sync or run async loop.
        
        # Since we want high perf, we should probably refactor BaseAgent to be async, 
        # but to keep "Integrate Fast" promise, I will use a helper to run the async Kimi call.
        
        try:
            return asyncio.run(self._generate_with_kimi(prompt))
        except Exception as e:
            self.logger.error(f"Failed to generate: {e}")
            return {"error": str(e)}

    async def _generate_with_kimi(self, prompt: str) -> Dict[str, Any]:
        """Call Kimi API"""
        async with aiohttp.ClientSession() as session:
            system_prompt = "You are an expert Content Creator (BMA & AI Niche). Create high-viral scripts."
            user_prompt = f"Create a short video script for: {prompt}. JSON Output: {{'title': '...', 'script': '...', 'hashtags': []}}"
            
            async with session.post(
                "https://api.moonshot.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {KIMI_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "moonshot-v1-8k",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.7
                }
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    content = data["choices"][0]["message"]["content"]
                    # Clean markdown
                    if "```json" in content:
                        content = content.split("```json")[1].split("```")[0]
                    elif "```" in content:
                        content = content.split("```")[1].split("```")[0]
                    return json.loads(content)
                else:
                    return {"error": f"Kimi API Error: {resp.status}"}

if __name__ == "__main__":
    agent = ContentAgent()
    agent.start()
