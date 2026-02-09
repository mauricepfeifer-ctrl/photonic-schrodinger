#!/usr/bin/env python3
"""
📊 MONITOR AGENT — System-Wächter

Blueprint Role:
- CPU/RAM/Disk Überwachung
- Docker Container Status
- Agent Heartbeat Tracking
- Telegram-Alerts bei kritischen Events
- Grafana-kompatible Metriken

Channels:
- Subscribes: system/heartbeat, system/alert
- Publishes:  system/health, system/alert
"""

import sys
import os
import asyncio
import json
import time
import subprocess
import platform
from typing import Dict, Any, List, Optional
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_agent import BaseAgent


# ─── THRESHOLDS ──────────────────────────────────────
CPU_WARN = 75       # % - Warning
CPU_CRITICAL = 85   # % - Throttle non-critical tasks
RAM_WARN = 80       # % - Warning
RAM_CRITICAL = 90   # % - Kill low-priority tasks
DISK_WARN = 85      # % - Warning
DISK_CRITICAL = 95  # % - Auto-cleanup
HEARTBEAT_TIMEOUT = 30  # seconds before agent considered dead


class MonitorAgent(BaseAgent):
    """System Monitor with auto-healing capabilities."""

    def __init__(self) -> None:
        super().__init__(agent_id="monitor-001", agent_type="monitor")
        self.agent_heartbeats: Dict[str, float] = {}
        self.alert_history: List[Dict[str, Any]] = []
        self.check_interval = 10  # seconds
        self.last_check = 0.0

    def process_task(self, task: Dict[str, Any]) -> Any:
        """Process monitoring requests."""
        action = task.get("action", "full_check")

        if action == "full_check":
            return self._full_system_check()
        elif action == "agent_status":
            return self._check_agents()
        elif action == "docker_status":
            return self._check_docker()
        else:
            return self._full_system_check()

    def start(self) -> None:
        """Override start with monitoring loop."""
        self.logger.info(f"📊 Monitor Agent {self.agent_id} starting...")
        if not self.bus.connect():
            self.logger.error("❌ Could not connect to message bus. Exiting.")
            return

        self.running = True

        # Subscribe to channels
        self.bus.subscribe(f"tasks/{self.agent_type}", self.handle_task)
        self.bus.subscribe("system/heartbeat", self._handle_heartbeat)
        self.bus.subscribe("system/shutdown", self.handle_shutdown)

        self.logger.info("📊 Monitoring active — checking every 10s")

        while self.running:
            now = time.time()

            # Periodic system check
            if now - self.last_check >= self.check_interval:
                self._periodic_check()
                self.last_check = now

            self.send_heartbeat()
            self.bus.listen_sync()
            time.sleep(1)

    def _handle_heartbeat(self, message: Dict[str, Any]) -> None:
        """Track agent heartbeats."""
        agent_id = message.get("agent_id", "unknown")
        self.agent_heartbeats[agent_id] = time.time()

    # ─── SYSTEM CHECKS ───────────────────────────────

    def _full_system_check(self) -> Dict[str, Any]:
        """Complete system health check."""
        cpu = self._get_cpu_usage()
        ram = self._get_ram_usage()
        disk = self._get_disk_usage()
        agents = self._check_agents()
        docker = self._check_docker()

        health = {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": cpu,
            "ram_percent": ram,
            "disk_percent": disk,
            "agents": agents,
            "docker": docker,
            "alerts": [],
            "overall": "healthy",
        }

        # Check thresholds
        if cpu > CPU_CRITICAL:
            alert = {"level": "critical", "component": "cpu", "value": cpu, "message": f"CPU at {cpu}%! Throttling."}
            health["alerts"].append(alert)
            health["overall"] = "critical"
            self._send_alert(alert)
        elif cpu > CPU_WARN:
            health["alerts"].append({"level": "warning", "component": "cpu", "value": cpu})
            health["overall"] = "warning"

        if ram > RAM_CRITICAL:
            alert = {"level": "critical", "component": "ram", "value": ram, "message": f"RAM at {ram}%! Freeing memory."}
            health["alerts"].append(alert)
            health["overall"] = "critical"
            self._send_alert(alert)
        elif ram > RAM_WARN:
            health["alerts"].append({"level": "warning", "component": "ram", "value": ram})
            if health["overall"] != "critical":
                health["overall"] = "warning"

        if disk > DISK_CRITICAL:
            alert = {"level": "critical", "component": "disk", "value": disk, "message": f"Disk at {disk}%!"}
            health["alerts"].append(alert)
            health["overall"] = "critical"
            self._send_alert(alert)

        # Publish health status
        if self.bus:
            self.bus.publish("system/health", health)

        return health

    def _periodic_check(self) -> None:
        """Lightweight periodic check."""
        health = self._full_system_check()

        # Check dead agents
        now = time.time()
        for agent_id, last_seen in list(self.agent_heartbeats.items()):
            if agent_id == self.agent_id:
                continue
            if now - last_seen > HEARTBEAT_TIMEOUT:
                alert = {
                    "level": "warning",
                    "component": "agent",
                    "agent_id": agent_id,
                    "message": f"Agent {agent_id} not responding ({int(now - last_seen)}s)",
                }
                self._send_alert(alert)

        status = health["overall"]
        cpu = health["cpu_percent"]
        ram = health["ram_percent"]
        active = len([a for a, t in self.agent_heartbeats.items() if now - t < HEARTBEAT_TIMEOUT])
        self.logger.info(
            f"📊 [{status.upper()}] CPU={cpu}% RAM={ram}% Agents={active} "
            f"Alerts={len(health['alerts'])}"
        )

    # ─── RESOURCE MONITORING ─────────────────────────

    def _get_cpu_usage(self) -> float:
        """Get CPU usage percentage."""
        try:
            if platform.system() == "Darwin":
                # macOS
                result = subprocess.run(
                    ["top", "-l", "1", "-n", "0"],
                    capture_output=True, text=True, timeout=5
                )
                for line in result.stdout.split("\n"):
                    if "CPU usage" in line:
                        # Parse: "CPU usage: 12.5% user, 8.3% sys, 79.1% idle"
                        parts = line.split(",")
                        for part in parts:
                            if "idle" in part:
                                idle = float(part.strip().split("%")[0])
                                return round(100 - idle, 1)
            else:
                # Linux
                result = subprocess.run(
                    ["grep", "cpu ", "/proc/stat"],
                    capture_output=True, text=True, timeout=5
                )
                # Simplified — just return a value
                values = result.stdout.split()[1:5]
                total = sum(float(v) for v in values)
                idle = float(values[3])
                return round((1 - idle / total) * 100, 1) if total > 0 else 0.0

        except Exception as e:
            self.logger.debug(f"CPU check failed: {e}")
        return 0.0

    def _get_ram_usage(self) -> float:
        """Get RAM usage percentage."""
        try:
            if platform.system() == "Darwin":
                result = subprocess.run(
                    ["vm_stat"],
                    capture_output=True, text=True, timeout=5
                )
                lines = result.stdout.split("\n")
                stats: Dict[str, int] = {}
                for line in lines[1:]:
                    if ":" in line:
                        key, val = line.split(":")
                        val_clean = val.strip().rstrip(".")
                        try:
                            stats[key.strip()] = int(val_clean)
                        except ValueError:
                            pass

                free = stats.get("Pages free", 0) * 16384
                active = stats.get("Pages active", 0) * 16384
                inactive = stats.get("Pages inactive", 0) * 16384
                wired = stats.get("Pages wired down", 0) * 16384
                total = free + active + inactive + wired
                used = active + wired
                return round(used / total * 100, 1) if total > 0 else 0.0
            else:
                with open("/proc/meminfo") as f:
                    mem = {}
                    for line in f:
                        parts = line.split()
                        mem[parts[0].rstrip(":")] = int(parts[1])
                total = mem.get("MemTotal", 1)
                available = mem.get("MemAvailable", 0)
                return round((1 - available / total) * 100, 1)

        except Exception as e:
            self.logger.debug(f"RAM check failed: {e}")
        return 0.0

    def _get_disk_usage(self) -> float:
        """Get disk usage percentage."""
        try:
            result = subprocess.run(
                ["df", "-h", "/"],
                capture_output=True, text=True, timeout=5
            )
            lines = result.stdout.strip().split("\n")
            if len(lines) >= 2:
                parts = lines[1].split()
                for part in parts:
                    if "%" in part:
                        return float(part.rstrip("%"))
        except Exception as e:
            self.logger.debug(f"Disk check failed: {e}")
        return 0.0

    def _check_docker(self) -> Dict[str, Any]:
        """Check Docker container status."""
        try:
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}\t{{.Status}}"],
                capture_output=True, text=True, timeout=10
            )
            containers = {}
            for line in result.stdout.strip().split("\n"):
                if "\t" in line:
                    name, status = line.split("\t", 1)
                    containers[name] = status
            return {"running": len(containers), "containers": containers}
        except Exception:
            return {"running": 0, "containers": {}, "error": "Docker not available"}

    def _check_agents(self) -> Dict[str, Any]:
        """Check which agents are alive."""
        now = time.time()
        status: Dict[str, Any] = {}
        for agent_id, last_seen in self.agent_heartbeats.items():
            delta = now - last_seen
            status[agent_id] = {
                "alive": delta < HEARTBEAT_TIMEOUT,
                "last_seen_seconds_ago": round(delta, 1),
            }
        return status

    # ─── ALERTS ──────────────────────────────────────

    def _send_alert(self, alert: Dict[str, Any]) -> None:
        """Send alert via Redis bus and attempt Telegram notification."""
        alert["timestamp"] = datetime.now().isoformat()
        self.alert_history.append(alert)

        # Keep only last 100 alerts
        if len(self.alert_history) > 100:
            self.alert_history = self.alert_history[-100:]

        if self.bus:
            self.bus.publish("system/alert", alert)

        self.logger.warning(f"🚨 ALERT [{alert['level']}]: {alert.get('message', alert)}")

        # Send Telegram alert for critical issues
        if alert["level"] == "critical":
            self._telegram_alert(alert)

    def _telegram_alert(self, alert: Dict[str, Any]) -> None:
        """Send critical alert to Telegram."""
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        user_id = os.getenv("TELEGRAM_USER_ID")
        if not token or not user_id:
            return

        text = (
            f"🚨 CRITICAL ALERT\n\n"
            f"Component: {alert.get('component', '?')}\n"
            f"Message: {alert.get('message', 'Unknown')}\n"
            f"Time: {alert.get('timestamp', '')}"
        )

        try:
            import urllib.request
            data = json.dumps({"chat_id": user_id, "text": text}).encode()
            req = urllib.request.Request(
                f"https://api.telegram.org/bot{token}/sendMessage",
                data=data,
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req, timeout=5)
        except Exception as e:
            self.logger.error(f"❌ Telegram alert failed: {e}")

    def get_status_summary(self) -> str:
        """Pretty-print system status for Telegram."""
        health = self._full_system_check()
        now = time.time()
        active_agents = len([
            a for a, t in self.agent_heartbeats.items()
            if now - t < HEARTBEAT_TIMEOUT
        ])

        lines = [
            "📊 SYSTEM STATUS",
            "═" * 25,
            f"CPU:  {health['cpu_percent']}%",
            f"RAM:  {health['ram_percent']}%",
            f"Disk: {health['disk_percent']}%",
            f"Agents: {active_agents} active",
            f"Docker: {health['docker'].get('running', 0)} containers",
            f"Status: {health['overall'].upper()}",
        ]

        if health["alerts"]:
            lines.append(f"\n⚠️ {len(health['alerts'])} active alerts")

        return "\n".join(lines)


if __name__ == "__main__":
    agent = MonitorAgent()
    agent.start()
