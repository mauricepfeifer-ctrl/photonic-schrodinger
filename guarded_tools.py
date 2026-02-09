"""
🛡️ GUARDED TOOLS — SAFE EXECUTION WRAPPER
Maurice's AI Empire

Handles:
- Whitelisted Command Execution
- Safe File System Access
- Audit Logging
- Browser Integration (ReadOnly vs Interactive)

Usage:
    from guarded_tools import Toolkit
    tools = Toolkit()
    tools.run_command("ls -la") 
"""
import subprocess
import logging
import os
import shutil
from datetime import datetime
from typing import List, Optional

logger = logging.getLogger("GuardedTools")

ALLOWED_COMMANDS = [
    "ls", "grep", "cat", "find", "wc", "head", "tail",
    "git status", "git log", "git diff",
    "python3 --version", "node -v"
]

ALLOWED_DIRS = [
    "/Users/maurice/.gemini/antigravity/playground/photonic-schrodinger",
    "content_output",
    "sales_output",
    "memory_store"
]

class Toolkit:
    def __init__(self):
        self.audit_log = "audit.log"

    def _log_action(self, action: str, details: str, allowed: bool):
        entry = f"{datetime.now().isoformat()} | {action.upper()} | {'✅ ALLOWED' if allowed else '🛑 BLOCKED'} | {details}\n"
        with open(self.audit_log, "a") as f:
            f.write(entry)
        if not allowed:
            logger.warning(f"🛑 Security Block: {action} - {details}")

    def run_command(self, cmd: str) -> str:
        """Execute a shell command if allowed"""
        # 1. basic verification
        is_safe = any(cmd.startswith(ok) for ok in ALLOWED_COMMANDS)
        
        # 2. log
        self._log_action("EXEC", cmd, is_safe)
        
        if not is_safe:
            return "🛑 Command not in whitelist."

        try:
            result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
            return result.decode("utf-8")
        except subprocess.CalledProcessError as e:
            return f"❌ Error: {e.output.decode('utf-8')}"

    def read_file(self, path: str) -> str:
        """Safe file read"""
        # 1. Path traversal check
        abs_path = os.path.abspath(path)
        is_allowed = any(abs_path.startswith(os.path.abspath(d)) for d in ALLOWED_DIRS)
        
        self._log_action("READ", path, is_allowed)
        
        if not is_allowed:
            return "🛑 Access denied. Directory not whitelisted."
            
        if not os.path.exists(abs_path):
            return "❌ File not found."
            
        with open(abs_path, "r") as f:
            return f.read()

    def write_file(self, path: str, content: str) -> str:
        """Safe file write"""
        abs_path = os.path.abspath(path)
        is_allowed = any(abs_path.startswith(os.path.abspath(d)) for d in ALLOWED_DIRS)
        
        self._log_action("WRITE", path, is_allowed)
        
        if not is_allowed:
            return "🛑 Access denied. Directory not whitelisted."
            
        with open(abs_path, "w") as f:
            f.write(content)
        return "✅ File written."

if __name__ == "__main__":
    t = Toolkit()
    print(t.run_command("ls -la"))
    print(t.run_command("rm -rf /")) # Should block
