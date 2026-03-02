import unittest

from core.agent import Agent
from core.skills import SkillInfo


class _FakeSkills:
    def __init__(self, skill: SkillInfo):
        self._skill = skill

    def refresh(self):
        return None

    def get_skill(self, name: str):
        if name in {self._skill.key, self._skill.name}:
            return self._skill
        return None

    def build_run_prompt(self, skill: SkillInfo, user_instruction: str = "") -> str:
        return f"run {skill.key}: {user_instruction}"


class AgentRunSkillTests(unittest.TestCase):
    def test_run_skill_disables_auto_goal_setup(self):
        agent = Agent.__new__(Agent)
        skill = SkillInfo(
            key="kpi-daily-check",
            name="kpi-daily-check",
            description="",
            path=None,  # type: ignore[arg-type]
        )
        agent.skills = _FakeSkills(skill)
        captured = {}

        def fake_chat(message: str, chat_id: str = "default", auto_goal_setup: bool = True):
            captured["message"] = message
            captured["chat_id"] = chat_id
            captured["auto_goal_setup"] = auto_goal_setup
            return "ok"

        agent.chat = fake_chat  # type: ignore[assignment]
        agent.list_skills = lambda: [{"key": "kpi-daily-check"}]  # type: ignore[assignment]

        result = agent.run_skill("kpi-daily-check", "오늘 체크", chat_id="c1")
        self.assertEqual(result, "ok")
        self.assertEqual(captured["chat_id"], "c1")
        self.assertFalse(captured["auto_goal_setup"])


if __name__ == "__main__":
    unittest.main()
