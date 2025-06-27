import datetime
import json

from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission


@tool(
    name="weather_forcast_summarizer_tool",
    description="Given the weather forcast JSON (as string or dict), returns the human readable summary of forcast.",
    permission=ToolPermission.READ_ONLY,
)
def summarize_forecast_tool(data):
    """
    Takes the full OpenWeatherMap forecast JSON (as string or dict) and returns a list of human-readable strings.
    Each entry includes:
      - Day of week
      - Date and time (12‑hour format)
      - Weather description
      - Rain chance category and percentage
      - Rain volume in mm
    """
    # Parse JSON string if input is a string
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError as e:
            return [f"Error parsing JSON: {str(e)}"]
    
    # Validate that data is now a dictionary
    if not isinstance(data, dict):
        return ["Error: Input must be a JSON string or dictionary"]
    
    summaries = []
    for entry in data.get("list", []):
        # Parse timestamp
        dt_txt = entry.get("dt_txt")
        if not dt_txt:
            continue
            
        try:
            dt = datetime.datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
            
        day = dt.strftime("%A")
        time = dt.strftime("%I:%M %p").lstrip("0")

        # Precipitation probability and volume
        pop = entry.get("pop", 0)
        rain_vol = entry.get("rain", {}).get("3h", 0)

        # Weather description
        weather = entry.get("weather", [{}])[0]
        desc = weather.get("description", "No data").capitalize()

        # Categorize rain chance
        pop_pct = int(pop * 100)
        if pop < 0.3:
            pop_text = f"Low ({pop_pct}%)"
        elif pop < 0.6:
            pop_text = f"Moderate ({pop_pct}%)"
        else:
            pop_text = f"High ({pop_pct}%)"

        # Format summary
        summary = (
            f"{day}, {dt.date()} at {time}: {desc}. "
            f"Rain chance: {pop_text}. "
            f"Rain volume: {rain_vol} mm."
        )
        summaries.append(summary)
    return summaries
