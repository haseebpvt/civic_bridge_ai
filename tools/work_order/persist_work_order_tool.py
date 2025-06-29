import os
import json
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
from dotenv import load_dotenv

from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission
from langchain_ibm import ChatWatsonx
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()


class WorkOrderInfo(BaseModel):
    date: str = Field(description="Date of the work")
    time: str = Field(description="Time of the work")
    title: str = Field(description="Title of the work order")
    description: str = Field(description="Summarized one sentence description of the work")
    priority: str = Field(description="Priority of the work (High, Medium, Low)")
    status: str = Field(description="Status of the work (open, scheduled, done)")
    pdfUrl: str = Field(description="URL to the PDF document", default="")


@tool(
    name="persist_work_order_tool",
    description="Given generated work order, extract the key information from work order and persist in database.",
    permission=ToolPermission.READ_ONLY,
)
def persist_work_order_tool(work_order: str, pdf_url: str = ""):
    # Extract information
    extracted_info = _get_inference(work_order)

    # Write to Firebase Realtime database
    try:
        # Initialize Firebase if not already initialized
        _initialize_firebase()
        
        # Generate a unique work order ID in the format wo_YYYYMMDD_XXX
        work_order_id = _generate_work_order_id()
        
        # Add the generated ID and PDF URL to the extracted info
        extracted_info['id'] = work_order_id
        extracted_info['pdfUrl'] = pdf_url
        
        # Get reference to orders in Firebase Realtime Database
        ref = db.reference('orders')
        
        # Set the work order data with the custom ID
        ref.child(work_order_id).set(extracted_info)
        
        return {
            "success": True,
            "message": f"Work order successfully persisted to Firebase",
            "order_id": work_order_id,
            "data": extracted_info
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to persist work order: {str(e)}",
            "data": extracted_info
        }
    

def _get_inference(prompt: str):
    # Set Watson AI API key from environment variable
    watsonx_apikey = os.getenv("WATSONX_APIKEY")
    if not watsonx_apikey:
        raise ValueError("WATSONX_APIKEY not found in environment variables. Please check your .env file.")
    
    os.environ["WATSONX_APIKEY"] = watsonx_apikey

    chat = ChatWatsonx(
        model_id="ibm/granite-3-3-8b-instruct",
        url=os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com"),
        project_id=os.getenv("WATSONX_PROJECT_ID"),
    )

    parser = chat.with_structured_output(schema=WorkOrderInfo)

    result: WorkOrderInfo = parser.invoke(prompt)

    return result.model_dump()


def _initialize_firebase():
    """Initialize Firebase Admin SDK if not already initialized
    
    This function handles multiple authentication scenarios:
    1. Local Service Account File - Uses the bundled service account key file
    2. Service Account Key Content (JSON string in environment variable) - Best for cloud deployment
    3. Service Account Key File Path - Good for local development with custom key files  
    4. Application Default Credentials - Good for local development with gcloud auth
    """
    if not firebase_admin._apps:
        database_url = os.environ.get('FIREBASE_DATABASE_URL', 'https://test-d9354.firebaseio.com')
        
        # Option 1: Local Service Account File (bundled with the code)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        local_service_account_path = os.path.join(current_dir, 'test-d9354-firebase-adminsdk-81jqs-4159a720ab.json')
        if os.path.exists(local_service_account_path):
            try:
                cred = credentials.Certificate(local_service_account_path)
                firebase_admin.initialize_app(cred, {'databaseURL': database_url})
                print("Firebase initialized with local service account file")
                return
            except Exception as e:
                print(f"Failed to initialize Firebase with local service account file: {e}")
        
        # Option 2: Service Account Key Content (JSON string) - RECOMMENDED for cloud deployment
        service_account_content = os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON')
        if service_account_content:
            try:
                service_account_info = json.loads(service_account_content)
                cred = credentials.Certificate(service_account_info)
                firebase_admin.initialize_app(cred, {'databaseURL': database_url})
                print("Firebase initialized with service account key content")
                return
            except (json.JSONDecodeError, Exception) as e:
                print(f"Failed to initialize Firebase with service account content: {e}")
        
        # Option 3: Service Account Key File Path  
        service_account_key_path = os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY_PATH')
        if service_account_key_path and os.path.exists(service_account_key_path):
            try:
                cred = credentials.Certificate(service_account_key_path)
                firebase_admin.initialize_app(cred, {'databaseURL': database_url})
                print("Firebase initialized with service account key file")
                return
            except Exception as e:
                print(f"Failed to initialize Firebase with service account file: {e}")
        
        # Option 4: Application Default Credentials (for local development)
        try:
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred, {'databaseURL': database_url})
            print("Firebase initialized with Application Default Credentials") 
            return
        except Exception as e:
            print(f"Failed to initialize Firebase with Application Default Credentials: {e}")
        
        # If all methods fail, raise an informative error
        raise Exception(
            "Firebase credentials not found. Please ensure the service account file exists in the tools/work_order directory, "
            "or set FIREBASE_SERVICE_ACCOUNT_JSON environment variable for cloud deployment, "
            "or run 'gcloud auth application-default login' for local development. "
            f"Database URL: {database_url}"
        )


def _generate_work_order_id():
    """Generate a unique work order ID in the format wo_YYYYMMDD_XXX"""
    # Get current date in YYYYMMDD format
    current_date = datetime.now().strftime("%Y%m%d")
    
    # Get reference to orders in Firebase
    ref = db.reference('orders')
    
    # Get all existing orders
    orders = ref.get() or {}
    
    # Find the highest sequence number for today's date
    max_sequence = 0
    date_prefix = f"wo_{current_date}_"
    
    for order_id in orders.keys():
        if order_id.startswith(date_prefix):
            try:
                # Extract the sequence number (last 3 digits)
                sequence_str = order_id.split('_')[-1]
                sequence_num = int(sequence_str)
                max_sequence = max(max_sequence, sequence_num)
            except (ValueError, IndexError):
                continue
    
    # Generate next sequence number
    next_sequence = max_sequence + 1
    
    # Format as wo_YYYYMMDD_XXX (pad sequence to 3 digits)
    return f"wo_{current_date}_{next_sequence:03d}"
