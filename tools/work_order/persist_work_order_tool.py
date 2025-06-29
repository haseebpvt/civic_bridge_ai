import os
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission
from langchain_ibm import ChatWatsonx
from pydantic import BaseModel, Field


class WorkOrderInfo(BaseModel):
    date: str = Field(description="Date of the work")
    time: str = Field(description="Time of the work")
    title: str = Field(description="Title of the work order")
    description: str = Field(description="Detailed description of the work")
    priority: str = Field(description="Priority of the work (High, Medium, Low)")
    status: str = Field(description="Status of the work (open, scheduled, done)")
    pdfUrl: str = Field(description="URL to the PDF document", default="")


@tool(
    name="persist_work_order_tool",
    description="Given generated work order, extract the key information from work order and persist in database.",
    permission=ToolPermission.READ_ONLY,
)
def persist_work_order_tool(work_order: str):
    # Extract information
    extracted_info = _get_inference(work_order)

    # Write to Firebase Realtime database
    try:
        # Initialize Firebase if not already initialized
        _initialize_firebase()
        
        # Generate a unique work order ID in the format wo_YYYYMMDD_XXX
        work_order_id = _generate_work_order_id()
        
        # Add the generated ID to the extracted info
        extracted_info['id'] = work_order_id
        
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
    os.environ["WATSONX_APIKEY"] = "ZA9eEpcQJFUqjvtLAAxbuvWmUgTlbyXWqVVmM3Nq3FwD"

    chat = ChatWatsonx(
        model_id="ibm/granite-3-3-8b-instruct",
        url="https://us-south.ml.cloud.ibm.com",
        project_id="bb2a1719-9aa6-497c-a167-8389bde3c92e",
    )

    parser = chat.with_structured_output(schema=WorkOrderInfo)

    result: WorkOrderInfo = parser.invoke(prompt)

    return result.model_dump()


def _initialize_firebase():
    """Initialize Firebase Admin SDK if not already initialized"""
    if not firebase_admin._apps:
        # You can initialize with default credentials or specify a service account key
        # Option 1: Use default credentials (if running on Google Cloud or with GOOGLE_APPLICATION_CREDENTIALS env var)
        try:
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred, {
                'databaseURL': os.environ.get('FIREBASE_DATABASE_URL', 'https://test-d9354.firebaseio.com')
            })
        except Exception:
            # Option 2: Use service account key file (you need to set the path)
            service_account_key_path = os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY', 'path/to/serviceAccountKey.json')
            if os.path.exists(service_account_key_path):
                cred = credentials.Certificate(service_account_key_path)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': os.environ.get('FIREBASE_DATABASE_URL', 'https://test-d9354.firebaseio.com')
                })
            else:
                raise Exception("Firebase credentials not found. Please set GOOGLE_APPLICATION_CREDENTIALS environment variable or provide FIREBASE_SERVICE_ACCOUNT_KEY path.")


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
