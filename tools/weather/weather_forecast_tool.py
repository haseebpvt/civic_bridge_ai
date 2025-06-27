import http.client
import json

from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission


@tool(
    name="weather_forecast_tool",
    description="Given the city name, returns the upcoming days weather forecast in JSON format, filtered for outdoor work scheduling (rain data only).",
    permission=ToolPermission.READ_ONLY,
)
def get_weather_forecast(city: str):
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
    
    try:
        # Parse the full response
        full_forecast = json.loads(data.decode("utf-8"))
        
        # Check if the API returned an error
        if "cod" in full_forecast and str(full_forecast["cod"]) != "200":
            return json.dumps({"error": f"Weather API error: {full_forecast.get('message', 'Unknown error')}"})
        
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
            # Handle missing weather data gracefully
            weather_data = entry.get("weather", [{}])[0] if entry.get("weather") else {}
            
            filtered_entry = {
                "dt": entry.get("dt"),
                "dt_txt": entry.get("dt_txt"),
                "pop": entry.get("pop", 0),  # probability of precipitation (0-1)
                "weather": [
                    {
                        "main": weather_data.get("main", "Unknown"),
                        "description": weather_data.get("description", "No description")
                    }
                ]
            }
            
            # Only include rain data if it exists
            if "rain" in entry:
                filtered_entry["rain"] = entry["rain"]
                
            filtered_forecast["list"].append(filtered_entry)
        
        return json.dumps(filtered_forecast)
        
    except json.JSONDecodeError as e:
        return json.dumps({"error": f"Failed to parse weather data: {str(e)}"})
    except Exception as e:
        return json.dumps({"error": f"Weather tool error: {str(e)}"})


if __name__ == '__main__':
    result = get_weather_forecast("Kakkanad")

    print(result)