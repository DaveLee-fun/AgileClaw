"""
Shell execution tool — run any shell command on the host machine.
Full PC access, no sandboxing.
"""
import subprocess


TOOL_DEFINITION = {
    "name": "shell",
    "description": "Execute a shell command on the host machine. Returns stdout+stderr.",
    "input_schema": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "Shell command to execute (bash)",
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds (default: 30)",
            },
        },
        "required": ["command"],
    },
}


def run(command: str, timeout: int = 30) -> str:
    """Execute shell command, return combined stdout+stderr."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[stderr]\n{result.stderr}"
        return output.strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return f"Error: command timed out after {timeout}s"
    except Exception as e:
        return f"Error: {e}"
