"""
Risk Scoring Agent for the Email QA Agentic Platform
Calculates overall risk score based on all analysis results
"""

from typing import Dict, Any
from collections import Counter


class RiskScoringAgent:
    def __init__(self):
        # Define severity weights
        self.severity_weights = {
            "critical": 10,
            "high": 5,
            "medium": 3,
            "low": 1
        }
        
        # Define risk thresholds
        self.risk_thresholds = {
            "high": 80,
            "medium": 50,
            "low": 0
        }
    
    def calculate_risk(self, all_agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate risk score based on all agent results
        
        Args:
            all_agent_results: Combined results from all agents
            
        Returns:
            Dict containing risk score and level
        """
        # Calculate base score from all issues
        total_score = 0
        issue_counts = Counter()
        
        # Process deterministic test results
        deterministic_results = all_agent_results.get("deterministic", [])
        for test in deterministic_results:
            if test["status"] == "fail":
                severity = "high"  # Deterministic failures are generally high severity
                total_score += self.severity_weights.get(severity, 5)
                issue_counts[severity] += 1
        
        # Process compliance results
        compliance_results = all_agent_results.get("compliance", {})
        for issue in compliance_results.get("issues", []):
            severity = issue.get("severity", "medium")
            total_score += self.severity_weights.get(severity, 3)
            issue_counts[severity] += 1
        
        # Process tone results
        tone_results = all_agent_results.get("tone", {})
        for issue in tone_results.get("issues", []):
            severity = issue.get("severity", "medium")
            total_score += self.severity_weights.get(severity, 3)
            issue_counts[severity] += 1
        
        # Process accessibility results
        accessibility_results = all_agent_results.get("accessibility", {})
        for issue in accessibility_results.get("issues", []):
            severity = issue.get("severity", "medium")
            total_score += self.severity_weights.get(severity, 3)
            issue_counts[severity] += 1
        
        # Normalize score to 0-100 scale
        max_possible_score = sum([
            len(deterministic_results) * self.severity_weights["high"],
            len(compliance_results.get("issues", [])) * self.severity_weights["critical"],
            len(tone_results.get("issues", [])) * self.severity_weights["critical"],
            len(accessibility_results.get("issues", [])) * self.severity_weights["critical"]
        ])
        
        normalized_score = 0
        if max_possible_score > 0:
            normalized_score = min(100, (total_score / max_possible_score) * 100)
        
        # Determine risk level
        risk_level = self._determine_risk_level(normalized_score)
        
        return {
            "agent": "risk_scoring",
            "score": round(normalized_score, 2),
            "risk_level": risk_level,
            "issue_counts": dict(issue_counts),
            "reason": self._generate_risk_reason(risk_level, issue_counts)
        }
    
    def _determine_risk_level(self, score: float) -> str:
        """Determine risk level based on score"""
        if score >= self.risk_thresholds["high"]:
            return "high"
        elif score >= self.risk_thresholds["medium"]:
            return "medium"
        else:
            return "low"
    
    def _generate_risk_reason(self, risk_level: str, issue_counts: Counter) -> str:
        """Generate reason for the risk level"""
        if risk_level == "high":
            return f"High risk due to {issue_counts['critical']} critical and {issue_counts['high']} high severity issues"
        elif risk_level == "medium":
            return f"Medium risk due to {issue_counts['medium']} medium severity issues"
        else:
            return f"Low risk with {issue_counts['low']} minor issues"