import sys
import os
import asyncio
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_agent import BaseAgent
from ollama_engine import OllamaEngine, LLMResponse


SYSTEM_PROMPT = (
    "Du bist ein viraler TikTok/Shorts Content Experte. "
    "Erstelle Hook + Script + CTA für maximale Views. "
    "Kurz, punchy, emotional. Max 60 Sekunden Sprechtext."
)


class TikTokAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(agent_id="tiktok-001", agent_type="tiktok")
        self.llm = OllamaEngine(model="glm-4.7-flash")

    def process_task(self, task: Dict[str, Any]) -> Any:
        prompt = task.get("prompt", "AI macht dich reich")
        self.logger.info(f"🎵 TikTok: {prompt}")
        try:
            resp = asyncio.run(self.llm.chat([
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Erstelle TikTok Script für: {prompt}"},
            ]))
            assert isinstance(resp, LLMResponse)
            return {
                "script": resp.content,
                "model": resp.model,
                "latency_ms": resp.latency_ms,
                "hashtags": ["#fyp", "#ai", "#viral", "#geldverdienen"],
            }
        except Exception as e:
            self.logger.error(f"❌ LLM Error: {e}")
            return {"error": str(e)}


if __name__ == "__main__":
    agent = TikTokAgent()
    agent.start()
