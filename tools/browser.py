"""
Browser control tool via Playwright.
Headless=False by default so you can see what's happening.
"""
from playwright.sync_api import sync_playwright, Browser, Page
from typing import Optional

_browser: Optional[Browser] = None
_page: Optional[Page] = None

TOOL_OPEN = {
    "name": "browser_open",
    "description": "Open a URL in the browser.",
    "input_schema": {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "URL to open"},
        },
        "required": ["url"],
    },
}

TOOL_SCREENSHOT = {
    "name": "browser_screenshot",
    "description": "Take a screenshot of the current browser page. Returns the file path.",
    "input_schema": {"type": "object", "properties": {}},
}

TOOL_CLICK = {
    "name": "browser_click",
    "description": "Click an element on the page by CSS selector or text.",
    "input_schema": {
        "type": "object",
        "properties": {
            "selector": {"type": "string", "description": "CSS selector or text to click"},
        },
        "required": ["selector"],
    },
}

TOOL_TYPE = {
    "name": "browser_type",
    "description": "Type text into an input field.",
    "input_schema": {
        "type": "object",
        "properties": {
            "selector": {"type": "string", "description": "CSS selector for the input"},
            "text": {"type": "string", "description": "Text to type"},
        },
        "required": ["selector", "text"],
    },
}

TOOL_GET_TEXT = {
    "name": "browser_get_text",
    "description": "Get all visible text from the current page.",
    "input_schema": {"type": "object", "properties": {}},
}


def _get_page(headless: bool = False) -> Page:
    global _browser, _page
    if _browser is None:
        pw = sync_playwright().start()
        _browser = pw.chromium.launch(headless=headless)
    if _page is None or _page.is_closed():
        _page = _browser.new_page()
    return _page


def browser_open(url: str, headless: bool = False) -> str:
    try:
        page = _get_page(headless)
        page.goto(url, wait_until="domcontentloaded", timeout=15000)
        return f"Opened: {page.url} — Title: {page.title()}"
    except Exception as e:
        return f"Error: {e}"


def browser_screenshot(headless: bool = False) -> str:
    try:
        import tempfile, os
        page = _get_page(headless)
        path = os.path.join(tempfile.gettempdir(), "agileclaw_screenshot.png")
        page.screenshot(path=path)
        return f"Screenshot saved: {path}"
    except Exception as e:
        return f"Error: {e}"


def browser_click(selector: str, headless: bool = False) -> str:
    try:
        page = _get_page(headless)
        page.click(selector, timeout=5000)
        return f"Clicked: {selector}"
    except Exception as e:
        return f"Error: {e}"


def browser_type(selector: str, text: str, headless: bool = False) -> str:
    try:
        page = _get_page(headless)
        page.fill(selector, text)
        return f"Typed into {selector}"
    except Exception as e:
        return f"Error: {e}"


def browser_get_text(headless: bool = False) -> str:
    try:
        page = _get_page(headless)
        text = page.inner_text("body")
        return text[:5000]
    except Exception as e:
        return f"Error: {e}"


def _headless(context: dict) -> bool:
    return bool(context.get("headless", False))


def _handle_open(tool_input: dict, context: dict) -> str:
    return browser_open(tool_input["url"], _headless(context))


def _handle_screenshot(tool_input: dict, context: dict) -> str:
    return browser_screenshot(_headless(context))


def _handle_click(tool_input: dict, context: dict) -> str:
    return browser_click(tool_input["selector"], _headless(context))


def _handle_type(tool_input: dict, context: dict) -> str:
    return browser_type(tool_input["selector"], tool_input["text"], _headless(context))


def _handle_get_text(tool_input: dict, context: dict) -> str:
    return browser_get_text(_headless(context))


def get_tool_specs() -> list[dict]:
    return [
        {
            "definition": TOOL_OPEN,
            "handler": _handle_open,
        },
        {
            "definition": TOOL_SCREENSHOT,
            "handler": _handle_screenshot,
        },
        {
            "definition": TOOL_CLICK,
            "handler": _handle_click,
        },
        {
            "definition": TOOL_TYPE,
            "handler": _handle_type,
        },
        {
            "definition": TOOL_GET_TEXT,
            "handler": _handle_get_text,
        },
    ]
