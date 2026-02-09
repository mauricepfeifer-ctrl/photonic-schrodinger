import sys
import os
import asyncio
import json
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_agent import BaseAgent
from ollama_engine import OllamaEngine, LLMResponse


SYSTEM_PROMPT = (
    "Du bist ein Elite Content Creator für AI & Tech Nischen. "
    "Erstelle virale Scripts für TikTok/YouTube Shorts/X Posts. "
    "Antworte IMMER als JSON: {\"title\": \"...\", \"script\": \"...\", \"hashtags\": [...]}"
)


class ContentAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(agent_id="content-001", agent_type="content")
        self.llm = OllamaEngine(model="glm-4.7-flash")

    def process_task(self, task: Dict[str, Any]) -> Any:
        prompt = task.get("prompt", "AI Automation")
        self.logger.info(f"🎥 Generating content: {prompt}")
        try:
            resp = asyncio.run(self.llm.chat([
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Erstelle virales Script für: {prompt}"},
            ]))
            assert isinstance(resp, LLMResponse)
            # Try to parse JSON, fallback to raw
            try:
                return json.loads(resp.content)
            except json.JSONDecodeError:
                return {"title": prompt, "script": resp.content, "hashtags": ["#AI", "#Viral"]}
        except Exception as e:
            self.logger.error(f"❌ LLM Error: {e}")
            return {"error": str(e)}


if __name__ == "__main__":
    agent = ContentAgent()
    agent.start()
