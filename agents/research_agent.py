import sys
import os
import asyncio
import json
from datetime import datetime
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_agent import BaseAgent
from ollama_engine import OllamaEngine, LLMResponse


SYSTEM_PROMPT = (
    "Du bist ein Research Agent. Analysiere Trends, Märkte und Technologien. "
    "Antworte IMMER als JSON: {\"topic\": \"...\", \"summary\": \"...\", \"key_facts\": [...], \"opportunities\": [...]}"
)

KNOWLEDGE_FILE = "knowledge_context.json"


class ResearchAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(agent_id="research-001", agent_type="research")
        self.llm = OllamaEngine(model="deepseek-r1:8b")

    def process_task(self, task: Dict[str, Any]) -> Any:
        query = task.get("prompt", "AI Trends 2026")
        self.logger.info(f"🔬 Researching: {query}")
        try:
            resp = asyncio.run(self.llm.chat([
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Recherchiere: {query}"},
            ]))
            assert isinstance(resp, LLMResponse)
            # Try JSON parse, fallback
            try:
                result = json.loads(resp.content)
            except json.JSONDecodeError:
                result = {"topic": query, "summary": resp.content, "key_facts": [], "opportunities": []}

            # Save to knowledge
            self._update_knowledge(result.get("topic", query), result)
            return result
        except Exception as e:
            self.logger.error(f"❌ LLM Error: {e}")
            return {"error": str(e)}

    def _update_knowledge(self, topic: str, data: Dict[str, Any]) -> None:
        try:
            ctx = {}
            if os.path.exists(KNOWLEDGE_FILE):
                with open(KNOWLEDGE_FILE, "r") as f:
                    ctx = json.load(f)
            ctx.setdefault("topics", {})[topic] = data
            ctx.setdefault("meta", {})["last_updated"] = datetime.now().isoformat()
            with open(KNOWLEDGE_FILE, "w") as f:
                json.dump(ctx, f, indent=2)
            self.logger.info(f"✅ Knowledge saved: {topic}")
        except Exception as e:
            self.logger.error(f"❌ Knowledge save failed: {e}")


if __name__ == "__main__":
    agent = ResearchAgent()
    agent.start()
