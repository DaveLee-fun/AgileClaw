"""
Threads API tool.
"""
import json

import httpx


THREADS_BASE_URL = "https://graph.threads.net/v1.0"

TOOL_GET_FOLLOWERS = {
    "name": "threads_get_followers",
    "description": "Get Threads account metrics such as followers_count using Threads Graph API.",
    "input_schema": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "Threads user ID",
            },
            "access_token": {
                "type": "string",
                "description": "Threads API access token",
            },
            "fields": {
                "type": "string",
                "description": "Comma-separated fields. Default: followers_count",
            },
        },
        "required": ["user_id", "access_token"],
    },
}


def get_followers(user_id: str, access_token: str, fields: str = "followers_count") -> str:
    """Fetch account metrics from Threads Graph API."""
    url = f"{THREADS_BASE_URL}/{user_id}"
    params = {
        "fields": fields,
        "access_token": access_token,
    }

    try:
        with httpx.Client(timeout=20) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        payload = {
            "user_id": user_id,
            "requested_fields": [part.strip() for part in fields.split(",") if part.strip()],
            "data": data,
        }
        if "followers_count" in data:
            payload["followers_count"] = data.get("followers_count")

        return json.dumps(payload, ensure_ascii=False)
    except Exception as exc:
        return f"Error getting Threads metrics: {exc}"


def _handle_get_followers(tool_input: dict, context: dict) -> str:
    fields = tool_input.get("fields", "followers_count")
    return get_followers(
        user_id=tool_input["user_id"],
        access_token=tool_input["access_token"],
        fields=fields,
    )


def get_tool_specs() -> list[dict]:
    return [
        {
            "definition": TOOL_GET_FOLLOWERS,
            "handler": _handle_get_followers,
        }
    ]
