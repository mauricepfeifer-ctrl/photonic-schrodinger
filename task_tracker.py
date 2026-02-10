#!/usr/bin/env python3
"""
🎯 TASK TRACKER — Tracks 1000 Tasks + Generates Reports
Every completed task produces a full report with:
- What was done
- What improved
- Revenue impact
- Learnings
- Next steps
"""
import json
import os
import time
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from pathlib import Path

TASKS_FILE = "docs/MEGA_1000_TASKS.json"
REPORTS_DIR = "docs/task_reports"

@dataclass
class TaskReport:
    task_id: int
    title: str
    category: str
    completed_at: str
    duration_minutes: int
    what_was_done: str
    what_improved: str
    revenue_impact_eur: float
    learnings: List[str]
    tools_used: List[str]
    next_steps: List[str]
    rating: int  # 1-10

@dataclass 
class Task:
    id: int
    title: str
    category: str
    subcategory: str
    priority: str  # 💰 🧠 ⚡ 🔥
    revenue_potential_eur: float
    time_estimate_hours: float
    status: str = "pending"  # pending, in_progress, completed, skipped
    report: Optional[Dict] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

class TaskTracker:
    def __init__(self):
        self.tasks: List[Task] = []
        self.reports: List[TaskReport] = []
        os.makedirs(REPORTS_DIR, exist_ok=True)
        
    def load(self):
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE) as f:
                data = json.load(f)
                self.tasks = [Task(**t) for t in data.get("tasks", [])]
    
    def save(self):
        data = {"tasks": [asdict(t) for t in self.tasks], "updated_at": datetime.now().isoformat()}
        with open(TASKS_FILE, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def complete_task(self, task_id: int, report: TaskReport):
        for t in self.tasks:
            if t.id == task_id:
                t.status = "completed"
                t.completed_at = datetime.now().isoformat()
                t.report = asdict(report)
                break
        
        # Save individual report
        report_file = os.path.join(REPORTS_DIR, f"task_{task_id:04d}_report.md")
        with open(report_file, "w") as f:
            f.write(self._format_report(report))
        
        self.save()
        return report_file
    
    def _format_report(self, r: TaskReport) -> str:
        learnings = "\n".join(f"  - {l}" for l in r.learnings)
        tools = ", ".join(r.tools_used)
        next_steps = "\n".join(f"  - {s}" for s in r.next_steps)
        
        return f"""# ✅ Task #{r.task_id} — COMPLETED

## 📋 {r.title}
**Category**: {r.category}
**Completed**: {r.completed_at}
**Duration**: {r.duration_minutes} min
**Rating**: {"⭐" * r.rating} ({r.rating}/10)

---

## 🔧 What Was Done
{r.what_was_done}

## 📈 What Improved
{r.what_improved}

## 💰 Revenue Impact
**Estimated**: €{r.revenue_impact_eur:,.2f}

## 🧠 Learnings
{learnings}

## 🛠️ Tools Used
{tools}

## ➡️ Next Steps
{next_steps}

---
*Report generated at {datetime.now().isoformat()}*
"""

    def dashboard(self) -> str:
        total = len(self.tasks)
        done = sum(1 for t in self.tasks if t.status == "completed")
        in_prog = sum(1 for t in self.tasks if t.status == "in_progress")
        revenue = sum(t.report.get("revenue_impact_eur", 0) for t in self.tasks if t.report)
        
        return f"""
{'═'*60}
🎯  TASK TRACKER DASHBOARD
{'═'*60}
📊 Total Tasks:    {total}
✅ Completed:      {done} ({done/total*100:.1f}%)
🔄 In Progress:    {in_prog}
⏳ Pending:        {total - done - in_prog}
💰 Revenue Impact: €{revenue:,.2f}
{'═'*60}
"""

if __name__ == "__main__":
    tracker = TaskTracker()
    tracker.load()
    print(tracker.dashboard())
