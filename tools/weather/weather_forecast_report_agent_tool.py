import json

from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission


@tool(
    name="generate_weather_forecast_report_tool",
    description="Generate weather forcast report per day.",
    permission=ToolPermission.READ_ONLY,
)
def generate_weather_forecast_report_tool(weather_forcast_json: str):
    '''
    Generate weather forcast report for each day.

    :param weather_forcast_json: Input json containing weather report of the day
    :return: String containing human-readable report of weather
    '''

    json_data = json.loads(weather_forcast_json)

    result = _extract_weather_info(json_data["list"])

    pass


def _extract_weather_info(list_data):
    result = []

    for item in list_data:
        try:
            date = item["dt_txt"]
            weather_object = item["weather"][0]
            weather = f'{weather_object["main"]}, {weather_object["description"]}'

            text = f"{date} - {weather}"

            result.append(text)
        except Exception as e:
            print(e)

    return result
