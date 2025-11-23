"""
API Endpoints for the Email QA Agentic Platform
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
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