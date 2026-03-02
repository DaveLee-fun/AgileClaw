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

    def test_chat_id_is_sanitized_for_history_filename(self):
        with tempfile.TemporaryDirectory() as tmp:
            memory = Memory(memory_dir=tmp)
            chat_id = "team/../unsafe"
            memory.save_message(chat_id, "user", "x")

            safe_id = memory._sanitize_chat_id(chat_id)  # pylint: disable=protected-access
            unsafe_path = Path(tmp) / f"history-{chat_id}.json"
            safe_path = Path(tmp) / f"history-{safe_id}.json"
            self.assertFalse(unsafe_path.exists())
            self.assertTrue(safe_path.exists())


if __name__ == "__main__":
    unittest.main()
