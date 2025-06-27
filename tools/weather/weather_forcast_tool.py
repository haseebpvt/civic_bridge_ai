import http.client
import json

from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission


@tool(
    name="weather_forcast_tool",
    description="Given the city name, returns the upcoming days weather forcast in JSON format, filtered for outdoor work scheduling (rain data only).",
    permission=ToolPermission.READ_ONLY,
)
def get_weather_forcast(city: str):
    conn = http.client.HTTPSConnection("api.openweathermap.org")
    payload = ''
    headers = {}
    conn.request(
        "GET",
        f"/data/2.5/forecast?q={city}&appid=168a339fbced32209eb9dc154da05cfa",
        payload,
        headers,
    )
    res = conn.getresponse()
    data = res.read()
    
    # Parse the full response
    full_forecast = json.loads(data.decode("utf-8"))
    
    # Filter to only essential fields for outdoor work scheduling
    filtered_forecast = {
        "city": {
            "name": full_forecast.get("city", {}).get("name"),
            "coord": full_forecast.get("city", {}).get("coord")
        },
        "list": []
    }
    
    # Filter each forecast entry to only rain-relevant data
    for entry in full_forecast.get("list", []):
        filtered_entry = {
            "dt": entry.get("dt"),
            "dt_txt": entry.get("dt_txt"),
            "pop": entry.get("pop"),  # probability of precipitation (0-1)
            "weather": [
                {
                    "main": entry.get("weather", [{}])[0].get("main"),
                    "description": entry.get("weather", [{}])[0].get("description")
                }
            ]
        }
        
        # Only include rain data if it exists
        if "rain" in entry:
            filtered_entry["rain"] = entry["rain"]
            
        filtered_forecast["list"].append(filtered_entry)
    
    return json.dumps(filtered_forecast)
