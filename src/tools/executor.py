import json
from src.tools.registry import get_tool


def execute_tool(tool_call):
    """
    Execute a registered tool.

    Supports two input formats:
    1) OpenAI tool_call object (from LLM)
    2) Backend-injected dict payload

    Expected formats:

    1) OpenAI tool_call:
       tool_call.function.name
       tool_call.function.arguments (JSON string)

    2) Backend dict:
       {
           "name": "tool_name",
           ...arguments,
           "user_id": "...",
           "session_id": "..."
       }
    """

    # -------------------------
    # Case 1: OpenAI tool_call
    # -------------------------
    if hasattr(tool_call, "function"):
        name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

    # -------------------------
    # Case 2: Backend dict
    # -------------------------
    elif isinstance(tool_call, dict):
        name = tool_call.get("name")
        if not name:
            raise ValueError("Tool name missing in execution payload")

        # Remove name before passing args to tool
        arguments = {k: v for k, v in tool_call.items() if k != "name"}

    else:
        raise TypeError("Invalid tool_call type passed to execute_tool")

    # -------------------------
    # Lookup tool
    # -------------------------
    tool = get_tool(name)
    if not tool:
        raise ValueError(f"Tool '{name}' not registered")

    # -------------------------
    # Execute tool safely
    # -------------------------
    try:
        return tool(arguments)
    except Exception as e:
        # Return structured error so LLM can respond gracefully
        return {
            "error": True,
            "tool": name,
            "message": str(e),
        }
