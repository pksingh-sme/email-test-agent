"""
Database models for the Email QA Agentic Platform
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, Float
from sqlalchemy.sql import func
from database.config import Base
from typing import Dict, Any
import json


class EmailTemplate(Base):
    __tablename__ = "email_templates"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="active")
    html_content = Column(Text)
    metadata_json = Column(Text)  # Store as JSON string
    
    def set_metadata(self, metadata: Dict[str, Any]):
        """Set metadata as JSON string"""
        self.metadata_json = json.dumps(metadata)
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata as dictionary"""
        if self.metadata_json:
            return json.loads(self.metadata_json)
        return {}


class QAReport(Base):
    __tablename__ = "qa_reports"
    
    id = Column(String, primary_key=True, index=True)
    email_template_id = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    overall_status = Column(String)
    risk_score = Column(Integer)
    report_data = Column(JSON)  # PostgreSQL supports JSON natively
    is_uploaded = Column(Boolean, default=False)  # To distinguish between Email on Acid and uploaded files


class UploadRecord(Base):
    __tablename__ = "upload_records"
    
    id = Column(String, primary_key=True, index=True)
    original_filename = Column(String)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed = Column(Boolean, default=False)
    qa_report_id = Column(String, nullable=True)


class RuleConfiguration(Base):
    __tablename__ = "rule_configurations"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    weight = Column(Float, default=0.0)
    priority = Column(String)  # High, Medium, Low
    override_enabled = Column(Boolean, default=False)
    business_override_text = Column(Text)
    error_message = Column(Text)
    category = Column(String)  # deterministic, compliance, tone, accessibility
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())