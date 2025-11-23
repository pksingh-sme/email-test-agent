"""
Database initialization script for the Email QA Agentic Platform
"""

from database.config import engine, Base
from database.models import EmailTemplate, QAReport, UploadRecord

def init_db():
    """Initialize database tables"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

def drop_db():
    """Drop all tables (use with caution!)"""
    Base.metadata.drop_all(bind=engine)
    print("Database tables dropped successfully!")

if __name__ == "__main__":
    init_db()