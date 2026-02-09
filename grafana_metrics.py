#!/usr/bin/env python3
"""
GRAFANA CLOUD METRICS EXPORTER
Maurice's AI Empire - Full Observability

Exports to Grafana Cloud:
- Agent performance metrics
- Revenue tracking
- Cost monitoring
- Error rates
- Conversion funnel
"""

import asyncio
import aiohttp
import json
import os
import logging
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Grafana Cloud Configuration
# Get these from: https://grafana.com/orgs/<your-org>/stacks
GRAFANA_CLOUD_URL = os.getenv("GRAFANA_CLOUD_URL", "https://influx-prod-eu-west-0.grafana.net/api/v1/push/influx/write")
GRAFANA_USER = os.getenv("GRAFANA_USER", "")  # Your Grafana Cloud user ID
GRAFANA_API_KEY = os.getenv("GRAFANA_API_KEY", "")  # API key from Grafana Cloud


@dataclass
class Metric:
    """Single metric point"""
    name: str
    value: float
    tags: Dict[str, str] = field(default_factory=dict)
    timestamp: Optional[int] = None  # Unix timestamp in nanoseconds
    
    def to_influx_line(self) -> str:
        """Convert to InfluxDB line protocol"""
        # Format: measurement,tag1=val1,tag2=val2 field=value timestamp
        tags_str = ",".join(f"{k}={v}" for k, v in self.tags.items())
        measurement = f"empire_{self.name}"
        if tags_str:
            measurement = f"{measurement},{tags_str}"
        ts = self.timestamp or int(time.time() * 1_000_000_000)
        return f"{measurement} value={self.value} {ts}"


