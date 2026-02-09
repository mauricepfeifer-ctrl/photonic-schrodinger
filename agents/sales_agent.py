import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_agent import BaseAgent
import logging
from typing import Dict, Any

class SalesAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="sales-001", agent_type="sales")
        
    def process_task(self, task: Dict[str, Any]) -> Any:
        self.logger.info(f"💰 Processing sales task: {task.get('prompt')}")
        
        # Logic to generate sales copy or emails
        prompt = task.get("prompt", "")
        
        email_copy = f"""
        Subject: Exclusive Opportunity
        
        Hey there,
        
        Regarding {prompt}... 
        
        Let's talk business.
        """
        
        return {"email_draft": email_copy, "crm_status": "draft_created"}

if __name__ == "__main__":
    agent = SalesAgent()
    agent.start()
