"""
API Endpoints for the Email QA Agentic Platform
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import HTMLResponse
from typing import List, Dict, Any
from pydantic import BaseModel
import os
import uuid
import json
from connectors.email_on_acid import EmailOnAcidConnector
from agent_orchestrator import AgentOrchestrator
from database.config import get_db
from database.models import EmailTemplate, QAReport, UploadRecord
from sqlalchemy.orm import Session

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
async def get_emails(db: Session = Depends(get_db)):
    """Fetch list of email proofs from Email on Acid and database"""
    if not email_connector:
        raise HTTPException(status_code=500, detail="Email connector not initialized")
    
    try:
        # Get emails from database (uploaded files)
        db_emails = db.query(EmailTemplate).all()
        emails = []
        
        for email in db_emails:
            metadata = email.get_metadata()
            emails.append({
                "id": email.id,
                "name": email.name,
                "created_at": email.created_at.isoformat() if email.created_at else "",
                "status": email.status
            })
        
        # Get emails from Email on Acid
        try:
            eo_emails = email_connector.get_email_list()
            emails.extend(eo_emails)
        except Exception as e:
            # If Email on Acid is not available, continue with database emails
            print(f"Warning: Could not fetch from Email on Acid: {e}")
        
        return emails
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch emails: {str(e)}")


# GET /emails/{id} - full HTML + metadata
@router.get("/emails/{email_id}", response_model=Dict[str, Any])
async def get_email_details(email_id: str, db: Session = Depends(get_db)):
    """Fetch full HTML and metadata for a specific email"""
    if not email_connector:
        raise HTTPException(status_code=500, detail="Email connector not initialized")
    
    try:
        # First try to get from database
        email_template = db.query(EmailTemplate).filter(EmailTemplate.id == email_id).first()
        if email_template:
            return {
                "id": email_template.id,
                "html_content": email_template.html_content,
                "metadata": email_template.get_metadata()
            }
        
        # If not in database, fetch from Email on Acid
        email_details = email_connector.get_email_details(email_id)
        return email_details
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch email details: {str(e)}")


# POST /emails/{id}/qa - run QA (deterministic + agentic)
@router.post("/emails/{email_id}/qa", response_model=QAResponse)
async def run_qa(email_id: str, request: QARequest, db: Session = Depends(get_db)):
    """Run QA process (deterministic + agentic) for an email"""
    if not email_connector or not agent_orchestrator:
        raise HTTPException(status_code=500, detail="Services not initialized")
    
    try:
        # Fetch email details
        email_details = await get_email_details(email_id, db)
        
        # Run QA process
        report = agent_orchestrator.run_qa_process(
            email_id,
            email_details["html_content"],
            email_details["metadata"]
        )
        
        # Save QA report to database
        # Convert report to JSON-serializable format
        try:
            serializable_report = json.loads(json.dumps(report, default=str))
        except Exception as serialize_error:
            # If serialization fails, create a simplified version
            serializable_report = {
                "overall_status": report.get("overall_status", "unknown"),
                "risk_score": report.get("risk_score", 0),
                "email_id": report.get("email_id", email_id),
                "message": "Full report could not be serialized"
            }
        
        existing_report = db.query(QAReport).filter(QAReport.id == email_id).first()
        if existing_report:
            # Update existing report
            existing_report.overall_status = report.get("overall_status", "unknown")
            existing_report.risk_score = report.get("risk_score", 0)
            existing_report.report_data = serializable_report
        else:
            # Create new report
            qa_report = QAReport(
                id=email_id,
                email_template_id=email_id,
                overall_status=report.get("overall_status", "unknown"),
                risk_score=report.get("risk_score", 0),
                report_data=serializable_report,
                is_uploaded=False  # Assuming this is from Email on Acid
            )
            db.add(qa_report)
        
        # Commit to database
        db.commit()
        
        return QAResponse(report=report)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"QA process failed: {str(e)}")


# GET /reports/{id} - fetch saved report
@router.get("/reports/{report_id}", response_model=Dict[str, Any])
async def get_report(report_id: str, db: Session = Depends(get_db)):
    """Fetch saved QA report"""
    try:
        # Try to get report from database
        report = db.query(QAReport).filter(QAReport.id == report_id).first()
        if report:
            # Handle the case where report_data might be a string or dict
            report_data = report.report_data
            if isinstance(report_data, str):
                import json
                report_data = json.loads(report_data)
            
            return {
                "report_id": report.id,
                "email_template_id": report.email_template_id,
                "created_at": report.created_at.isoformat() if report.created_at else "",
                "overall_status": report.overall_status,
                "risk_score": report.risk_score,
                "report_data": report_data
            }
        
        # If not found in database, return placeholder
        return {
            "report_id": report_id,
            "status": "not_found",
            "message": "Report not found in database"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch report: {str(e)}")


# POST /upload - upload HTML file for QA analysis
@router.post("/upload")
async def upload_email_html(file: UploadFile = File(...), db: Session = Depends(get_db)):
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
        
        # Save to database
        # Save email template
        email_template = EmailTemplate(
            id=file_id,
            name=file.filename or "Uploaded Email",
            html_content=html_content,
            status="processed"
        )
        email_template.set_metadata(metadata)
        db.add(email_template)
        
        # Save upload record
        upload_record = UploadRecord(
            id=file_id,
            original_filename=file.filename,
            processed=True,
            qa_report_id=file_id
        )
        db.add(upload_record)
        
        # Save QA report
        # Convert report to JSON-serializable format
        try:
            serializable_report = json.loads(json.dumps(report, default=str))
        except Exception as serialize_error:
            # If serialization fails, create a simplified version
            serializable_report = {
                "overall_status": report.get("overall_status", "unknown"),
                "risk_score": report.get("risk_score", 0),
                "email_id": report.get("email_id", file_id),
                "message": "Full report could not be serialized"
            }
        
        qa_report = QAReport(
            id=file_id,
            email_template_id=file_id,
            overall_status=report.get("overall_status", "unknown"),
            risk_score=report.get("risk_score", 0),
            report_data=serializable_report,  # PostgreSQL supports JSON natively
            is_uploaded=True
        )
        db.add(qa_report)
        
        # Commit to database
        db.commit()
        
        # Clean up uploaded file
        os.remove(file_path)
        
        return {"report": report}
    except Exception as e:
        db.rollback()
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