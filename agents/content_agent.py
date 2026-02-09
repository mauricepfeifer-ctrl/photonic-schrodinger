import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_agent import BaseAgent
import logging
from typing import Dict, Any

class ContentAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="content-001", agent_type="content")
        
    def process_task(self, task: Dict[str, Any]) -> Any:
        self.logger.info(f"🎥 Generating content for task: {task.get('prompt')}")
        
        # Here we would call Ollama/Kimi to generate the actual script
        # For now, we simulate the output
        prompt = task.get("prompt", "")
        
        script = f"""
        # TikTok Script based on: {prompt}
        
        [Hook]
        Wait! Stop right there. This is how you win.
        
        [Body]
        Details about {prompt}...
        
        [CTA]
        Follow for more!
        """
        
        return {"script": script, "hashtags": ["#AI", "#Automation", "#Money"]}

if __name__ == "__main__":
    agent = ContentAgent()
    agent.start()
