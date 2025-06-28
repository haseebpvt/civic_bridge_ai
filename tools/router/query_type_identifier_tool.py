import os
from typing import Literal

from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission
from langchain_ibm import ChatWatsonx
from pydantic import BaseModel, Field


class QueryType(BaseModel):
    query_type: Literal[
        "infrastructure_issue",
        "information_request",
        "casual_conversation",
    ] = Field(
        ...,
        description="Category of the user’s input, one of the predefined issue or query types.",
        example="infrastructure_issue"
    )
    query: str = Field(description="Users query as it is")
    location: str = Field(
        description="If there is a location specified this field will be populated or else this field will have null value."
    )


@tool(
    name="query_type_identifier_tool",
    description="Given users query it returns the type of users query.",
    permission=ToolPermission.READ_ONLY,
)
def query_type_identifier_tool(query: str):
    result = _get_inference(query)

    return result


def _get_inference(prompt: str):
    os.environ["WATSONX_APIKEY"] = "ZA9eEpcQJFUqjvtLAAxbuvWmUgTlbyXWqVVmM3Nq3FwD"

    chat = ChatWatsonx(
        model_id="ibm/granite-3-3-8b-instruct",
        url="https://us-south.ml.cloud.ibm.com",
        project_id="bb2a1719-9aa6-497c-a167-8389bde3c92e",
    )

    parser = chat.with_structured_output(schema=QueryType)

    result: QueryType = parser.invoke(prompt)

    return result.model_dump()

