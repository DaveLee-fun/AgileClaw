import json
import tempfile
import unittest
from pathlib import Path

from agile.team import build_team_charter
from core.memory import Memory


class MemoryTeamTests(unittest.TestCase):
    def test_create_and_list_team(self):
        with tempfile.TemporaryDirectory() as tmp:
            memory = Memory(memory_dir=tmp)
            created = memory.create_team(
                goal_name="3월 매출 목표",
                objective="3월 말까지 일매출 300 달러",
                kpi_hint="daily revenue from dashboard",
            )
            self.assertIn("team_id", created)
            self.assertIn("path", created)

            teams = memory.list_teams()
            self.assertEqual(len(teams), 1)
            self.assertEqual(teams[0]["team_id"], created["team_id"])

            charter = memory.load_team_charter(created["team_id"])
            self.assertIn("Agile Team Charter", charter)
            self.assertIn("3월 매출 목표", charter)

    def test_same_goal_reuses_team(self):
        with tempfile.TemporaryDirectory() as tmp:
            memory = Memory(memory_dir=tmp)
            first = memory.create_team(
                goal_name="Revenue Goal",
                objective="Increase daily revenue to 300",
            )
            second = memory.create_team(
                goal_name="Revenue Goal",
                objective="Same goal follow-up",
            )

            self.assertTrue(first["created"])
            self.assertFalse(second["created"])
            self.assertEqual(first["team_id"], second["team_id"])

    def test_different_korean_goals_create_distinct_teams(self):
        with tempfile.TemporaryDirectory() as tmp:
            memory = Memory(memory_dir=tmp)
            first = memory.create_team(
                goal_name="3월 매출 목표",
                objective="3월 말까지 일매출 300 달러",
            )
            second = memory.create_team(
                goal_name="3월 사용자 증가 목표",
                objective="3월 말까지 신규 가입자 500명",
            )

            self.assertNotEqual(first["team_id"], second["team_id"])
            self.assertEqual(len(memory.list_teams()), 2)

    def test_legacy_goal_index_key_is_migrated(self):
        with tempfile.TemporaryDirectory() as tmp:
            memory = Memory(memory_dir=tmp)
            team_id = "team-legacy-goal"
            team_file = Path(tmp) / "teams" / f"{team_id}.md"
            team_file.write_text(
                build_team_charter(
                    team_id=team_id,
                    goal_name="3월 매출 목표",
                    objective="legacy objective",
                )
            )

            index_path = Path(tmp) / "teams" / "index.json"
            index_path.write_text(json.dumps({"3": team_id}, ensure_ascii=False))

            reused = memory.create_team(
                goal_name="3월 매출 목표",
                objective="same goal from upgraded runtime",
            )
            self.assertFalse(reused["created"])
            self.assertEqual(reused["team_id"], team_id)

            upgraded_index = json.loads(index_path.read_text())
            self.assertNotIn("3", upgraded_index)
            self.assertIn(team_id, upgraded_index.values())


if __name__ == "__main__":
    unittest.main()
