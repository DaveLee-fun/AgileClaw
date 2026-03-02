import tempfile
import unittest

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


if __name__ == "__main__":
    unittest.main()
