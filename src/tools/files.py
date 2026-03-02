"""
File read/write tool.
"""
from pathlib import Path

TOOL_READ = {
    "name": "read_file",
    "description": "Read the contents of a file.",
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "File path to read"},
        },
        "required": ["path"],
    },
}

TOOL_WRITE = {
    "name": "write_file",
    "description": "Write content to a file (creates or overwrites).",
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "File path to write"},
            "content": {"type": "string", "description": "Content to write"},
        },
        "required": ["path", "content"],
    },
}


def read_file(path: str) -> str:
    try:
        return Path(path).read_text()
    except Exception as e:
        return f"Error reading file: {e}"


def write_file(path: str, content: str) -> str:
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
        return f"Written {len(content)} bytes to {path}"
    except Exception as e:
        return f"Error writing file: {e}"


def _handle_read(tool_input: dict, context: dict) -> str:
    return read_file(tool_input["path"])


def _handle_write(tool_input: dict, context: dict) -> str:
    return write_file(tool_input["path"], tool_input["content"])


def get_tool_specs() -> list[dict]:
    return [
        {
            "definition": TOOL_READ,
            "handler": _handle_read,
        },
        {
            "definition": TOOL_WRITE,
            "handler": _handle_write,
        },
    ]
