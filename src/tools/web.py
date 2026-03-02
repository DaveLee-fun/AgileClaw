"""
Web fetch tool — fetch URL content as text/markdown.
Uses httpx (no API key needed).
"""
import httpx

TOOL_DEFINITION = {
    "name": "web_fetch",
    "description": "Fetch content from a URL and return it as text. Use this for web searches and reading pages.",
    "input_schema": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "URL to fetch. For search, use: https://duckduckgo.com/html/?q=YOUR+QUERY",
            },
            "max_chars": {
                "type": "integer",
                "description": "Max characters to return (default: 5000)",
            },
        },
        "required": ["url"],
    },
}


def fetch(url: str, max_chars: int = 5000) -> str:
    """Fetch URL, return text content."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        with httpx.Client(follow_redirects=True, timeout=15) as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()
            text = response.text
            # Basic HTML stripping (rough)
            import re
            text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL)
            text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
            text = re.sub(r"<[^>]+>", " ", text)
            text = re.sub(r"\s+", " ", text).strip()
            return text[:max_chars]
    except Exception as e:
        return f"Error fetching {url}: {e}"


def _handle_web_fetch(tool_input: dict, context: dict) -> str:
    max_chars = int(tool_input.get("max_chars", 5000))
    return fetch(tool_input["url"], max_chars=max_chars)


def get_tool_specs() -> list[dict]:
    return [
        {
            "definition": TOOL_DEFINITION,
            "handler": _handle_web_fetch,
        }
    ]
