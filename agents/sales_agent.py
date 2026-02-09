import sys
import os
import asyncio
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_agent import BaseAgent
from ollama_engine import OllamaEngine, LLMResponse


SYSTEM_PROMPT = (
    "Du bist ein Top Sales Agent. Schreibe überzeugende, personalisierte "
    "Verkaufs-Emails und Outreach Messages für AI Automation Services. "
    "Kurz, freundlich, mit klarem CTA. Antworte auf Deutsch."
)


class SalesAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(agent_id="sales-001", agent_type="sales")
        self.llm = OllamaEngine(model="deepseek-r1:8b")

    def process_task(self, task: Dict[str, Any]) -> Any:
        prompt = task.get("prompt", "AI Automation Sprint anbieten")
        self.logger.info(f"💰 Sales task: {prompt}")
        try:
            resp = asyncio.run(self.llm.chat([
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Schreibe eine Verkaufs-Email für: {prompt}"},
            ]))
            assert isinstance(resp, LLMResponse)
            return {"email_draft": resp.content, "model": resp.model, "latency_ms": resp.latency_ms}
        except Exception as e:
            self.logger.error(f"❌ LLM Error: {e}")
            return {"error": str(e)}


if __name__ == "__main__":
    agent = SalesAgent()
    agent.start()
