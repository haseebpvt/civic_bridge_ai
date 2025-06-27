import json
from typing import Union, Dict, Any

from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission


@tool(
    name="generate_weather_forecast_report_tool",
    description="Generate a human-readable multi-day weather forecast report.",
    permission=ToolPermission.READ_ONLY,
)
def generate_weather_forecast_report_tool(
        forecast_data: Any
) -> str:
    """
    :param forecast_data: Either a JSON string or a Python dict containing the full forecast JSON.
    :return: A newline-separated, human-readable per-day report.
    """
    # if we got a string, parse it; otherwise assume it's already a dict
    if isinstance(forecast_data, str):
        data = json.loads(forecast_data)
    else:
        data = forecast_data

    # extract the list of time slots
    entries = data.get("list", [])
    report_lines = []
    for item in entries:
        dt = item.get("dt_txt", "<unknown time>")
        weather = item.get("weather", [{}])[0]
        main = weather.get("main", "Unknown")
        desc = weather.get("description", "")
        report_lines.append(f"{dt} – {main}, {desc}")

    return "\n".join(report_lines)
