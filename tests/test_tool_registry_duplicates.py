import types
import unittest
from unittest.mock import patch

import tools


class ToolRegistryDuplicateTests(unittest.TestCase):
    def test_duplicate_tool_name_is_reported(self):
        fake_mod_a = types.SimpleNamespace(
            get_tool_specs=lambda: [
                {
                    "definition": {
                        "name": "dup_tool",
                        "description": "tool a",
                        "input_schema": {"type": "object", "properties": {}},
                    },
                    "handler": lambda tool_input, context: "a",
                }
            ]
        )
        fake_mod_b = types.SimpleNamespace(
            get_tool_specs=lambda: [
                {
                    "definition": {
                        "name": "dup_tool",
                        "description": "tool b",
                        "input_schema": {"type": "object", "properties": {}},
                    },
                    "handler": lambda tool_input, context: "b",
                }
            ]
        )

        def fake_import(module_name: str):
            if module_name.endswith(".mod_a"):
                return fake_mod_a
            if module_name.endswith(".mod_b"):
                return fake_mod_b
            raise ImportError(module_name)

        with patch.object(tools.pkgutil, "iter_modules", return_value=[(None, "mod_a", False), (None, "mod_b", False)]):
            with patch.object(tools, "import_module", side_effect=fake_import):
                definitions, handlers, errors = tools.load_tools()

        self.assertEqual(len(definitions), 1)
        self.assertIn("dup_tool", handlers)
        self.assertTrue(any("duplicate tool name 'dup_tool'" in err for err in errors))


if __name__ == "__main__":
    unittest.main()
