import unittest

from main import normalize_config


class MainConfigTests(unittest.TestCase):
    def test_normalize_config_applies_defaults(self):
        cfg = normalize_config(
            {
                "claude": {"api_key": "k"},
            }
        )
        self.assertEqual(cfg["memory"]["dir"], "./memory")
        self.assertEqual(cfg["skills"]["dir"], "./skills")
        self.assertIn("browser", cfg)
        self.assertFalse(cfg["browser"]["headless"])

    def test_normalize_config_requires_claude_api_key(self):
        with self.assertRaises(ValueError):
            normalize_config({"claude": {}})

    def test_normalize_config_rejects_invalid_cron(self):
        with self.assertRaises(ValueError):
            normalize_config(
                {
                    "claude": {"api_key": "k"},
                    "cron": {},
                }
            )

    def test_normalize_config_rejects_invalid_root(self):
        with self.assertRaises(ValueError):
            normalize_config([])  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
