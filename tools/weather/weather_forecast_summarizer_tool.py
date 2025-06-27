import os

from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission
from langchain_ibm import WatsonxLLM


@tool(
    name="weather_forecast_summarizer_tool",
    description="Given filtered weather forecast JSON, returns human-readable rain/weather summary",
    permission=ToolPermission.READ_ONLY,
)
def summarize_forecast_tool(data: str):
    prompt = f'''
        Given a JSON weather forecast with a city block and a list of forecast entries, extract the information into a human-readable markdown list. For each forecast entry, display the date and time (dt_txt), weather condition (main and description), probability of precipitation (pop as a percentage), and rainfall volume over 3 hours if available (rain["3h"]). Format the output in markdown as a bullet list, grouped by date, with each time entry indented under its respective date.

        [JSON DATA]
        {data}
        '''

    result = _get_inference(prompt=prompt)

    return result


def _get_inference(prompt: str):
    # Get API key and project ID from environment variables for security
    api_key = os.getenv("WATSONX_APIKEY")
    project_id = os.getenv("WATSONX_PROJECT_ID")
    
    if not api_key:
        raise ValueError("WATSONX_APIKEY environment variable not set")
    if not project_id:
        raise ValueError("WATSONX_PROJECT_ID environment variable not set")

    llm = WatsonxLLM(
        model_id="ibm/granite-3-8b-instruct",
        url="https://us-south.ml.cloud.ibm.com",
        project_id=project_id,
        params={GenParams.MAX_NEW_TOKENS: 5000},
    )

    response = llm.invoke(prompt)

    return response
