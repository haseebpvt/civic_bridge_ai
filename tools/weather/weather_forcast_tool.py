import http.client

from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission


@tool(
    name="weather_forcast_tool",
    description="Given the city name, returns the upcoming days weather forcast in JSON format.",
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

    return data.decode("utf-8")
