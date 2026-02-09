#!/usr/bin/env python3
"""
🔍 QA AGENT — Quality Assurance & Content Prüfer

Blueprint Role:
- Prüft JEDEN Output der anderen Agenten
- Cross-Validation: nimmt Output von Agent A, lässt Agent B prüfen
- Veto-Recht: Kann Content blocken wenn Qualität nicht stimmt
- Nutzt bewusst ANDERES Modell als Content Agent

Channels:
- Subscribes: content/draft, tasks/qa
- Publishes:  content/approved, content/rejected, tasks/completed
"""

import sys
import os
import asyncio
import json
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_agent import BaseAgent
from ollama_engine import OllamaEngine, LLMResponse


QA_SYSTEM_PROMPT = (
    "Du bist ein strenger Qualitätsprüfer für Content. "
    "Prüfe den folgenden Content auf:\n"
    "1. FAKTEN: Sind alle Aussagen korrekt?\n"
    "2. QUALITÄT: Ist der Text gut geschrieben, klar und überzeugend?\n"
    "3. BRAND: Passt der Ton zur Marke (professionell, kompetent, direkt)?\n"
    "4. COMPLIANCE: Keine irreführenden Versprechen, keine Rechtsverstöße?\n"
    "5. ENGAGEMENT: Würde dieser Content Aufmerksamkeit erzeugen?\n\n"
    "Antworte IMMER als JSON:\n"
    '{"approved": true/false, "score": 1-10, "issues": ["..."], "suggestions": ["..."]}'
)


class QAAgent(BaseAgent):
    """Quality Assurance Agent with cross-model validation."""

    def __init__(self) -> None:
        super().__init__(agent_id="qa-001", agent_type="qa")
        # Use DIFFERENT model than content agent (deepseek vs glm)
        self.llm = OllamaEngine(model="deepseek-r1:8b")
        self.min_score = 6  # Minimum score to approve
        self.reviewed = 0
        self.approved_count = 0
        self.rejected_count = 0

    def process_task(self, task: Dict[str, Any]) -> Any:
        """Review content from another agent."""
        content = task.get("content") or task.get("prompt", "")
        source_agent = task.get("source_agent", "unknown")
        content_type = task.get("content_type", "general")

        self.logger.info(f"🔍 Reviewing {content_type} from {source_agent}")
        self.reviewed += 1

        try:
            review_prompt = (
                f"Review diesen {content_type} Content:\n\n"
                f"---\n{content}\n---\n\n"
                f"Quelle: Agent '{source_agent}'\n"
                f"Bewerte nach den 5 Kriterien."
            )

            resp = asyncio.run(self.llm.chat([
                {"role": "system", "content": QA_SYSTEM_PROMPT},
                {"role": "user", "content": review_prompt},
            ]))
            assert isinstance(resp, LLMResponse)

            # Parse response
            try:
                result = json.loads(resp.content)
            except json.JSONDecodeError:
                # If LLM didn't return JSON, try to extract verdict
                approved = "approved" in resp.content.lower() or "✅" in resp.content
                result = {
                    "approved": approved,
                    "score": 7 if approved else 4,
                    "issues": [],
                    "suggestions": [resp.content[:200]],
                }

            # Apply decision
            score = result.get("score", 5)
            approved = result.get("approved", score >= self.min_score)

            if approved and score >= self.min_score:
                self.approved_count += 1
                self.logger.info(f"  ✅ APPROVED (Score: {score}/10)")

                # Publish approved content
                if self.bus:
                    self.bus.publish("content/approved", {
                        "content": content,
                        "source_agent": source_agent,
                        "qa_score": score,
                        "qa_agent": self.agent_id,
                    })
            else:
                self.rejected_count += 1
                self.logger.info(f"  ❌ REJECTED (Score: {score}/10)")
                self.logger.info(f"  Issues: {result.get('issues', [])}")

                if self.bus:
                    self.bus.publish("content/rejected", {
                        "content": content,
                        "source_agent": source_agent,
                        "qa_score": score,
                        "issues": result.get("issues", []),
                        "suggestions": result.get("suggestions", []),
                    })

            result["reviewed_total"] = self.reviewed
            result["approval_rate"] = (
                f"{self.approved_count}/{self.reviewed}"
                f" ({100 * self.approved_count / max(1, self.reviewed):.0f}%)"
            )
            return result

        except Exception as e:
            self.logger.error(f"❌ QA Review failed: {e}")
            return {"error": str(e), "approved": True, "score": 0, "fallback": True}

    def start(self) -> None:
        """Override start to also subscribe to content/draft channel."""
        self.logger.info(f"🚀 QA Agent {self.agent_id} starting...")
        if not self.bus.connect():
            self.logger.error("❌ Could not connect to message bus. Exiting.")
            return

        self.running = True

        # Subscribe to QA-specific channels
        self.bus.subscribe(f"tasks/{self.agent_type}", self.handle_task)
        self.bus.subscribe("content/draft", self._handle_draft)
        self.bus.subscribe("system/shutdown", self.handle_shutdown)

        import time
        while self.running:
            self.send_heartbeat()
            self.bus.listen_sync()
            time.sleep(1)

    def _handle_draft(self, message: Dict[str, Any]) -> None:
        """Auto-review content drafts."""
        self.logger.info("📨 Auto-reviewing content draft")
        task = {
            "task_id": f"qa-auto-{self.reviewed}",
            "content": message.get("content", message.get("script", "")),
            "source_agent": message.get("agent_id", "unknown"),
            "content_type": "draft",
        }
        self.handle_task(task)


if __name__ == "__main__":
    agent = QAAgent()
    agent.start()
