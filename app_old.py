import os
from dotenv import load_dotenv

from langchain_ibm import ChatWatsonx
from langgraph.graph import StateGraph

# Load environment variables
load_dotenv()

# Set environment variables from .env file
os.environ["LANGSMITH_TRACING"] = os.getenv("LANGSMITH_TRACING", "true")
os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY", "")
os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "")
os.environ["WATSONX_APIKEY"] = os.getenv("WATSONX_APIKEY", "")

model = ChatWatsonx(
    model_id="ibm/granite-3-3-8b-instruct",
    url=os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com"),
    project_id=os.getenv("WATSONX_PROJECT_ID", "")
)

# result = model.invoke([
#     SystemMessage("You are a useful assistant"),
#     HumanMessage("I’m having trouble with my computer. I can’t seem to get an external display to work."),
# ])
#
# print(result.content)

# class

builder = StateGraph()
