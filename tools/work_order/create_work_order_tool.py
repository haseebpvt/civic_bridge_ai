import os

from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission
from langchain_ibm import WatsonxLLM


@tool(
    name="work_order_creation_tool",
    description="Creates a work order with the available date based on weather condition.",
    permission=ToolPermission.READ_ONLY,
)
def create_work_order(weather_details: str):
    prompt = f'''
    Using the weather suggestion from below, create a work order with issue type, location, date, time range, weather condition on that time range in markdown format.
    
    [WEATHER SUGGESTION]
    {weather_details}
    
    [Example]
    Work Order:
    Issue Type: Pothole
    Location: Banglore
    Description: A pothole is reported in Banglore city area. 
    Suggested Repair Date: June 30th
    Suggested Repair Time: 9:00 AM
    '''

    result = _get_inference(prompt)

    return result


def _get_inference(prompt: str):
    os.environ["WATSONX_APIKEY"] = "ZA9eEpcQJFUqjvtLAAxbuvWmUgTlbyXWqVVmM3Nq3FwD"

    llm = WatsonxLLM(
        model_id="ibm/granite-3-8b-instruct",
        url="https://us-south.ml.cloud.ibm.com",
        project_id="bb2a1719-9aa6-497c-a167-8389bde3c92e",
        params={GenParams.MAX_NEW_TOKENS: 5000},
    )

    response = llm.invoke(prompt)

    return response
