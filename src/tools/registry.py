from typing import Dict, Callable

TOOLS: Dict[str, Callable] = {}

def register_tool(name: str, handler: Callable):
    TOOLS[name] = handler

def get_tool(name: str):
    return TOOLS.get(name)
