import os

from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission
from langchain_ibm import WatsonxLLM


@tool(
    name="work_order_creation_tool",
    description="Creates a comprehensive work order with optimal scheduling based on weather conditions and issue details.",
    permission=ToolPermission.READ_ONLY,
)
def create_work_order(issue_type: str, location: str, issue_description: str = "", weather_details: str = ""):
    prompt = f'''
    Create a comprehensive work order for the reported issue with optimal scheduling based on weather conditions.
    
    [ISSUE DETAILS]
    Issue Type: {issue_type}
    Location: {location}
    Description: {issue_description}
    
    [WEATHER INFORMATION]
    {weather_details}
    
    Create a work order in markdown format that includes:
    - Issue identification and priority level
    - Optimal repair date and time based on weather
    - Required materials and crew size
    - Safety considerations
    - Expected duration
    - Weather conditions during scheduled time
    
    [Example Format]
    # Work Order #WO-{location.upper().replace(' ', '')}-001
    
    ## Issue Details
    - **Type**: {issue_type}
    - **Location**: {location}
    - **Priority**: [High/Medium/Low based on safety impact]
    - **Description**: {issue_description}
    
    ## Scheduling
    - **Recommended Date**: [Best weather window]
    - **Time Window**: [Optimal hours]
    - **Weather Conditions**: [Expected conditions]
    
    ## Resources Required
    - **Crew Size**: [Number of workers needed]
    - **Estimated Duration**: [Time to complete]
    - **Materials**: [List of required materials]
    
    ## Safety Notes
    - [Weather-related safety considerations]
    - [Equipment requirements]
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
