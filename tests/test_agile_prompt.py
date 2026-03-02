import unittest

from agile.loop import build_agile_prompt


class AgilePromptTests(unittest.TestCase):
    def test_agile_prompt_contains_team_refs(self):
        goals = "Goal: Increase revenue"
        refs = "- team-revenue | goal=revenue | charter=/tmp/team-revenue.md"
        prompt = build_agile_prompt(goals, team_refs=refs)
        self.assertIn(goals, prompt)
        self.assertIn("Goal team charters", prompt)
        self.assertIn(refs, prompt)

    def test_agile_prompt_handles_empty_team_refs(self):
        prompt = build_agile_prompt("Goal: Retention", team_refs="")
        self.assertIn("Goal team charters", prompt)
        self.assertIn("(none)", prompt)


if __name__ == "__main__":
    unittest.main()
