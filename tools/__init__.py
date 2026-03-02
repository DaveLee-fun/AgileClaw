"""
Tool registry with auto-discovery.

Each module under tools/ can expose:
  get_tool_specs() -> list[dict]

Spec format:
  {
      "definition": {... Claude tool schema ...},
      "handler": callable,  # (tool_input: dict, context: dict) -> str
  }
"""
from importlib import import_module
import pkgutil
from typing import Callable


ToolHandler = Callable[[dict, dict], str]


def _iter_tool_modules():
    for _, module_name, _ in pkgutil.iter_modules(__path__):
        if module_name.startswith("_"):
            continue
        yield module_name


def load_tools() -> tuple[list[dict], dict[str, ToolHandler], list[str]]:
    """
    Auto-load all tool modules and return:
      - tool definitions for Claude
      - mapping: tool_name -> handler
      - loading errors (non-fatal)
    """
    definitions: list[dict] = []
    handlers: dict[str, ToolHandler] = {}
    errors: list[str] = []

    for module_name in _iter_tool_modules():
        try:
            module = import_module(f"{__name__}.{module_name}")
        except Exception as exc:
            errors.append(f"{module_name}: import failed ({exc})")
            continue

        get_specs = getattr(module, "get_tool_specs", None)
        if not callable(get_specs):
            continue

        try:
            specs = get_specs() or []
        except Exception as exc:
            errors.append(f"{module_name}: get_tool_specs failed ({exc})")
            continue

        for spec in specs:
            definition = spec.get("definition")
            handler = spec.get("handler")
            if not definition or not callable(handler):
                errors.append(f"{module_name}: invalid tool spec")
                continue
            tool_name = definition.get("name")
            if not tool_name:
                errors.append(f"{module_name}: tool definition missing name")
                continue
            if tool_name in handlers:
                errors.append(f"{module_name}: duplicate tool name '{tool_name}'")
                continue
            definitions.append(definition)
            handlers[tool_name] = handler

    return definitions, handlers, errors
