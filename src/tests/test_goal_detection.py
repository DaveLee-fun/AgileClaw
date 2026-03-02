import unittest

from core.agent import Agent


class GoalDetectionTests(unittest.TestCase):
    def test_goal_request_detected_korean(self):
        self.assertTrue(Agent._looks_like_goal_request("목표: 3월 말까지 매출 300 달러 달성"))

    def test_goal_request_detected_english(self):
        self.assertTrue(Agent._looks_like_goal_request("Goal: increase revenue by 30%"))

    def test_goal_request_detected_korean_heuristic(self):
        self.assertTrue(Agent._looks_like_goal_request("3월 말까지 앱 설치를 80으로 올려줘"))

    def test_non_goal_request_not_detected(self):
        self.assertFalse(Agent._looks_like_goal_request("오늘 날씨 알려줘"))

    def test_extract_goal_name_prefers_marker(self):
        name = Agent._extract_goal_name("목표: Threads 팔로워 250 달성\n추가 메모")
        self.assertEqual(name, "Threads 팔로워 250 달성")

    def test_auto_marker_is_not_goal(self):
        self.assertFalse(Agent._looks_like_goal_request("[AUTO_TEAM_SETUP] Goal: increase revenue"))


if __name__ == "__main__":
    unittest.main()
