import http.client
import json
import os

from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission
from langchain_ibm import WatsonxLLM


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

        data = json.dumps(filtered_forecast)

        stripped_list = _summarise(data)

        prompt = f'''
        Please use the weather forcast data and summarize this day by day.
        There will be multiple weather weather data across next 5 days. Your job is to summarize each day weather. 
        
        [FORECAST]
        {stripped_list}
        '''

        summary = _get_inference(prompt)

        return summary

    except json.JSONDecodeError as e:
        return json.dumps({"error": f"Failed to parse weather data: {str(e)}"})
    except Exception as e:
        return json.dumps({"error": f"Weather tool error: {str(e)}"})


def _summarise(
        forecast_data: str
) -> str:
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


def _get_inference(prompt: str):
    os.environ["WATSONX_APIKEY"] = "ZA9eEpcQJFUqjvtLAAxbuvWmUgTlbyXWqVVmM3Nq3FwD"

    llm = WatsonxLLM(
        model_id="ibm/granite-3-3-8b-instruct",
        url="https://us-south.ml.cloud.ibm.com",
        project_id="bb2a1719-9aa6-497c-a167-8389bde3c92e",
        params={GenParams.MAX_NEW_TOKENS: 5000},
    )

    response = llm.invoke(prompt)

    return response


if __name__ == '__main__':
    res = _get_inference("Hello")
    print(res)
