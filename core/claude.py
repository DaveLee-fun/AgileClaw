"""
Claude API client wrapper.
Handles tool_use loop — sends messages, executes tool calls, returns final response.
"""
import anthropic
from typing import Any

class ClaudeClient:
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5", max_tokens: int = 4096):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens

    def chat(
        self,
        messages: list[dict],
        system: str,
        tools: list[dict],
        tool_executor,  # callable: (tool_name, tool_input) -> str
    ) -> str:
        """
        Run a full Claude conversation with tool_use loop.
        Returns the final text response.
        """
        while True:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system,
                messages=messages,
                tools=tools if tools else [],
            )

            # Collect text and tool_use blocks
            tool_uses = []
            text_parts = []
            for block in response.content:
                if block.type == "text":
                    text_parts.append(block.text)
                elif block.type == "tool_use":
                    tool_uses.append(block)

            # If no tool calls, we're done
            if response.stop_reason == "end_turn" or not tool_uses:
                return "\n".join(text_parts)

            # Execute all tool calls
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for tool_use in tool_uses:
                try:
                    result = tool_executor(tool_use.name, tool_use.input)
                except Exception as e:
                    result = f"Error: {e}"
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": str(result),
                })
            messages.append({"role": "user", "content": tool_results})
