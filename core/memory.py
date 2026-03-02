"""
Simple file-based memory.
Stores conversation history, goals, and logs as plain files.
"""
import json
from datetime import datetime
from pathlib import Path
from agile.loop import GOALS_TEMPLATE
from agile.team import make_team_id, build_team_charter


class Memory:
    def __init__(self, memory_dir: str = "./memory"):
        self.dir = Path(memory_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self._ensure_defaults()

    def _ensure_defaults(self):
        goals_file = self.dir / "goals.md"
        if not goals_file.exists():
            goals_file.write_text(GOALS_TEMPLATE)

        context_file = self.dir / "CONTEXT.md"
        if not context_file.exists():
            context_file.write_text("# Context\n\n")

        teams_dir = self.dir / "teams"
        teams_dir.mkdir(parents=True, exist_ok=True)

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

    def create_team(self, goal_name: str, objective: str, kpi_hint: str = "") -> dict:
        """Create a goal-specific agile team charter file."""
        team_id = make_team_id(goal_name)
        charter = build_team_charter(
            team_id=team_id,
            goal_name=goal_name,
            objective=objective,
            kpi_hint=kpi_hint,
        )
        team_file = self.dir / "teams" / f"{team_id}.md"
        team_file.write_text(charter)
        return {
            "team_id": team_id,
            "path": str(team_file.resolve()),
            "goal_name": goal_name,
            "objective": objective,
        }

    def list_teams(self) -> list[dict]:
        """List all agile team charter files."""
        teams_dir = self.dir / "teams"
        if not teams_dir.exists():
            return []

        teams: list[dict] = []
        for path in sorted(teams_dir.glob("team-*.md")):
            team_id = path.stem
            goal_name = team_id
            try:
                for line in path.read_text().splitlines():
                    if line.startswith("- Goal Name:"):
                        goal_name = line.split(":", 1)[1].strip()
                        break
            except Exception:
                pass
            teams.append(
                {
                    "team_id": team_id,
                    "goal_name": goal_name,
                    "path": str(path.resolve()),
                }
            )
        return teams

    def load_team_charter(self, team_id: str) -> str:
        team_file = self.dir / "teams" / f"{team_id}.md"
        if not team_file.exists():
            return ""
        return team_file.read_text()
