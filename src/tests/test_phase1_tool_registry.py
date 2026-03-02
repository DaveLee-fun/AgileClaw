import unittest

from tools import load_tools


class ToolRegistryPhase1Tests(unittest.TestCase):
    def test_phase1_tools_are_registered(self):
        definitions, handlers, errors = load_tools()

        self.assertEqual(errors, [])

        names = {item["name"] for item in definitions}
        self.assertIn("threads_get_followers", names)
        self.assertIn("reddit_get_karma", names)

        self.assertIn("threads_get_followers", handlers)
        self.assertIn("reddit_get_karma", handlers)


if __name__ == "__main__":
    unittest.main()
