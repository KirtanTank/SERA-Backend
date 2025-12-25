from typing import Dict, Callable

TOOLS: Dict[str, Callable] = {}


def register_tool(name: str, handler: Callable):
    if name in TOOLS:
        raise ValueError(f"Tool '{name}' is already registered")
    TOOLS[name] = handler


def get_tool(name: str):
    return TOOLS.get(name)


def list_tools():
    return list(TOOLS.keys())
