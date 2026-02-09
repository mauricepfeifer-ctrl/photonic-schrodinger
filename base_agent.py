import logging
import os
import json
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from redis_bus import RedisBus

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s")

class BaseAgent(ABC):
    """
    Base class for all AI Empire Agents.
    Handles Redis connection, heartbeat, and basic task consumption.
    """
    
    def __init__(self, agent_id: str, agent_type: str, bus=None):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.logger = logging.getLogger(f"Agent-{agent_type}")
        
        # Allow injection, otherwise default
        self.bus = bus if bus else RedisBus()
        self.running = False
        
    def start(self):
        """Start the agent loop"""
        self.logger.info(f"🚀 Agent {self.agent_id} starting...")
        if not self.bus.connect():
            self.logger.error("❌ Could not connect to message bus. Exiting.")
            return

        self.running = True
        
        # Subscribe to relevant channels
        self.bus.subscribe(f"tasks/{self.agent_type}", self.handle_task)
        self.bus.subscribe("system/shutdown", self.handle_shutdown)
        
        # Main loop
        while self.running:
            self.send_heartbeat()
            self.bus.listen_sync() # Processes messages
            time.sleep(1) # Heartbeat interval
            
    def send_heartbeat(self):
        """Send heartbeat to monitoring system"""
        self.bus.publish("system/heartbeat", {
            "agent_id": self.agent_id,
            "type": self.agent_type,
            "status": "active",
            "timestamp": time.time()
        })

    def handle_shutdown(self, message: Dict[str, Any]):
        """Handle shutdown signal"""
        self.logger.info("🛑 Received shutdown signal")
        self.running = False

    def handle_task(self, task: Dict[str, Any]):
        """Handle incoming task"""
        self.logger.info(f"📨 Received task: {task.get('task_id', 'unknown')}")
        try:
            result = self.process_task(task)
            self.bus.publish("tasks/completed", {
                "task_id": task.get("task_id"),
                "agent_id": self.agent_id,
                "result": result,
                "status": "success"
            })
        except Exception as e:
            self.logger.error(f"❌ Task failed: {e}")
            self.bus.publish("tasks/failed", {
                "task_id": task.get("task_id"),
                "agent_id": self.agent_id,
                "error": str(e),
                "status": "failed"
            })

    @abstractmethod
    def process_task(self, task: Dict[str, Any]) -> Any:
        """Process the actual task logic. Must be implemented by subclasses."""
        pass
