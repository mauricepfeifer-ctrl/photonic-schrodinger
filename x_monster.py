
import os
import json
import logging
import asyncio
import aiohttp
from datetime import datetime
from typing import List, Dict
import random

# Import our new modules
from n8n_connector import N8nConnector

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Config
KIMI_API_KEY = os.getenv("MOONSHOT_API_KEY", "sk-e57Q5aDfcpXpHkYfgeWCU3xjuqf2ZPoYxhuRH0kEZXGBeoMF")
KNOWLEDGE_FILE = "knowledge_context.json"
OUTPUT_DIR = "x_content"

class XMonsterEngine:
    """
    The Monster Machine's Voice.
    Generates high-frequency, high-quality X threads based on harvested knowledge.
    """
    def __init__(self):
        self.knowledge = {}
        self.n8n = N8nConnector()
        self.load_knowledge()
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def load_knowledge(self):
        if os.path.exists(KNOWLEDGE_FILE):
            with open(KNOWLEDGE_FILE, "r") as f:
                self.knowledge = json.load(f)
        else:
            logger.warning("⚠️ No knowledge file found. Running in blind mode.")

    async def generate_thread(self, topic: str, mode: str = "viral") -> Dict:
        """Use Kimi to write a thread."""
        logger.info(f"🧠 Generating {mode} thread about {topic}...")
        
        context = ""
        if topic in self.knowledge.get("topics", {}):
            context = f"CONTEXT: {self.knowledge['topics'][topic]['summary']}"
            
        prompts = {
            "viral": "Write a viral 5-tweet thread. Hook in first tweet. Short sentences. Punchy. No hashtags.",
            "shitpost": "Write a funny/sarcastic single tweet about this. Tech humor. Gen Z style.",
            "education": "Write a 3-tweet educational thread. Clear, concise, actionable.",
            "monster": "Write as the 'Monster Machine'. Aggressive, dominant, AI supremacy vibes. 1 tweet."
        }
        
        system_prompt = "You are a top-tier X (Twitter) ghostwriter. You understand engagement algorithms."
        user_prompt = f"""
        {prompts.get(mode, prompts['viral'])}
        
        TOPIC: {topic}
        {context}
        
        Output format: JSON with key 'tweets' (list of strings).
        """
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    "https://api.moonshot.ai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {KIMI_API_KEY}", "Content-Type": "application/json"},
                    json={
                        "model": "moonshot-v1-8k",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.8
                    }
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        content = data["choices"][0]["message"]["content"]
                        # Clean markdown
                        if "```json" in content:
                            content = content.split("```json")[1].split("```")[0]
                        
                        try:
                            result = json.loads(content)
                            return result
                        except:
                            return {"tweets": [content]} # Fallback
                    else:
                        logger.error(f"Kimi Error: {await resp.text()}")
                        return None
            except Exception as e:
                logger.error(f"Request failed: {e}")
                return None

    async def run_cycle(self):
        """Run a generation cycle."""
        topics = list(self.knowledge.get("topics", {}).keys()) or ["AI", "Future_Tech"]
        modes = ["viral", "education", "monster"]
        
        target_topic = random.choice(topics)
        target_mode = random.choice(modes)
        
        result = await self.generate_thread(target_topic, target_mode)
        
        if result:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{OUTPUT_DIR}/{timestamp}_{target_topic}.json"
            
            # Save locally
            with open(filename, "w") as f:
                json.dump(result, f, indent=2)
            
            logger.info(f"✅ Content created: {filename}")
            
            # Send to n8n
            await self.n8n.send_data({
                "type": "x_content",
                "topic": target_topic,
                "mode": target_mode,
                "tweets": result.get("tweets", []),
                "generated_at": timestamp
            }, "content-created")
            
        else:
            logger.warning("❌ Failed to generate content.")

async def main():
    engine = XMonsterEngine()
    # Run one immediate cycle
    await engine.run_cycle()
    await engine.n8n.close()

if __name__ == "__main__":
    asyncio.run(main())
