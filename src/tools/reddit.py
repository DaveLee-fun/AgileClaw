"""
Reddit public profile tool.
"""
import json

import httpx


TOOL_GET_KARMA = {
    "name": "reddit_get_karma",
    "description": "Get Reddit user karma summary from public profile API.",
    "input_schema": {
        "type": "object",
        "properties": {
            "username": {
                "type": "string",
                "description": "Reddit username (without u/)",
            },
        },
        "required": ["username"],
    },
}


def get_karma(username: str) -> str:
    """Fetch karma from Reddit public user endpoint."""
    url = f"https://www.reddit.com/user/{username}/about.json"
    headers = {
        "User-Agent": "AgileClaw/1.0 (KPI tracker)",
    }

    try:
        with httpx.Client(timeout=20, follow_redirects=True) as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json().get("data", {})

        payload = {
            "username": data.get("name", username),
            "total_karma": data.get("total_karma"),
            "link_karma": data.get("link_karma"),
            "comment_karma": data.get("comment_karma"),
            "created_utc": data.get("created_utc"),
            "is_suspended": data.get("is_suspended"),
        }
        return json.dumps(payload, ensure_ascii=False)
    except Exception as exc:
        return f"Error getting Reddit karma: {exc}"


def _handle_get_karma(tool_input: dict, context: dict) -> str:
    return get_karma(tool_input["username"])


def get_tool_specs() -> list[dict]:
    return [
        {
            "definition": TOOL_GET_KARMA,
            "handler": _handle_get_karma,
        }
    ]
