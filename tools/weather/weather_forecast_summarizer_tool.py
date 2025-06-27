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
        Parse the following JSON weather forecast data and return ONLY a simple timeline of weather entries.

        JSON data to parse:
        {data}

        Return ONLY the timeline entries in this exact format (one entry per line):
        Date Time: Weather description (pop% chance of rain) - Rainfall: Xmm over 3h

        Do not include:
        - Any JSON data
        - Any labels like [OUTPUT] or [JSON DATA]  
        - Any explanations or additional text
        - Any markdown formatting
        - Any code examples

        Return only the plain text timeline entries, nothing else.
        '''

    result = _get_inference(prompt=prompt)

    return result


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
