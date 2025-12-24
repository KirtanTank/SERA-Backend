from src.tools.registry import register_tool
from src.tools.actions import get_current_time, get_weather

register_tool("get_current_time", get_current_time)
register_tool("get_weather", get_weather)
