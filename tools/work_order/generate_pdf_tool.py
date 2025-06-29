import os
import tempfile
import uuid
from datetime import datetime

import firebase_admin
from firebase_admin import credentials, storage
from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission

# Import PDF generation functionality
try:
    import markdown
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    import re
except ImportError:
    print("Required packages not installed. Please install: pip install reportlab markdown")

@tool(
    name="generate_pdf_tool",
    description="Converts a markdown work order to PDF and uploads it to Firebase Storage, returning the public URL.",
    permission=ToolPermission.READ_ONLY,
)
def generate_pdf_tool(work_order_markdown: str, work_order_id: str = None):
    """
    Convert markdown work order to PDF and upload to Firebase Storage.
    
    Args:
        work_order_markdown: The work order content in markdown format
        work_order_id: Optional work order ID for naming the PDF file
        
    Returns:
        dict: Contains success status, message, and pdf_url if successful
    """
    try:
        # Initialize Firebase if not already initialized
        _initialize_firebase()
        
        # Generate a unique filename
        if not work_order_id:
            work_order_id = f"wo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        pdf_filename = f"{work_order_id}.pdf"
        
        # Create temporary file for PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            temp_pdf_path = temp_pdf.name
            
            # Convert Markdown to PDF using reportlab
            _create_pdf_from_markdown(work_order_markdown, temp_pdf_path)
            
            # Upload PDF to Firebase Storage
            bucket = storage.bucket()
            blob = bucket.blob(f"work_orders/{pdf_filename}")
            
            # Upload the file
            blob.upload_from_filename(temp_pdf_path)
            
            # Make the file publicly accessible
            blob.make_public()
            
            # Get the public URL
            pdf_url = blob.public_url
            
            # Clean up temporary file
            os.unlink(temp_pdf_path)
            
            return {
                "success": True,
                "message": f"PDF generated and uploaded successfully",
                "pdf_url": pdf_url,
                "filename": pdf_filename
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to generate and upload PDF: {str(e)}",
            "pdf_url": ""
        }


def _create_pdf_from_markdown(markdown_content: str, output_path: str):
    """Convert markdown content to PDF using reportlab."""
    
    # Create PDF document
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=18)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=12,
        textColor=colors.darkblue
    )
    
    normal_style = styles['Normal']
    
    # Story to hold the PDF content
    story = []
    
    # Add header
    story.append(Paragraph("Work Order Document", title_style))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
                          styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Parse markdown content
    lines = markdown_content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            story.append(Spacer(1, 6))
            continue
            
        # Handle headers
        if line.startswith('# '):
            story.append(Paragraph(line[2:], title_style))
        elif line.startswith('## '):
            story.append(Paragraph(line[3:], heading_style))
        elif line.startswith('### '):
            story.append(Paragraph(line[4:], styles['Heading3']))
        # Handle bullet points
        elif line.startswith('- '):
            # Process markdown formatting in bullet points
            formatted_line = _format_markdown_text(line[2:])
            story.append(Paragraph(f"• {formatted_line}", normal_style))
        # Handle regular text
        else:
            formatted_line = _format_markdown_text(line)
            if formatted_line:
                story.append(Paragraph(formatted_line, normal_style))
    
    # Add footer
    story.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.grey
    )
    story.append(Paragraph("This document was automatically generated by the Work Order Management System.", 
                          footer_style))
    
    # Build PDF
    doc.build(story)


def _format_markdown_text(text: str) -> str:
    """Format basic markdown text elements for reportlab."""
    # Bold text
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Italic text
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    # Remove markdown links but keep text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    return text


def _initialize_firebase():
    """Initialize Firebase Admin SDK if not already initialized"""
    if not firebase_admin._apps:
        # Try to use the same initialization logic as persist_work_order_tool
        database_url = os.environ.get('FIREBASE_DATABASE_URL', 'https://test-d9354.firebaseio.com')
        storage_bucket = os.environ.get('FIREBASE_STORAGE_BUCKET', 'test-d9354.appspot.com')
        
        # Option 1: Local Service Account File (bundled with the code)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        local_service_account_path = os.path.join(current_dir, 'test-d9354-firebase-adminsdk-81jqs-4159a720ab.json')
        if os.path.exists(local_service_account_path):
            try:
                cred = credentials.Certificate(local_service_account_path)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': database_url,
                    'storageBucket': storage_bucket
                })
                print("Firebase initialized with local service account file")
                return
            except Exception as e:
                print(f"Failed to initialize Firebase with local service account file: {e}")
        
        # Option 2: Service Account Key Content (JSON string)
        service_account_content = os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON')
        if service_account_content:
            try:
                import json
                service_account_info = json.loads(service_account_content)
                cred = credentials.Certificate(service_account_info)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': database_url,
                    'storageBucket': storage_bucket
                })
                print("Firebase initialized with service account key content")
                return
            except (json.JSONDecodeError, Exception) as e:
                print(f"Failed to initialize Firebase with service account content: {e}")
        
        # Option 3: Service Account Key File Path
        service_account_key_path = os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY_PATH')
        if service_account_key_path and os.path.exists(service_account_key_path):
            try:
                cred = credentials.Certificate(service_account_key_path)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': database_url,
                    'storageBucket': storage_bucket
                })
                print("Firebase initialized with service account key file")
                return
            except Exception as e:
                print(f"Failed to initialize Firebase with service account file: {e}")
        
        # Option 4: Application Default Credentials
        try:
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred, {
                'databaseURL': database_url,
                'storageBucket': storage_bucket
            })
            print("Firebase initialized with Application Default Credentials")
            return
        except Exception as e:
            print(f"Failed to initialize Firebase with Application Default Credentials: {e}")
        
        # If all methods fail, raise an informative error
        raise Exception(
            "Firebase credentials not found. Please ensure the service account file exists in the tools/work_order directory, "
            "or set FIREBASE_SERVICE_ACCOUNT_JSON environment variable for cloud deployment, "
            "or run 'gcloud auth application-default login' for local development. "
            f"Database URL: {database_url}, Storage Bucket: {storage_bucket}"
        ) 