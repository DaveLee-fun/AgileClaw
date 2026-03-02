import unittest

from agile.report import build_daily_report_prompt, build_weekly_report_prompt


class ReportPromptTests(unittest.TestCase):
    def test_daily_prompt_contains_goals(self):
        goals = "Metric A: 10 -> 20"
        prompt = build_daily_report_prompt(goals)

        self.assertIn(goals, prompt)
        self.assertIn("today", prompt.lower())
        self.assertIn("top risk KPI", prompt)

    def test_weekly_prompt_contains_goals(self):
        goals = "Metric B: 5 -> 15"
        prompt = build_weekly_report_prompt(goals)

        self.assertIn(goals, prompt)
        self.assertIn("week", prompt.lower())
        self.assertIn("top 3 actions", prompt)

    def test_daily_prompt_includes_team_refs(self):
        goals = "Metric C: 1 -> 2"
        refs = "- team-1 | goal=growth | charter=/tmp/team-1.md"
        prompt = build_daily_report_prompt(goals, team_refs=refs)
        self.assertIn("Goal team charters", prompt)
        self.assertIn(refs, prompt)

    def test_weekly_prompt_handles_empty_team_refs(self):
        goals = "Metric D: 10 -> 12"
        prompt = build_weekly_report_prompt(goals, team_refs="")
        self.assertIn("Goal team charters", prompt)
        self.assertIn("(none)", prompt)


if __name__ == "__main__":
    unittest.main()
