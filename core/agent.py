"""
Main agent — the brain of AgileClaw.
Receives a message, thinks with Claude, uses tools, returns response.
"""
from core.claude import ClaudeClient
from core.memory import Memory
from tools import shell, files, web, browser
from agile.loop import AGILE_SYSTEM_PROMPT, build_agile_prompt

# All available tools
ALL_TOOLS = [
    shell.TOOL_DEFINITION,
    files.TOOL_READ,
    files.TOOL_WRITE,
    web.TOOL_DEFINITION,
    browser.TOOL_OPEN,
    browser.TOOL_SCREENSHOT,
    browser.TOOL_CLICK,
    browser.TOOL_TYPE,
    browser.TOOL_GET_TEXT,
]

SYSTEM_PROMPT = """You are AgileClaw — a personal AI agent with full access to the host machine.

You can:
- Run shell commands (shell tool)
- Read and write files (read_file, write_file tools)
- Fetch web pages (web_fetch tool)
- Control a browser (browser_open, browser_click, browser_type, browser_get_text, browser_screenshot tools)

You have memory of past conversations and the user's goals.

Be direct, efficient, and proactive. If you can do something, do it — don't just explain how.
Keep responses concise. Use Korean when the user writes in Korean.
"""


class Agent:
    def __init__(self, config: dict):
        self.claude = ClaudeClient(
            api_key=config["claude"]["api_key"],
            model=config["claude"].get("model", "claude-sonnet-4-5"),
            max_tokens=config["claude"].get("max_tokens", 4096),
        )
        self.memory = Memory(config["memory"]["dir"])
        self.headless = config.get("browser", {}).get("headless", False)

    def _tool_executor(self, tool_name: str, tool_input: dict) -> str:
        """Execute a tool call from Claude."""
        if tool_name == "shell":
            return shell.run(tool_input["command"], tool_input.get("timeout", 30))
        elif tool_name == "read_file":
            return files.read_file(tool_input["path"])
        elif tool_name == "write_file":
            return files.write_file(tool_input["path"], tool_input["content"])
        elif tool_name == "web_fetch":
            return web.fetch(tool_input["url"], tool_input.get("max_chars", 5000))
        elif tool_name == "browser_open":
            return browser.browser_open(tool_input["url"], self.headless)
        elif tool_name == "browser_screenshot":
            return browser.browser_screenshot(self.headless)
        elif tool_name == "browser_click":
            return browser.browser_click(tool_input["selector"], self.headless)
        elif tool_name == "browser_type":
            return browser.browser_type(tool_input["selector"], tool_input["text"], self.headless)
        elif tool_name == "browser_get_text":
            return browser.browser_get_text(self.headless)
        else:
            return f"Unknown tool: {tool_name}"

    def chat(self, user_message: str, chat_id: str = "default") -> str:
        """Process a user message and return the agent's response."""
        # Load conversation history
        history = self.memory.get_conversation_history(chat_id)

        # Load context
        context = self.memory.load_context()
        system = SYSTEM_PROMPT
        if context:
            system += f"\n\nContext:\n{context}"

        # Build messages
        messages = history.copy()
        messages.append({"role": "user", "content": user_message})

        # Save user message
        self.memory.save_message(chat_id, "user", user_message)
        self.memory.log(f"User: {user_message[:100]}", "chat")

        # Run Claude with tools
        response = self.claude.chat(
            messages=messages,
            system=system,
            tools=ALL_TOOLS,
            tool_executor=self._tool_executor,
        )

        # Save response
        self.memory.save_message(chat_id, "assistant", response)
        self.memory.log(f"Agent: {response[:100]}", "chat")

        return response

    def run_agile_review(self, chat_id: str = "default") -> str:
        """Run the agile loop — measure KPIs and suggest improvements."""
        goals = self.memory.load_goals()
        prompt = build_agile_prompt(goals)

        messages = [{"role": "user", "content": prompt}]
        response = self.claude.chat(
            messages=messages,
            system=AGILE_SYSTEM_PROMPT,
            tools=ALL_TOOLS,
            tool_executor=self._tool_executor,
        )
        self.memory.log(f"Agile review completed", "agile")
        return response
