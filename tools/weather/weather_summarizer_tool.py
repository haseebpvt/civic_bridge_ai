import os

from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission
from langchain_ibm import WatsonxLLM


@tool(
    name="weather_summarizer_tool",
    description="Given weather data in JSON format, write a one paragraph concise weather summary.",
    permission=ToolPermission.READ_ONLY,
)
def get_weather_summary(data: str):
    prompt = f'''
    From the JSON data below, generate a short, one-paragraph weather summary with only the most important information. 
    Convert all temperatures from Fahrenheit to Celsius and show only the Celsius values. 
    Do not include any additional text beyond the summary.
    
    [JSON DATA]
    {data}
    '''

    result = get_inference(prompt=prompt)

    return result


def get_inference(prompt: str):
    os.environ["WATSONX_APIKEY"] = "ZA9eEpcQJFUqjvtLAAxbuvWmUgTlbyXWqVVmM3Nq3FwD"

    llm = WatsonxLLM(
        model_id="ibm/granite-3-8b-instruct",
        url="https://us-south.ml.cloud.ibm.com",
        project_id="bb2a1719-9aa6-497c-a167-8389bde3c92e",
        params={GenParams.MAX_NEW_TOKENS: 5000},
    )

    response = llm.invoke(prompt)

    return response
