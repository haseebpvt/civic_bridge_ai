import http.client

from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission


@tool(
    name="get_current_weather_tool",
    description="Fetch weather data from the internet and return JSON.",
    permission=ToolPermission.READ_ONLY
)
def get_current_weather(city: str):
    conn = http.client.HTTPSConnection("api.openweathermap.org")
    payload = ''
    headers = {}
    conn.request(
        "GET",
        f"/data/2.5/weather?q={city}&appid=168a339fbced32209eb9dc154da05cfa",
        payload,
        headers
    )
    res = conn.getresponse()
    data = res.read()

    return data.decode("utf-8")
