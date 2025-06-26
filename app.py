import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ibm import ChatWatsonx
from langgraph.graph import START, StateGraph

os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGSMITH_API_KEY"] = "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"
os.environ["LANGSMITH_PROJECT"] = "pr-flowery-paperwork-57"
os.environ["WATSONX_APIKEY"] = "QERQOCPJVu_qRCsnU8Oo276IYNosaGXCTyX7i945bYQq"

model = ChatWatsonx(
    model_id="ibm/granite-3-3-8b-instruct",
    url="https://us-south.ml.cloud.ibm.com",
    project_id="bb2a1719-9aa6-497c-a167-8389bde3c92e"
)

# result = model.invoke([
#     SystemMessage("You are a useful assistant"),
#     HumanMessage("I’m having trouble with my computer. I can’t seem to get an external display to work."),
# ])
#
# print(result.content)

# class

builder = StateGraph()