class GrafanaExporter:
    """
    Exports metrics to Grafana Cloud
    Uses InfluxDB line protocol over HTTP
    """
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.metrics_buffer: List[Metric] = []
        self.buffer_size = 100  # Flush every 100 metrics
        self.stats = {
            "metrics_sent": 0,
            "metrics_failed": 0,
            "last_flush": None,
        }
    
    async def init(self):
        if not self.session:
            auth = aiohttp.BasicAuth(GRAFANA_USER, GRAFANA_API_KEY) if GRAFANA_USER else None
            self.session = aiohttp.ClientSession(auth=auth)
    
    async def close(self):
        await self.flush()
        if self.session:
            await self.session.close()
    
    def record(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a metric"""
        metric = Metric(name=name, value=value, tags=tags or {})
        self.metrics_buffer.append(metric)
        
        if len(self.metrics_buffer) >= self.buffer_size:
            asyncio.create_task(self.flush())
    
    async def flush(self):
        """Send buffered metrics to Grafana Cloud"""
        if not self.metrics_buffer:
            return
        
        if not GRAFANA_USER or not GRAFANA_API_KEY:
            # Local mode - just log metrics
            logger.info(f"📊 [LOCAL] {len(self.metrics_buffer)} metrics recorded")
            for m in self.metrics_buffer[-5:]:  # Show last 5
                logger.debug(f"  {m.name}: {m.value} {m.tags}")
            self.metrics_buffer = []
            return
        
        await self.init()
        
        # Build payload
        lines = [m.to_influx_line() for m in self.metrics_buffer]
        payload = "\n".join(lines)
        
        try:
            async with self.session.post(
                GRAFANA_CLOUD_URL,
                data=payload,
                headers={"Content-Type": "text/plain"}
            ) as resp:
                if resp.status in (200, 204):
                    self.stats["metrics_sent"] += len(self.metrics_buffer)
                    logger.info(f"📊 Sent {len(self.metrics_buffer)} metrics to Grafana")
                else:
                    self.stats["metrics_failed"] += len(self.metrics_buffer)
                    error = await resp.text()
                    logger.error(f"Grafana error {resp.status}: {error[:200]}")
        except Exception as e:
            self.stats["metrics_failed"] += len(self.metrics_buffer)
            logger.error(f"Grafana export failed: {e}")
        
        self.metrics_buffer = []
        self.stats["last_flush"] = datetime.now().isoformat()


class EmpireMetrics:
    """
    High-level metrics for Maurice's AI Empire
    """
    
    def __init__(self):
        self.exporter = GrafanaExporter()
    
    async def init(self):
        await self.exporter.init()
    
    async def close(self):
        await self.exporter.close()
    
    # =========================================================================
    # AGENT METRICS
    # =========================================================================
    
    def record_agent_task(self, agent_type: str, status: str, duration_ms: float):
        """Record agent task execution"""
        self.exporter.record("agent_task_total", 1, {"agent_type": agent_type, "status": status})
        self.exporter.record("agent_task_duration_ms", duration_ms, {"agent_type": agent_type})
    
    def record_agent_count(self, agent_type: str, count: int):
        """Record active agent count"""
        self.exporter.record("agent_active", count, {"agent_type": agent_type})
    
    # =========================================================================
    # REVENUE METRICS
    # =========================================================================
    
    def record_sale(self, product: str, amount_eur: float):
        """Record a sale"""
        self.exporter.record("revenue_sale_eur", amount_eur, {"product": product})
        self.exporter.record("revenue_sale_count", 1, {"product": product})
    
    def record_lead(self, source: str, score: int):
        """Record lead generation"""
        self.exporter.record("lead_generated", 1, {"source": source})
        self.exporter.record("lead_score", score, {"source": source})
    
    def record_conversion(self, stage: str, converted: bool):
        """Record funnel conversion"""
        self.exporter.record("funnel_conversion", 1 if converted else 0, {"stage": stage})
    
    # =========================================================================
    # COST METRICS
    # =========================================================================
    
    def record_kimi_usage(self, tokens: int, cost_usd: float):
        """Record Kimi API usage"""
        self.exporter.record("kimi_tokens", tokens, {})
        self.exporter.record("kimi_cost_usd", cost_usd, {})
    
    def record_cost(self, service: str, amount_usd: float):
        """Record cost"""
        self.exporter.record("cost_usd", amount_usd, {"service": service})
    
    # =========================================================================
    # PERFORMANCE METRICS
    # =========================================================================
    
    def record_latency(self, operation: str, latency_ms: float):
        """Record operation latency"""
        self.exporter.record("latency_ms", latency_ms, {"operation": operation})
    
    def record_error(self, component: str, error_type: str):
        """Record error"""
        self.exporter.record("error_total", 1, {"component": component, "error_type": error_type})
    
    def record_throughput(self, operation: str, count: int):
        """Record throughput"""
        self.exporter.record("throughput_per_sec", count, {"operation": operation})
    
    # =========================================================================
    # BRAIN METRICS
    # =========================================================================
    
    def record_brain_decision(self, cell: str, decision: str, confidence: float):
        """Record 8-brain decision"""
        self.exporter.record("brain_decision", 1, {"cell": cell, "decision": decision})
        self.exporter.record("brain_confidence", confidence, {"cell": cell})
    
    async def flush(self):
        """Force flush metrics"""
        await self.exporter.flush()


# ============================================================================
# DEMO DASHBOARD GENERATOR
# ============================================================================

def generate_grafana_dashboard() -> Dict[str, Any]:
    """Generate Grafana dashboard JSON for import"""
    return {
        "dashboard": {
            "title": "Maurice's AI Empire",
            "tags": ["empire", "ai", "revenue"],
            "timezone": "browser",
            "panels": [
                {
                    "id": 1,
                    "title": "Revenue (EUR)",
                    "type": "stat",
                    "gridPos": {"x": 0, "y": 0, "w": 6, "h": 4},
                    "targets": [{"expr": "sum(empire_revenue_sale_eur)"}]
                },
                {
                    "id": 2,
                    "title": "Active Agents",
                    "type": "gauge",
                    "gridPos": {"x": 6, "y": 0, "w": 6, "h": 4},
                    "targets": [{"expr": "sum(empire_agent_active)"}]
                },
                {
                    "id": 3,
                    "title": "Tasks/sec",
                    "type": "graph",
                    "gridPos": {"x": 12, "y": 0, "w": 12, "h": 4},
                    "targets": [{"expr": "rate(empire_agent_task_total[1m])"}]
                },
                {
                    "id": 4,
                    "title": "Kimi Cost ($)",
                    "type": "stat",
                    "gridPos": {"x": 0, "y": 4, "w": 6, "h": 4},
                    "targets": [{"expr": "sum(empire_kimi_cost_usd)"}]
                },
                {
                    "id": 5,
                    "title": "Conversion Rate",
                    "type": "stat",
                    "gridPos": {"x": 6, "y": 4, "w": 6, "h": 4},
                    "targets": [{"expr": "avg(empire_funnel_conversion)"}]
                },
                {
                    "id": 6,
                    "title": "Error Rate",
                    "type": "graph",
                    "gridPos": {"x": 12, "y": 4, "w": 12, "h": 4},
                    "targets": [{"expr": "rate(empire_error_total[5m])"}]
                },
            ]
        },
        "overwrite": True
    }


async def main():
    """Demo metrics recording"""
    metrics = EmpireMetrics()
    await metrics.init()
    
    logger.info("="*60)
    logger.info("GRAFANA METRICS EXPORTER - DEMO")
    logger.info("="*60)
    
    # Simulate some metrics
    for i in range(10):
        metrics.record_agent_task("sales", "completed", 150 + i*10)
        metrics.record_sale("core", 97.0)
        metrics.record_lead("twitter", 70 + i*3)
        metrics.record_kimi_usage(500, 0.00025)
        
        if i % 3 == 0:
            metrics.record_error("swarm", "timeout")
        
        await asyncio.sleep(0.1)
    
    await metrics.flush()
    
    logger.info(f"\nExporter stats: {metrics.exporter.stats}")
    
    # Generate dashboard
    dashboard = generate_grafana_dashboard()
    dashboard_path = "/Users/maurice/.gemini/antigravity/playground/photonic-schrodinger/grafana_dashboard.json"
    with open(dashboard_path, "w") as f:
        json.dump(dashboard, f, indent=2)
    logger.info(f"\n📊 Dashboard saved to: {dashboard_path}")
    logger.info("Import this JSON in Grafana: Dashboards → New → Import")
    
    await metrics.close()


if __name__ == "__main__":
    asyncio.run(main())
