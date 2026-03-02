"""
Simple file-based memory.
Stores conversation history, goals, and logs as plain files.
"""
import json
from datetime import datetime
from pathlib import Path
import re
from agile.loop import GOALS_TEMPLATE
from agile.team import make_team_id, build_team_charter, slugify, make_goal_key


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

        team_index_file = self.dir / "teams" / "index.json"
        if not team_index_file.exists():
            team_index_file.write_text("{}")

    def _team_index_path(self) -> Path:
        return self.dir / "teams" / "index.json"

    def _load_team_index(self) -> dict:
        path = self._team_index_path()
        try:
            data = json.loads(path.read_text())
            if isinstance(data, dict):
                return data
            self.log("teams/index.json is not an object. Reset to empty index.", "error")
            return {}
        except Exception:
            return {}

    def _save_team_index(self, data: dict):
        path = self._team_index_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    @staticmethod
    def _legacy_goal_key(goal_name: str) -> str:
        """
        Backward compatibility for older index keys that only kept [a-z0-9].
        """
        value = (goal_name or "").strip().lower()
        value = re.sub(r"[^a-z0-9]+", "-", value)
        value = re.sub(r"-+", "-", value).strip("-")
        return value or "goal"

    @staticmethod
    def _extract_goal_name_from_charter(team_file: Path) -> str:
        try:
            for line in team_file.read_text().splitlines():
                if line.startswith("- Goal Name:"):
                    return line.split(":", 1)[1].strip()
        except Exception:
            return ""
        return ""

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
        try:
            with open(history_file) as f:
                history = json.load(f)
        except Exception:
            self.log(f"Corrupted history file detected: {history_file.name}. Reset to empty history.", "error")
            return []
        if not isinstance(history, list):
            self.log(f"Invalid history format detected: {history_file.name}. Reset to empty history.", "error")
            return []
        normalized: list[dict] = []
        for item in history:
            if not isinstance(item, dict):
                continue
            role = item.get("role")
            content = item.get("content")
            if role not in {"user", "assistant"}:
                continue
            if not isinstance(content, str):
                content = str(content)
            normalized.append({"role": role, "content": content})
        return normalized[-limit:]

    def save_message(self, chat_id: str, role: str, content: str):
        """Append a message to conversation history."""
        history_file = self.dir / f"history-{chat_id}.json"
        history = []
        if history_file.exists():
            try:
                with open(history_file) as f:
                    history = json.load(f)
            except Exception:
                self.log(f"Corrupted history file overwritten: {history_file.name}.", "error")
                history = []
        if not isinstance(history, list):
            self.log(f"Invalid history format overwritten: {history_file.name}.", "error")
            history = []
        history.append({"role": role, "content": content})
        # Keep last 100 messages per chat
        history = history[-100:]
        with open(history_file, "w") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def create_team(self, goal_name: str, objective: str, kpi_hint: str = "") -> dict:
        """
        Create or reuse a goal-specific agile team charter file.

        Reuse rule:
        - If the same normalized goal key exists in team index and file exists, reuse team.
        - Otherwise create a new team and register it in index.
        """
        goal_key = make_goal_key(goal_name)
        index = self._load_team_index()

        lookup_keys = [goal_key, slugify(goal_name), self._legacy_goal_key(goal_name)]
        existing_team_id = ""
        matched_key = ""
        stale_key = ""
        for key in lookup_keys:
            if key and key in index:
                existing_team_id = index.get(key, "")
                matched_key = key
                break

        if existing_team_id:
            team_file = self.dir / "teams" / f"{existing_team_id}.md"
            if team_file.exists():
                # For legacy keys, verify actual charter goal before reusing.
                if matched_key and matched_key != goal_key:
                    charter_goal = self._extract_goal_name_from_charter(team_file)
                    if charter_goal and make_goal_key(charter_goal) != goal_key:
                        existing_team_id = ""
                        stale_key = matched_key

        if existing_team_id:
            team_file = self.dir / "teams" / f"{existing_team_id}.md"
            if team_file.exists():
                # Migrate legacy key to hash key to prevent future collisions.
                changed = False
                if index.get(goal_key) != existing_team_id:
                    index[goal_key] = existing_team_id
                    changed = True
                if matched_key and matched_key != goal_key:
                    index.pop(matched_key, None)
                    changed = True
                if changed:
                    self._save_team_index(index)
                return {
                    "team_id": existing_team_id,
                    "path": str(team_file.resolve()),
                    "goal_name": goal_name,
                    "objective": objective,
                    "created": False,
                }
        elif stale_key:
            index.pop(stale_key, None)
            self._save_team_index(index)

        team_id = make_team_id(goal_name)
        charter = build_team_charter(
            team_id=team_id,
            goal_name=goal_name,
            objective=objective,
            kpi_hint=kpi_hint,
        )
        team_file = self.dir / "teams" / f"{team_id}.md"
        team_file.write_text(charter)
        index[goal_key] = team_id
        for key in lookup_keys:
            if key and key != goal_key and index.get(key) == team_id:
                index.pop(key, None)
        self._save_team_index(index)
        return {
            "team_id": team_id,
            "path": str(team_file.resolve()),
            "goal_name": goal_name,
            "objective": objective,
            "created": True,
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
