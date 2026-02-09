"""
💓 HEARTBEAT SCHEDULER — SYSTEM RHYTHM & AUTOMATION
Maurice's AI Empire

Handles:
- Rotating System Checks (Mail, Calendar, Tasks)
- Fixed-Time Cron Jobs (e.g., Daily Brief @ 08:30)
- System Health Monitoring

Usage:
    from heartbeat_scheduler import Heartbeat
    beat = Heartbeat(memory_system)
    beat.start()
"""
import time
import threading
import logging
from datetime import datetime
from typing import Callable, Dict, List, Any

logger = logging.getLogger("Heartbeat")

class Heartbeat:
    def __init__(self, memory_system):
        self.memory = memory_system
        self.running = False
        self.jobs: List[Dict] = []
        self.last_pulse = 0
        
        # Standard Schedules
        self.schedule_job("08:30", "daily_brief", self._run_daily_brief)
        self.schedule_job("18:00", "daily_review", self._run_daily_review)
        self.schedule_job("12:00", "competitor_check", self._run_competitor_check)

    def schedule_job(self, time_str: str, name: str, callback: Callable):
        """Schedule a job for a specific HH:MM time"""
        self.jobs.append({
            "time": time_str,
            "name": name,
            "callback": callback,
            "last_run": None
        })
        logger.info(f"⏰ Scheduled: {name} @ {time_str}")

    def start(self):
        """Start the heartbeat in a background thread"""
        self.running = True
        t = threading.Thread(target=self._loop, daemon=True)
        t.start()
        logger.info("💓 Heartbeat started.")

    def stop(self):
        self.running = False
        logger.info("💔 Heartbeat stopped.")

    def _loop(self):
        while self.running:
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            
            # check cron jobs
            for job in self.jobs:
                if job["time"] == current_time:
                    today_str = now.strftime("%Y-%m-%d")
                    if job["last_run"] != today_str:
                        logger.info(f"⚡ Triggering Cron: {job['name']}")
                        try:
                            job["callback"]()
                            job["last_run"] = today_str
                            self.memory.add_event("system", f"Executed cron: {job['name']}", 2)
                        except Exception as e:
                            logger.error(f"❌ Cron failed {job['name']}: {e}")

            # check pulse (every 5 min)
            if time.time() - self.last_pulse > 300:
                self._pulse_check()
                self.last_pulse = time.time()

            time.sleep(10) # check every 10s

    def _pulse_check(self):
        """Routine health check every 5 mins"""
        # Logic to check emails, files, system health would go here
        # For now, just logging presence
        pass

    # --- JOB CALLBACKS ---
    
    def _run_daily_brief(self):
        # TODO: Connect to Agent
        print("☀️ MORNING BRIEFING INITIATED")
        
    def _run_daily_review(self):
        self.memory.daily_review()
        
    def _run_competitor_check(self):
        # TODO: Connect to Research Agent
        print("🕵️ COMPETITOR CHECK INIT")

if __name__ == "__main__":
    # Test
    from memory_core import MemorySystem
    mem = MemorySystem()
    hb = Heartbeat(mem)
    hb.start()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        hb.stop()
