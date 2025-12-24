import json
from src.tools.registry import get_tool

def execute_tool(tool_call):
    name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    tool = get_tool(name)
    if not tool:
        raise ValueError(f"Tool {name} not found")

    return tool(arguments)
