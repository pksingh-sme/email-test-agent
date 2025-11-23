"""
Agent Orchestrator for the Email QA Agentic Platform
Manages the multi-agent workflow and consolidates results
"""

from typing import Dict, List, Any
from agents.supervisor_agent import SupervisorAgent
from deterministic_tests import run_all_deterministic_tests


class AgentOrchestrator:
    def __init__(self):
        self.supervisor_agent = SupervisorAgent()
    
    def run_qa_process(self, email_id: str, html_content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the complete QA process for an email
        
        Args:
            email_id: Unique identifier for the email
            html_content: HTML content of the email
            metadata: Metadata associated with the email
            
        Returns:
            Dict containing the consolidated QA report
        """
        # Run deterministic tests
        deterministic_results = run_all_deterministic_tests(html_content, metadata)
        
        # Run agentic workflow through supervisor
        agentic_results = self.supervisor_agent.process_email(
            email_id, html_content, metadata, deterministic_results
        )
        
        # Consolidate results
        consolidated_report = {
            "email_id": email_id,
            "deterministic_tests": deterministic_results,
            "agentic_analysis": agentic_results,
            "overall_status": self._calculate_overall_status(deterministic_results, agentic_results),
            "risk_score": agentic_results.get("risk_score", 0),
            "generated_at": self._get_current_timestamp()
        }
        
        return consolidated_report
    
    def _calculate_overall_status(self, deterministic_results: List[Dict], agentic_results: Dict) -> str:
        """Calculate overall status based on deterministic and agentic results"""
        # Count failures in deterministic tests
        deterministic_failures = sum(1 for test in deterministic_results if test["status"] == "fail")
        
        # Check agentic risk level
        risk_level = agentic_results.get("risk_level", "low")
        
        # Determine overall status
        if deterministic_failures > 3 or risk_level == "high":
            return "fail"
        elif deterministic_failures > 0 or risk_level == "medium":
            return "needs_review"
        else:
            return "pass"
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


# Example usage
if __name__ == "__main__":
    orchestrator = AgentOrchestrator()
    
    # Example data
    sample_html = "<html><body><h1>Hello World</h1></body></html>"
    sample_metadata = {
        "subject": "Test Subject",
        "preheader": "Test Preheader",
        "template_name": "Test Template",
        "locale": "en-US"
    }
    
    # Run QA process
    result = orchestrator.run_qa_process("test-email-123", sample_html, sample_metadata)
    print(result)