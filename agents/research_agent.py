import sys
import os
import logging
import json
from typing import Dict, Any
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_agent import BaseAgent

class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="research-001", agent_type="research")
        self.knowledge_file = "knowledge_context.json"
        
    def process_task(self, task: Dict[str, Any]) -> Any:
        query = task.get("prompt", "")
        self.logger.info(f"🔬 Researching: {query}")
        
        # In a real scenario, this would trigger Scrapy/Perplexity/Tavily.
        # For now, we simulate finding the data the user just provided.
        
        # Save found knowledge
        if "market" in query.lower() or "surveillance" in query.lower():
            result = {
                "topic": "AI Video Surveillance Market",
                "summary": "AI Video Surveillance: 6.5B -> 28.76B USD by 2030 (CAGR 30.6%). Less than 5% of 90M cameras use true AI.",
                "sources": ["NYU Tandon", "Markets&Markets"],
                "timestamp": datetime.now().isoformat()
            }
            self._update_knowledge("AI_Video_Surveillance", result)
            return result
            
        return {"error": "No data found"}

    def _update_knowledge(self, topic: str, data: Dict[str, Any]):
        """Update the central knowledge context."""
        try:
            if os.path.exists(self.knowledge_file):
                with open(self.knowledge_file, 'r') as f:
                    context = json.load(f)
            else:
                context = {"topics": {}}
                
            context["topics"][topic] = data
            context["meta"] = context.get("meta", {})
            context["meta"]["last_updated"] = datetime.now().isoformat()
            
            with open(self.knowledge_file, 'w') as f:
                json.dump(context, f, indent=2)
                
            self.logger.info(f"✅ Knowledge updated: {topic}")
        except Exception as e:
            self.logger.error(f"❌ Failed to update knowledge: {e}")

if __name__ == "__main__":
    agent = ResearchAgent()
    # Seed initial data provided by user
    seed_data = {
        "topic": "AI Video Surveillance Market", 
        "summary": "AI Video Surveillance: 6.5B -> 28.76B USD by 2030 (CAGR 30.6%). Key Players: Pano AI, A.I. Tech, Visionify. Trends: Edge AI, Behavioral Analytics. Killer Fact: <5% of 90M cameras use AI.",
        "sources": ["User Research"],
        "timestamp": datetime.now().isoformat()
    }
    agent._update_knowledge("AI_Video_Surveillance", seed_data)
    agent.start()
