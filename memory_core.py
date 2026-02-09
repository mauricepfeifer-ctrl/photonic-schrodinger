"""
🧠 MEMORY CORE — PERSISTENT CONTEXT SYSTEM
Maurice's AI Empire

Handles:
- Short-term Memory (Working Context)
- Long-term Memory (JSON Storage)
- Automated Pruning & Review
- Profile/Goal/Rule Schemas

Usage:
    from memory_core import MemorySystem
    mem = MemorySystem()
    mem.add_event("research", "Found new competitor: X")
    mem.daily_review()
"""
import json
import os
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field

# Setup
MEMORY_DIR = "memory_store"
if not os.path.exists(MEMORY_DIR):
    os.makedirs(MEMORY_DIR)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(MEMORY)s] %(message)s")
logger = logging.getLogger("Memory")

@dataclass
class Profile:
    name: str = "Maurice Pfeifer"
    role: str = "Empire Commander"
    goals: List[str] = field(default_factory=lambda: [
        "Simplify everything to 1-click",
        "Generate €10k/month automated revenue",
        "Build brand authority in AI Automation"
    ])
    constraints: List[str] = field(default_factory=lambda: [
        "No manual data entry",
        "High-ticket focus (>€500)",
        "Premium brand voice (No hype, just results)"
    ])

@dataclass
class MemoryItem:
    content: str
    feature: str  # e.g., "research", "feed", "system"
    timestamp: float = field(default_factory=time.time)
    importance: int = 1  # 1-5
    embedding: Optional[List[float]] = None  # For future vector search

class MemorySystem:
    def __init__(self):
        self.profile_path = f"{MEMORY_DIR}/profile.json"
        self.working_path = f"{MEMORY_DIR}/working_memory.json"
        self.archive_path = f"{MEMORY_DIR}/long_term_archive.jsonl"
        self.profile = self._load_profile()
        self.working_memory: List[Dict] = self._load_working()
        
    def _load_profile(self) -> Profile:
        if os.path.exists(self.profile_path):
            with open(self.profile_path, 'r') as f:
                data = json.load(f)
                return Profile(**data)
        return Profile()

    def _load_working(self) -> List[Dict]:
        if os.path.exists(self.working_path):
            with open(self.working_path, 'r') as f:
                return json.load(f)
        return []

    def save(self):
        """Persist current state to disk"""
        with open(self.profile_path, 'w') as f:
            json.dump(asdict(self.profile), f, indent=2)
        with open(self.working_path, 'w') as f:
            json.dump(self.working_memory, f, indent=2)

    def add_event(self, feature: str, content: str, importance: int = 1):
        """Add item to working memory"""
        item = MemoryItem(content=content, feature=feature, importance=importance)
        self.working_memory.append(asdict(item))
        # Auto-save if significant
        if importance > 3:
            self.save()
            logger.info(f"💾 Saved critical memory: {content[:40]}...")

    def get_context(self, limit: int = 10) -> str:
        """Get recent working memory as context string"""
        recent = sorted(self.working_memory, key=lambda x: x['timestamp'])[-limit:]
        context = []
        for item in recent:
            t = datetime.fromtimestamp(item['timestamp']).strftime('%H:%M')
            context.append(f"[{t}] [{item['feature'].upper()}] {item['content']}")
        return "\n".join(context)

    def daily_review(self):
        """
        Compress working memory into long-term archive.
        - High importance -> Archive
        - Low importance -> Discard
        - Summary -> working memory
        """
        logger.info("🧹 Starting Daily Memory Review...")
        
        # 1. Filter important items
        to_archive = [m for m in self.working_memory if m['importance'] >= 3]
        
        # 2. Append to archive
        with open(self.archive_path, 'a') as f:
            for item in to_archive:
                f.write(json.dumps(item) + "\n")
        
        # 3. Clear working memory (keep last 5 for continuity)
        kept = self.working_memory[-5:]
        
        # 4. Add summary marker
        summary = {
            "content": f"Daily Review completed. Archived {len(to_archive)} items. Cleared {len(self.working_memory) - len(kept)} items.",
            "feature": "system",
            "timestamp": time.time(),
            "importance": 5
        }
        kept.append(summary)
        
        self.working_memory = kept
        self.save()
        logger.info(f"✅ Daily Review Done. Archived {len(to_archive)} items.")

if __name__ == "__main__":
    # Test
    m = MemorySystem()
    m.add_event("test", "System initialized", 5)
    print("Context:\n" + m.get_context())
    m.daily_review()
