import json
import tempfile
import unittest
from pathlib import Path

from core.memory import Memory


class MemoryHistoryTests(unittest.TestCase):
    def test_corrupted_history_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            memory = Memory(memory_dir=tmp)
            history_file = Path(tmp) / "history-default.json"
            history_file.write_text("{invalid json")

            history = memory.get_conversation_history("default")
            self.assertEqual(history, [])

    def test_corrupted_history_is_overwritten_on_save(self):
        with tempfile.TemporaryDirectory() as tmp:
            memory = Memory(memory_dir=tmp)
            history_file = Path(tmp) / "history-default.json"
            history_file.write_text("{invalid json")

            memory.save_message("default", "user", "hello")
            parsed = json.loads(history_file.read_text())
            self.assertEqual(len(parsed), 1)
            self.assertEqual(parsed[0]["role"], "user")
            self.assertEqual(parsed[0]["content"], "hello")


if __name__ == "__main__":
    unittest.main()
