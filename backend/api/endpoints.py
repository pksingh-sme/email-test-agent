"""
API Endpoints for the Email QA Agentic Platform
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse
from typing import List, Dict, Any
from pydantic import BaseModel
import os
import uuid
from connectors.email_on_acid import EmailOnAcidConnector
from agent_orchestrator import AgentOrchestrator

# Initialize router
router = APIRouter()

# Initialize services
try:
    email_connector = EmailOnAcidConnector()
    agent_orchestrator = AgentOrchestrator()
except Exception as e:
    print(f"Warning: Could not initialize services: {e}")
    email_connector = None
    agent_orchestrator = None


class QARequest(BaseModel):
    email_id: str


class QAResponse(BaseModel):
    report: Dict[str, Any]


# GET /emails - list of proofs from Email on Acid
@router.get("/emails", response_model=List[Dict[str, Any]])
async def get_emails():
    """Fetch list of email proofs from Email on Acid"""
    if not email_connector:
        raise HTTPException(status_code=500, detail="Email connector not initialized")
    
    try:
        emails = email_connector.get_email_list()
        return emails
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch emails: {str(e)}")


# GET /emails/{id} - full HTML + metadata
@router.get("/emails/{email_id}", response_model=Dict[str, Any])
async def get_email_details(email_id: str):
    """Fetch full HTML and metadata for a specific email"""
    if not email_connector:
        raise HTTPException(status_code=500, detail="Email connector not initialized")
    
    try:
        email_details = email_connector.get_email_details(email_id)
        return email_details
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch email details: {str(e)}")


# POST /emails/{id}/qa - run QA (deterministic + agentic)
@router.post("/emails/{email_id}/qa", response_model=QAResponse)
async def run_qa(email_id: str, request: QARequest):
    """Run QA process (deterministic + agentic) for an email"""
    if not email_connector or not agent_orchestrator:
        raise HTTPException(status_code=500, detail="Services not initialized")
    
    try:
        # Fetch email details
        email_details = email_connector.get_email_details(email_id)
        
        # Run QA process
        report = agent_orchestrator.run_qa_process(
            email_id,
            email_details["html_content"],
            email_details["metadata"]
        )
        
        return QAResponse(report=report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"QA process failed: {str(e)}")


# GET /reports/{id} - fetch saved report
@router.get("/reports/{report_id}", response_model=Dict[str, Any])
async def get_report(report_id: str):
    """Fetch saved QA report"""
    # This is a placeholder - in a real implementation, this would fetch
    # a saved report from a database
    return {
        "report_id": report_id,
        "status": "placeholder",
        "message": "Report fetching not implemented in this placeholder"
    }


# POST /upload - upload HTML file for QA analysis
@router.post("/upload")
async def upload_email_html(file: UploadFile = File(...)):
    """Upload HTML file for QA analysis"""
    if not agent_orchestrator:
        raise HTTPException(status_code=500, detail="Agent orchestrator not initialized")
    
    try:
        # Create uploads directory if it doesn't exist
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_path = os.path.join(upload_dir, f"{file_id}.html")
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Extract HTML content and basic metadata
        html_content = content.decode('utf-8')
        metadata = {
            "subject": "Uploaded Email",
            "preheader": "Uploaded HTML file for QA analysis",
            "template_name": file.filename or "Uploaded Email",
            "locale": "en-US"
        }
        
        # Run QA process
        report = agent_orchestrator.run_qa_process(
            file_id,
            html_content,
            metadata
        )
        
        # Clean up uploaded file
        os.remove(file_path)
        
        return {"report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process uploaded file: {str(e)}")


# GET /upload - show upload form
@router.get("/upload", response_class=HTMLResponse)
async def upload_form():
    """Show HTML upload form"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Email QA Upload</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 600px; margin: 0 auto; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input[type="file"] { display: block; margin-bottom: 10px; }
            button { background-color: #0085FF; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background-color: #0066cc; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Upload Email HTML for QA Analysis</h1>
            <form action="/api/v1/upload" method="post" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="file">Select HTML File:</label>
                    <input type="file" name="file" accept=".html,.htm" required>
                </div>
                <button type="submit">Upload and Analyze</button>
            </form>
        </div>
    </body>
    </html>
    """