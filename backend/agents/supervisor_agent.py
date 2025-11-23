"""
Supervisor Agent for the Email QA Agentic Platform
Controls orchestration and merges results from sub-agents
"""

from typing import Dict, List, Any
from agents.compliance_agent import ComplianceAgent
from agents.tone_agent import ToneAgent
from agents.accessibility_agent import AccessibilityAgent
from agents.risk_scoring_agent import RiskScoringAgent
from agents.fix_suggestion_agent import FixSuggestionAgent


class SupervisorAgent:
    def __init__(self):
        # Initialize all sub-agents
        self.compliance_agent = ComplianceAgent()
        self.tone_agent = ToneAgent()
        self.accessibility_agent = AccessibilityAgent()
        self.risk_scoring_agent = RiskScoringAgent()
        self.fix_suggestion_agent = FixSuggestionAgent()
    
    def process_email(self, email_id: str, html_content: str, metadata: Dict[str, Any], 
                     deterministic_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process an email through all sub-agents and consolidate results
        
        Args:
            email_id: Unique identifier for the email
            html_content: HTML content of the email
            metadata: Metadata associated with the email
            deterministic_results: Results from deterministic tests
            
        Returns:
            Dict containing the consolidated analysis from all agents
        """
        # Run each agent's analysis
        compliance_results = self.compliance_agent.analyze(email_id, html_content, metadata)
        tone_results = self.tone_agent.analyze(email_id, html_content, metadata)
        accessibility_results = self.accessibility_agent.analyze(email_id, html_content, metadata)
        
        # Combine all agent results for risk scoring
        all_agent_results = {
            "compliance": compliance_results,
            "tone": tone_results,
            "accessibility": accessibility_results,
            "deterministic": deterministic_results
        }
        
        # Calculate risk score
        risk_results = self.risk_scoring_agent.calculate_risk(all_agent_results)
        
        # Generate fix suggestions
        fix_suggestions = self.fix_suggestion_agent.generate_fixes(
            all_agent_results, risk_results
        )
        
        # Consolidate all results
        consolidated_results = {
            "overall_status": self._determine_overall_status(
                deterministic_results, compliance_results, tone_results, 
                accessibility_results, risk_results
            ),
            "risk_score": risk_results.get("score", 0),
            "risk_level": risk_results.get("risk_level", "low"),
            "compliance_analysis": compliance_results,
            "tone_analysis": tone_results,
            "accessibility_analysis": accessibility_results,
            "deterministic_results": deterministic_results,
            "fix_suggestions": fix_suggestions,
            "top_issues": self._extract_top_issues(
                deterministic_results, compliance_results, tone_results,
                accessibility_results
            ),
            "score_breakdown": risk_results.get("breakdown", {})
        }
        
        return consolidated_results
    
    def _determine_overall_status(self, deterministic_results: List[Dict], 
                                 compliance_results: Dict, tone_results: Dict,
                                 accessibility_results: Dict, risk_results: Dict) -> str:
        """Determine overall status based on all analysis results"""
        # Count deterministic failures
        deterministic_failures = sum(1 for test in deterministic_results if test["status"] == "fail")
        
        # Check for critical compliance issues
        compliance_issues = compliance_results.get("issues", [])
        critical_compliance = any(issue.get("severity") == "critical" for issue in compliance_issues)
        
        # Check risk level
        risk_level = risk_results.get("risk_level", "low")
        
        # Determine overall status
        if deterministic_failures > 3 or critical_compliance or risk_level == "high":
            return "fail"
        elif deterministic_failures > 0 or risk_level == "medium":
            return "needs_review"
        else:
            return "pass"
    
    def _extract_top_issues(self, deterministic_results: List[Dict], 
                           compliance_results: Dict, tone_results: Dict,
                           accessibility_results: Dict) -> List[Dict[str, Any]]:
        """Extract top issues from all analyses"""
        top_issues = []
        
        # Add deterministic failures
        for test in deterministic_results:
            if test["status"] == "fail":
                top_issues.append({
                    "type": "deterministic",
                    "test_name": test["test_name"],
                    "details": test["details"],
                    "severity": "high"
                })
        
        # Add compliance issues
        for issue in compliance_results.get("issues", []):
            top_issues.append({
                "type": "compliance",
                "test_name": issue.get("rule", ""),
                "details": issue.get("description", ""),
                "severity": issue.get("severity", "medium")
            })
        
        # Add tone issues
        for issue in tone_results.get("issues", []):
            top_issues.append({
                "type": "tone",
                "test_name": issue.get("rule", ""),
                "details": issue.get("description", ""),
                "severity": issue.get("severity", "medium")
            })
        
        # Add accessibility issues
        for issue in accessibility_results.get("issues", []):
            top_issues.append({
                "type": "accessibility",
                "test_name": issue.get("rule", ""),
                "details": issue.get("description", ""),
                "severity": issue.get("severity", "medium")
            })
        
        # Sort by severity (critical > high > medium > low)
        severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        top_issues.sort(key=lambda x: severity_order.get(x["severity"], 0), reverse=True)
        
        return top_issues[:10]  # Return top 10 issues