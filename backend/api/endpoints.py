"""
API Endpoints for the Email QA Agentic Platform
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Body
from fastapi.responses import HTMLResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import os
import uuid
import json
from connectors.email_on_acid import EmailOnAcidConnector
from agent_orchestrator import AgentOrchestrator
from database.config import get_db
from database.models import EmailTemplate, QAReport, UploadRecord, RuleConfiguration
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


class RuleConfigRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    weight: float = 0.0
    priority: str = "Medium"
    override_enabled: bool = False
    business_override_text: Optional[str] = ""
    error_message: Optional[str] = ""
    category: str = "deterministic"


class RuleConfigResponse(BaseModel):
    id: str
    name: str
    description: str
    weight: float
    priority: str
    override_enabled: bool
    business_override_text: str
    error_message: str
    category: str
    created_at: str
    updated_at: str


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
            # Get QA report for risk score
            qa_report = db.query(QAReport).filter(QAReport.email_template_id == email.id).first()
            
            emails.append({
                "id": email.id,
                "name": email.name,
                "created_at": email.created_at.isoformat() if email.created_at else "",
                "status": email.status,
                "locale": metadata.get("locale", "N/A"),
                "risk_score": qa_report.risk_score if qa_report else 0
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
            original_filename=file.filename or "Uploaded Email",
            processed=True,
            qa_report_id=file_id
        )
        db.add(upload_record)
        
        # Save QA report
        try:
            serializable_report = json.loads(json.dumps(report, default=str))
        except Exception as serialize_error:
            serializable_report = {
                "overall_status": report.get("overall_status", "unknown"),
                "risk_score": report.get("risk_score", 0),
                "email_id": file_id,
                "message": "Full report could not be serialized"
            }
        
        qa_report = QAReport(
            id=file_id,
            email_template_id=file_id,
            overall_status=report.get("overall_status", "unknown"),
            risk_score=report.get("risk_score", 0),
            report_data=serializable_report,
            is_uploaded=True
        )
        db.add(qa_report)
        
        # Commit to database
        db.commit()
        
        return {
            "message": "File uploaded and analyzed successfully",
            "report": report,
            "email_id": file_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


# GET /rules - get all rule configurations
@router.get("/rules", response_model=List[RuleConfigResponse])
async def get_rules(db: Session = Depends(get_db)):
    """Get all rule configurations"""
    try:
        rules = db.query(RuleConfiguration).all()
        
        # If no rules exist, create default rules
        if not rules:
            default_rules = [
                {
                    "id": str(uuid.uuid4()),
                    "name": "ALT Text Required",
                    "description": "Ensure meaningful ALT text is applied",
                    "weight": 10.0,
                    "priority": "Medium",
                    "override_enabled": True,
                    "business_override_text": "Allow decorative images with empty ALT",
                    "error_message": "ALT text missing. Suggested: <AI-generated suggestion>",
                    "category": "accessibility"
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Decorative Image ALT Skip",
                    "description": "Skip ALT text requirement for decorative images",
                    "weight": 5.0,
                    "priority": "Low",
                    "override_enabled": False,
                    "business_override_text": "",
                    "error_message": "Decorative image requires ALT text",
                    "category": "accessibility"
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "CTA Branding Color Check",
                    "description": "Ensure CTA buttons use brand colors",
                    "weight": 15.0,
                    "priority": "High",
                    "override_enabled": True,
                    "business_override_text": "Allow non-brand colors for special campaigns",
                    "error_message": "CTA color does not match brand guidelines",
                    "category": "compliance"
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Link Validation",
                    "description": "Check for broken or malformed links",
                    "weight": 20.0,
                    "priority": "High",
                    "override_enabled": True,
                    "business_override_text": "Allow placeholder links for development",
                    "error_message": "Invalid or broken link detected",
                    "category": "deterministic"
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Template Width Check",
                    "description": "Ensure template width is within acceptable range",
                    "weight": 10.0,
                    "priority": "Low",
                    "override_enabled": True,
                    "business_override_text": "Allow custom widths for special templates",
                    "error_message": "Template width outside acceptable range",
                    "category": "deterministic"
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Font Size Check",
                    "description": "Ensure font sizes comply with brand guidelines",
                    "weight": 10.0,
                    "priority": "Medium",
                    "override_enabled": False,
                    "business_override_text": "",
                    "error_message": "Font size does not match brand guidelines",
                    "category": "compliance"
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Copy Tone Check",
                    "description": "Ensure copy tone matches brand guidelines",
                    "weight": 10.0,
                    "priority": "Medium",
                    "override_enabled": True,
                    "business_override_text": "Allow casual tone for specific campaigns",
                    "error_message": "Copy tone does not match brand guidelines",
                    "category": "tone"
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Accessibility Color Contrast",
                    "description": "Ensure sufficient color contrast for accessibility",
                    "weight": 10.0,
                    "priority": "Medium",
                    "override_enabled": False,
                    "business_override_text": "",
                    "error_message": "Insufficient color contrast detected",
                    "category": "accessibility"
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Spam Word Check",
                    "description": "Detect spammy words that may affect deliverability",
                    "weight": 10.0,
                    "priority": "Low",
                    "override_enabled": True,
                    "business_override_text": "Allow promotional language for marketing emails",
                    "error_message": "Spammy words detected in content",
                    "category": "tone"
                }
            ]
            
            for rule_data in default_rules:
                rule = RuleConfiguration(**rule_data)
                db.add(rule)
            
            db.commit()
            rules = db.query(RuleConfiguration).all()
        
        return [
            RuleConfigResponse(
                id=rule.id,
                name=rule.name,
                description=rule.description,
                weight=rule.weight,
                priority=rule.priority,
                override_enabled=rule.override_enabled,
                business_override_text=rule.business_override_text or "",
                error_message=rule.error_message or "",
                category=rule.category,
                created_at=rule.created_at.isoformat() if rule.created_at else "",
                updated_at=rule.updated_at.isoformat() if rule.updated_at else ""
            )
            for rule in rules
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch rules: {str(e)}")


# PUT /rules/{rule_id} - update rule configuration
@router.put("/rules/{rule_id}", response_model=RuleConfigResponse)
async def update_rule(rule_id: str, rule_data: RuleConfigRequest, db: Session = Depends(get_db)):
    """Update rule configuration"""
    try:
        rule = db.query(RuleConfiguration).filter(RuleConfiguration.id == rule_id).first()
        if not rule:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        # Update rule fields
        rule.name = rule_data.name
        rule.description = rule_data.description
        rule.weight = rule_data.weight
        rule.priority = rule_data.priority
        rule.override_enabled = rule_data.override_enabled
        rule.business_override_text = rule_data.business_override_text
        rule.error_message = rule_data.error_message
        rule.category = rule_data.category
        
        db.commit()
        db.refresh(rule)
        
        return RuleConfigResponse(
            id=rule.id,
            name=rule.name,
            description=rule.description,
            weight=rule.weight,
            priority=rule.priority,
            override_enabled=rule.override_enabled,
            business_override_text=rule.business_override_text or "",
            error_message=rule.error_message or "",
            category=rule.category,
            created_at=rule.created_at.isoformat() if rule.created_at else "",
            updated_at=rule.updated_at.isoformat() if rule.updated_at else ""
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update rule: {str(e)}")


# POST /rules - create new rule configuration
@router.post("/rules", response_model=RuleConfigResponse)
async def create_rule(rule_data: RuleConfigRequest, db: Session = Depends(get_db)):
    """Create new rule configuration"""
    try:
        rule = RuleConfiguration(
            id=str(uuid.uuid4()),
            name=rule_data.name,
            description=rule_data.description,
            weight=rule_data.weight,
            priority=rule_data.priority,
            override_enabled=rule_data.override_enabled,
            business_override_text=rule_data.business_override_text,
            error_message=rule_data.error_message,
            category=rule_data.category
        )
        
        db.add(rule)
        db.commit()
        db.refresh(rule)
        
        return RuleConfigResponse(
            id=rule.id,
            name=rule.name,
            description=rule.description,
            weight=rule.weight,
            priority=rule.priority,
            override_enabled=rule.override_enabled,
            business_override_text=rule.business_override_text or "",
            error_message=rule.error_message or "",
            category=rule.category,
            created_at=rule.created_at.isoformat() if rule.created_at else "",
            updated_at=rule.updated_at.isoformat() if rule.updated_at else ""
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create rule: {str(e)}")


# PUT /scoring-model - update scoring model formula
@router.put("/scoring-model")
async def update_scoring_model(formula: str = Body(..., embed=True), db: Session = Depends(get_db)):
    """Update scoring model formula"""
    try:
        # In a real implementation, this would save the formula to a configuration table
        # For now, we'll just return success
        return {"message": "Scoring model updated successfully", "formula": formula}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update scoring model: {str(e)}")