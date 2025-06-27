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
    pass
