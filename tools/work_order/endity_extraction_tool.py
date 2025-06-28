import os
import json
import re
from typing import Optional

from pydantic import BaseModel, Field
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission
from langchain_ibm import WatsonxLLM


class IssueDetails(BaseModel):
    """Pydantic model for extracted issue details."""
    type_of_issue: str = Field(..., description="The type or category of the issue reported")
    location: str = Field(..., description="The location where the issue is occurring")
    description: Optional[str] = Field(None, description="Additional description of the issue")


@tool(
    name="extract_details_from_issue_tool",
    description="Extract issue type, location, description from the user query and return structured JSON output.",
    permission=ToolPermission.READ_ONLY,
)
def extract_details_from_issue(query: str) -> IssueDetails:
    """
    Extract issue details from user query using Pydantic for structured output.
    
    Args:
        query: The user's issue description
        
    Returns:
        IssueDetails: Pydantic model containing structured issue information
    """
    prompt = f'''
    You are an expert at extracting structured information from text. Given the user's query about an issue, extract the relevant information and format it as JSON.

    User Query: "{query}"

    Extract the following information:
    1. type_of_issue: What type of issue is being reported? (e.g., pothole, streetlight, water leak, garbage, noise, etc.)
    2. location: Where is the issue located?
    3. description: A brief description of the issue (optional)

    Response format - Return ONLY this JSON structure, no other text:
    {{
        "type_of_issue": "identified issue type",
        "location": "extracted location",
        "description": "brief description of the issue"
    }}

    Examples:
    - For "There is a pothole in downtown area" → {{"type_of_issue": "pothole", "location": "downtown area", "description": "There is a pothole in downtown area"}}
    - For "Streetlight not working on Main Street" → {{"type_of_issue": "streetlight", "location": "Main Street", "description": "Streetlight not working on Main Street"}}

    Now extract from: "{query}"
    
    JSON:
    '''

    response = _get_inference(prompt)
    
    try:
        # Clean up the response - remove any extra text
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            json_str = response[json_start:json_end]
            response_data = json.loads(json_str)
            issue_details = IssueDetails(**response_data)
            return issue_details
        else:
            raise ValueError("No valid JSON found in response")
            
    except (json.JSONDecodeError, ValueError) as e:
        # Fallback: try to extract basic information if JSON parsing fails
        print(f"JSON parsing failed: {e}. Attempting fallback extraction.")
        return _fallback_extraction(query)


def _fallback_extraction(query: str) -> IssueDetails:
    """
    Fallback extraction method when JSON parsing fails.
    
    Args:
        query: The user's issue description
        
    Returns:
        IssueDetails: Basic extracted information
    """
    # Simple keyword-based extraction as fallback
    query_lower = query.lower()
    
    # Common issue types
    issue_types = {
        'pothole': ['pothole', 'road damage', 'crater', 'hole in road'],
        'streetlight': ['streetlight', 'street light', 'lamp', 'lighting', 'light not working'],
        'water leak': ['water leak', 'pipe burst', 'water', 'plumbing'],
        'garbage': ['garbage', 'trash', 'waste', 'litter'],
        'noise': ['noise', 'loud', 'sound', 'disturbance'],
        'electrical': ['power', 'electricity', 'electrical', 'wire'],
        'other': []
    }
    
    detected_type = 'other'
    for issue_type, keywords in issue_types.items():
        if any(keyword in query_lower for keyword in keywords):
            detected_type = issue_type
            break
    
    # Improved location extraction
    location = 'location not specified'
    
    # Location patterns to look for
    location_patterns = [
        (r'\bin\s+([^.!?]+?)(?:\s+area|\s+street|\s+road|\.|\!|\?|$)', 'in '),
        (r'\bat\s+([^.!?]+?)(?:\s+area|\s+street|\s+road|\.|\!|\?|$)', 'at '),
        (r'\bnear\s+([^.!?]+?)(?:\s+area|\s+street|\s+road|\.|\!|\?|$)', 'near '),
        (r'\bon\s+([^.!?]+?)(?:\s+street|\s+road|\.|\!|\?|$)', 'on '),
        (r'([A-Za-z\s]+)(?:\s+area|\s+street|\s+road)', ''),
    ]
    
    for pattern, prefix in location_patterns:
        matches = re.findall(pattern, query, re.IGNORECASE)
        if matches:
            # Take the first match and clean it up
            potential_location = matches[0].strip()
            # Remove common words that might be captured
            stop_words = ['there', 'is', 'was', 'the', 'a', 'an', 'and', 'or', 'but']
            location_words = [word for word in potential_location.split() if word.lower() not in stop_words]
            if location_words:
                location = ' '.join(location_words)
                break
    
    return IssueDetails(
        type_of_issue=detected_type,
        location=location,
        description=query
    )


def _get_inference(prompt: str):
    os.environ["WATSONX_APIKEY"] = "ZA9eEpcQJFUqjvtLAAxbuvWmUgTlbyXWqVVmM3Nq3FwD"

    llm = WatsonxLLM(
        model_id="ibm/granite-3-3-8b-instruct",
        url="https://us-south.ml.cloud.ibm.com",
        project_id="bb2a1719-9aa6-497c-a167-8389bde3c92e",
        params={GenParams.MAX_NEW_TOKENS: 50},
    )

    response = llm.invoke(prompt)

    return response


if __name__ == '__main__':
    # Test cases
    test_queries = [
        "There is a pothole in Kakkanad area.",
        "The streetlight near the park is not working.",
        "Water leak on Main Street needs immediate attention.",
        "Garbage collection has not happened in downtown area for weeks.",
        "Loud noise from construction site at Industrial Avenue.",
        "Electrical wire hanging dangerously near the school."
    ]
    
    print("=== Entity Extraction Test Results ===\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"Test {i}: {query}")
        res = extract_details_from_issue(query)
        print("Extracted details:")
        print(res.model_dump_json(indent=2))
        print("-" * 50)