"""
Main agent — the brain of AgileClaw.
Receives a message, thinks with Claude, uses tools, returns response.
"""
from typing import Callable
import re

from core.claude import ClaudeClient
from core.memory import Memory
from core.skills import SkillCatalog
from tools import load_tools
from agile.loop import AGILE_SYSTEM_PROMPT, build_agile_prompt
from agile.report import build_daily_report_prompt, build_weekly_report_prompt
from agile.team import build_team_bootstrap_prompt, build_team_update_prompt

SYSTEM_PROMPT_BASE = """You are AgileClaw — a personal AI agent with full access to the host machine.

You can:
- Use tools to run commands, read/write files, browse the web, and control the browser

Core policy:
- Agile execution is mandatory: each goal/request should be treated as an Agile Team unit.
- Before execution, define how success is measured (KPI source, frequency, numeric target).
- Then execute, measure, and improve in loops.

You have memory of past conversations and team goals.
When a local skill is relevant, read the referenced SKILL.md and follow it.

Be direct, efficient, and proactive. If you can do something, do it — don't just explain how.
Keep responses concise. Use Korean when the user writes in Korean.
"""


class Agent:
    def __init__(self, config: dict):
        claude_cfg = config["claude"]
        self.claude = ClaudeClient(
            api_key=claude_cfg["api_key"],
            model=claude_cfg.get("model", "claude-sonnet-4-5"),
            max_tokens=claude_cfg.get("max_tokens", 4096),
            max_tool_rounds=claude_cfg.get("max_tool_rounds", 10),
            max_retries=claude_cfg.get("max_retries", 2),
            retry_base_delay=claude_cfg.get("retry_base_delay", 1.0),
        )
        self.memory = Memory(config["memory"]["dir"])
        self.headless = config.get("browser", {}).get("headless", False)
        self.scheduler = None

        skills_dir = config.get("skills", {}).get("dir", "./skills")
        self.skills = SkillCatalog(skills_dir=skills_dir)
        self.skills.refresh()

        self.tool_definitions: list[dict] = []
        self.tool_handlers: dict[str, Callable[[dict, dict], str]] = {}
        self.tool_load_errors: list[str] = []
        self._refresh_tools()

    def _refresh_tools(self):
        self.tool_definitions, self.tool_handlers, self.tool_load_errors = load_tools()
        for err in self.tool_load_errors:
            self.memory.log(f"Tool load error: {err}", "error")

    def _build_system_prompt(self) -> str:
        context = self.memory.load_context()
        skills_block = self.skills.build_prompt_block()

        system = SYSTEM_PROMPT_BASE
        if context:
            system += f"\n\nContext:\n{context}"
        if skills_block:
            system += f"\n\nSkills:\n{skills_block}"
        return system

    def _build_team_refs(self) -> str:
        teams = self.memory.list_teams()
        if not teams:
            return ""

        lines: list[str] = []
        for team in teams:
            lines.append(
                f"- {team['team_id']} | goal={team['goal_name']} | charter={team['path']}"
            )
        return "\n".join(lines)

    def _tool_executor(self, tool_name: str, tool_input: dict) -> str:
        """Execute a tool call from Claude."""
        handler = self.tool_handlers.get(tool_name)
        if not handler:
            return f"Unknown tool: {tool_name}"
        try:
            return str(
                handler(
                    tool_input or {},
                    {
                        "headless": self.headless,
                        "memory_dir": str(self.memory.dir),
                    },
                )
            )
        except Exception as exc:
            return f"Error: {exc}"

    @staticmethod
    def _looks_like_goal_request(user_message: str) -> bool:
        text = (user_message or "").lower()
        if "[auto_team_setup]" in text:
            return False

        goal_markers = [
            "목표",
            "달성",
            "kpi",
            "성과",
            "target",
            "goal",
            "achieve",
            "increase",
            "grow",
        ]
        return any(marker in text for marker in goal_markers)

    @staticmethod
    def _extract_goal_name(user_message: str) -> str:
        text = (user_message or "").strip()
        if not text:
            return "new-goal"

        # Prefer explicit Korean marker like "목표: ..."
        match = re.search(r"목표\s*[:：]\s*(.+)", text)
        if match:
            candidate = match.group(1).splitlines()[0].strip()
            return candidate[:80]

        # Fallback: first sentence chunk
        chunk = re.split(r"[\n.!?]", text)[0].strip()
        if chunk:
            return chunk[:80]
        return text[:80]

    def chat(self, user_message: str, chat_id: str = "default", auto_goal_setup: bool = True) -> str:
        """Process a user message and return the agent's response."""
        self.skills.refresh()
        self._refresh_tools()

        prepared_message = user_message
        if auto_goal_setup and self._looks_like_goal_request(user_message):
            goal_name = self._extract_goal_name(user_message)
            team = self.memory.create_team(
                goal_name=goal_name,
                objective=user_message,
                kpi_hint=(
                    "Before execution, define KPI measurement method for each metric: "
                    "source, frequency, and numeric success threshold."
                ),
            )
            self.memory.log(
                f"Auto team setup: {team['team_id']} for goal '{goal_name}' (created={team.get('created')})",
                "agile",
            )
            prepared_message = (
                "[AUTO_TEAM_SETUP]\n"
                f"Team ID: {team['team_id']}\n"
                f"Team Charter: {team['path']}\n"
                f"Team Created: {team.get('created', False)}\n"
                "Requirement: confirm how each KPI will be measured first, then execute the goal.\n\n"
                "Original user request:\n"
                f"{user_message}"
            )

        # Load conversation history
        history = self.memory.get_conversation_history(chat_id)

        # Build system prompt
        system = self._build_system_prompt()

        # Build messages
        messages = history.copy()
        messages.append({"role": "user", "content": prepared_message})

        # Save user message
        self.memory.save_message(chat_id, "user", prepared_message)
        self.memory.log(f"User: {prepared_message[:100]}", "chat")

        # Run Claude with tools
        response = self.claude.chat(
            messages=messages,
            system=system,
            tools=self.tool_definitions,
            tool_executor=self._tool_executor,
        )

        # Save response
        self.memory.save_message(chat_id, "assistant", response)
        self.memory.log(f"Agent: {response[:100]}", "chat")

        return response

    def run_agile_review(self, chat_id: str = "default") -> str:
        """Run the agile loop — measure KPIs and suggest improvements."""
        self.skills.refresh()
        self._refresh_tools()
        goals = self.memory.load_goals()
        prompt = build_agile_prompt(goals, team_refs=self._build_team_refs())
        context = self.memory.load_context()

        system = AGILE_SYSTEM_PROMPT
        if context:
            system += f"\n\nContext:\n{context}"
        system += f"\n\nSkills:\n{self.skills.build_prompt_block()}"

        messages = [{"role": "user", "content": prompt}]
        response = self.claude.chat(
            messages=messages,
            system=system,
            tools=self.tool_definitions,
            tool_executor=self._tool_executor,
        )
        self.memory.log(f"Agile review completed", "agile")
        return response

    def run_daily_report(self, chat_id: str = "default") -> str:
        """Generate a daily KPI report."""
        self.skills.refresh()
        self._refresh_tools()
        goals = self.memory.load_goals()
        prompt = build_daily_report_prompt(goals, team_refs=self._build_team_refs())
        context = self.memory.load_context()

        system = AGILE_SYSTEM_PROMPT
        if context:
            system += f"\n\nContext:\n{context}"
        system += f"\n\nSkills:\n{self.skills.build_prompt_block()}"

        messages = [{"role": "user", "content": prompt}]
        response = self.claude.chat(
            messages=messages,
            system=system,
            tools=self.tool_definitions,
            tool_executor=self._tool_executor,
        )
        self.memory.log("Daily report completed", "agile")
        return response

    def run_weekly_report(self, chat_id: str = "default") -> str:
        """Generate a weekly KPI report."""
        self.skills.refresh()
        self._refresh_tools()
        goals = self.memory.load_goals()
        prompt = build_weekly_report_prompt(goals, team_refs=self._build_team_refs())
        context = self.memory.load_context()

        system = AGILE_SYSTEM_PROMPT
        if context:
            system += f"\n\nContext:\n{context}"
        system += f"\n\nSkills:\n{self.skills.build_prompt_block()}"

        messages = [{"role": "user", "content": prompt}]
        response = self.claude.chat(
            messages=messages,
            system=system,
            tools=self.tool_definitions,
            tool_executor=self._tool_executor,
        )
        self.memory.log("Weekly report completed", "agile")
        return response

    def list_skills(self) -> list[dict]:
        self.skills.refresh()
        return [
            {
                "key": skill.key,
                "name": skill.name,
                "description": skill.description,
                "path": str(skill.path),
            }
            for skill in self.skills.list_skills()
        ]

    def run_skill(self, skill_name: str, user_instruction: str = "", chat_id: str = "default") -> str:
        self.skills.refresh()
        skill = self.skills.get_skill(skill_name)
        if not skill:
            available = ", ".join(item["key"] for item in self.list_skills()) or "(none)"
            return f"Unknown skill: {skill_name}\nAvailable skills: {available}"

        prompt = self.skills.build_run_prompt(skill, user_instruction)
        return self.chat(prompt, chat_id=chat_id)

    def create_agile_team(
        self,
        goal_name: str,
        objective: str,
        kpi_hint: str = "",
        chat_id: str = "default",
    ) -> str:
        """Create a goal-specific agile team and run kickoff planning."""
        info = self.memory.create_team(goal_name=goal_name, objective=objective, kpi_hint=kpi_hint)
        team_id = info["team_id"]
        team_path = info["path"]
        created = bool(info.get("created", True))

        if created:
            prompt = build_team_bootstrap_prompt(
                team_id=team_id,
                team_file_path=team_path,
                user_instruction="Focus on measurable KPI cadence and first sprint execution.",
            )
        else:
            prompt = build_team_update_prompt(
                team_id=team_id,
                team_file_path=team_path,
                user_instruction="Continue this goal team sprint with latest KPI measurements.",
            )

        kickoff_result = self.chat(prompt, chat_id=chat_id, auto_goal_setup=False)
        return (
            f"Agile team {'created' if created else 'reused'}.\n"
            f"- team_id: {team_id}\n"
            f"- charter: {team_path}\n\n"
            f"Kickoff summary:\n{kickoff_result}"
        )

    def list_agile_teams(self) -> list[dict]:
        return self.memory.list_teams()
