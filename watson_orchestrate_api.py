import http.client
import json
import logging
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WatsonOrchestrateAPI:
    def __init__(self,
                 bearer_token: str,
                 host: str = "api.au-syd.watson-orchestrate.cloud.ibm.com",
                 instance_id: str = "dbbdab2a-ba67-4d21-b8a7-ca02baaca8bf",
                 orchestration_id: str = "863a8415-e2ae-430e-9e02-5a9baf9d9d19"):
        """
        Initialize Watson Orchestrate API client
        
        Args:
            bearer_token: IBM Watson Orchestrate bearer token
            host: API host URL
            instance_id: Watson Orchestrate instance ID
            orchestration_id: Orchestration ID for the specific workflow
        """
        self.bearer_token = bearer_token
        self.host = host
        self.instance_id = instance_id
        self.orchestration_id = orchestration_id
        self.endpoint = f"/instances/{instance_id}/v1/orchestrate/{orchestration_id}/chat/completions"

    def send_message(self, text: str) -> Optional[Dict[Any, Any]]:
        """
        Send a message to Watson Orchestrate API
        
        Args:
            text: The text message to send
            
        Returns:
            Dictionary containing the API response or None if error occurred
        """
        try:
            conn = http.client.HTTPSConnection(self.host)

            payload = json.dumps({
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "response_type": "text",
                                "text": text,
                                "channels": [
                                    {
                                        "channel": "chat"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            })

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.bearer_token}'
            }

            logger.info(f"Sending message to Watson Orchestrate: {text[:100]}...")
            conn.request("POST", self.endpoint, payload, headers)

            res = conn.getresponse()
            data = res.read()

            if res.status == 200:
                response_data = json.loads(data.decode("utf-8"))
                logger.info("Successfully received response from Watson Orchestrate")
                return response_data
            else:
                logger.error(f"Watson Orchestrate API error: HTTP {res.status}")
                logger.error(f"Response: {data.decode('utf-8')}")
                return None

        except Exception as e:
            logger.error(f"Error calling Watson Orchestrate API: {str(e)}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()


# Load credentials from environment variables
WATSON_BEARER_TOKEN = os.getenv("WATSON_BEARER_TOKEN")
WATSON_ORCHESTRATE_HOST = os.getenv("WATSON_ORCHESTRATE_HOST", "api.au-syd.watson-orchestrate.cloud.ibm.com")
WATSON_ORCHESTRATE_INSTANCE_ID = os.getenv("WATSON_ORCHESTRATE_INSTANCE_ID")
WATSON_ORCHESTRATE_ORCHESTRATION_ID = os.getenv("WATSON_ORCHESTRATE_ORCHESTRATION_ID")

if not WATSON_BEARER_TOKEN:
    raise ValueError("Watson credentials not found in environment variables. Please check your .env file.")

# Create default instance
watson_api = WatsonOrchestrateAPI(
    bearer_token=WATSON_BEARER_TOKEN,
    host=WATSON_ORCHESTRATE_HOST,
    instance_id=WATSON_ORCHESTRATE_INSTANCE_ID,
    orchestration_id=WATSON_ORCHESTRATE_ORCHESTRATION_ID
)


def send_to_watson(text: str) -> Optional[str]:
    """
    Convenience function to send text to Watson Orchestrate and get response
    
    Args:
        text: The text to send
        
    Returns:
        String response from Watson or None if error occurred
    """
    response = watson_api.send_message(text)
    if response:
        # Extract the response text from the Watson response
        # This may need to be adjusted based on the actual response structure
        try:
            # Assuming the response has a choices array with message content
            if 'choices' in response and len(response['choices']) > 0:
                return response['choices'][0]['message']['content']
            elif 'content' in response:
                return response['content']
            else:
                return str(response)  # Return full response as string if structure is different
        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing Watson response: {e}")
            return str(response)  # Return full response as fallback
    return None


if __name__ == '__main__':
    api = WatsonOrchestrateAPI(bearer_token=WATSON_BEARER_TOKEN)
    api.send_message("There is a broken street light in Thrissur")