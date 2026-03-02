"""
Simple file-based memory.
Stores conversation history, goals, and logs as plain files.
"""
import json
import os
from datetime import datetime
from pathlib import Path


class Memory:
    def __init__(self, memory_dir: str = "./memory"):
        self.dir = Path(memory_dir)
        self.dir.mkdir(parents=True, exist_ok=True)

    def load_goals(self) -> str:
        """Load goals.md content."""
        goals_file = self.dir / "goals.md"
        if goals_file.exists():
            return goals_file.read_text()
        return "No goals defined yet. Create memory/goals.md to set your goals."

    def save_goals(self, content: str):
        """Save goals.md."""
        (self.dir / "goals.md").write_text(content)

    def load_context(self) -> str:
        """Load persistent context (CONTEXT.md)."""
        ctx_file = self.dir / "CONTEXT.md"
        if ctx_file.exists():
            return ctx_file.read_text()
        return ""

    def save_context(self, content: str):
        (self.dir / "CONTEXT.md").write_text(content)

    def log(self, message: str, category: str = "general"):
        """Append a log entry to daily log file."""
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.dir / f"log-{today}.md"
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] [{category}] {message}\n"
        with open(log_file, "a") as f:
            f.write(entry)

    def get_conversation_history(self, chat_id: str, limit: int = 20) -> list[dict]:
        """Load recent conversation history for a chat."""
        history_file = self.dir / f"history-{chat_id}.json"
        if not history_file.exists():
            return []
        with open(history_file) as f:
            history = json.load(f)
        return history[-limit:]

    def save_message(self, chat_id: str, role: str, content: str):
        """Append a message to conversation history."""
        history_file = self.dir / f"history-{chat_id}.json"
        history = []
        if history_file.exists():
            with open(history_file) as f:
                history = json.load(f)
        history.append({"role": role, "content": content})
        # Keep last 100 messages per chat
        history = history[-100:]
        with open(history_file, "w") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
