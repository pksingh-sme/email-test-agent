"""
Risk Scoring Agent for the Email QA Agentic Platform
Calculates overall risk score based on all analysis results
"""

from typing import Dict, Any
from collections import Counter
from database.models import RuleConfiguration
from database.config import SessionLocal


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
        
        # Load rule configurations from database
        self.rule_weights = self._load_rule_weights()
    
    def _load_rule_weights(self) -> Dict[str, float]:
        """Load rule weights from database"""
        try:
            db = SessionLocal()
            rules = db.query(RuleConfiguration).all()
            weights = {}
            for rule in rules:
                weights[rule.name] = rule.weight
            db.close()
            return weights
        except Exception as e:
            print(f"Warning: Could not load rule weights from database: {e}")
            # Return default weights
            return {
                "ALT Text Required": 10.0,
                "Link Validation": 20.0,
                "CTA Branding Color Check": 15.0,
                "Template Width Check": 10.0,
                "Font Size Check": 10.0,
                "Copy Tone Check": 10.0,
                "Accessibility Color Contrast": 10.0,
                "Spam Word Check": 10.0,
                "Decorative Image ALT Skip": 5.0
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
        max_possible_score = 100
        issue_counts = Counter()
        
        # Process deterministic test results
        deterministic_results = all_agent_results.get("deterministic", [])
        deterministic_score = 0
        deterministic_max = 0
        
        for test in deterministic_results:
            if test["status"] == "fail":
                # Get weight for this test
                test_name = test.get("test_name", "")
                weight = self.rule_weights.get(test_name, 5.0)  # Default weight
                severity = "high"  # Deterministic failures are generally high severity
                deterministic_score += (weight / 100) * self.severity_weights.get(severity, 5)
                issue_counts[severity] += 1
            deterministic_max += self.rule_weights.get(test.get("test_name", ""), 5.0) / 100 * self.severity_weights["high"]
        
        # Process compliance results
        compliance_results = all_agent_results.get("compliance", {})
        compliance_score = 0
        compliance_max = 0
        
        for issue in compliance_results.get("issues", []):
            rule_name = issue.get("rule", "")
            weight = self.rule_weights.get(rule_name, 10.0)  # Default weight
            severity = issue.get("severity", "medium")
            compliance_score += (weight / 100) * self.severity_weights.get(severity, 3)
            issue_counts[severity] += 1
            compliance_max += self.rule_weights.get(rule_name, 10.0) / 100 * self.severity_weights["critical"]
        
        # Process tone results
        tone_results = all_agent_results.get("tone", {})
        tone_score = 0
        tone_max = 0
        
        for issue in tone_results.get("issues", []):
            rule_name = issue.get("rule", "")
            weight = self.rule_weights.get(rule_name, 10.0)  # Default weight
            severity = issue.get("severity", "medium")
            tone_score += (weight / 100) * self.severity_weights.get(severity, 3)
            issue_counts[severity] += 1
            tone_max += self.rule_weights.get(rule_name, 10.0) / 100 * self.severity_weights["critical"]
        
        # Process accessibility results
        accessibility_results = all_agent_results.get("accessibility", {})
        accessibility_score = 0
        accessibility_max = 0
        
        for issue in accessibility_results.get("issues", []):
            rule_name = issue.get("rule", "")
            weight = self.rule_weights.get(rule_name, 10.0)  # Default weight
            severity = issue.get("severity", "medium")
            accessibility_score += (weight / 100) * self.severity_weights.get(severity, 3)
            issue_counts[severity] += 1
            accessibility_max += self.rule_weights.get(rule_name, 10.0) / 100 * self.severity_weights["critical"]
        
        # Calculate weighted scores (40% deterministic, 25% compliance, 15% tone, 20% accessibility)
        deterministic_weighted = (deterministic_score / max(deterministic_max, 1)) * 40 if deterministic_max > 0 else 0
        compliance_weighted = (compliance_score / max(compliance_max, 1)) * 25 if compliance_max > 0 else 0
        tone_weighted = (tone_score / max(tone_max, 1)) * 15 if tone_max > 0 else 0
        accessibility_weighted = (accessibility_score / max(accessibility_max, 1)) * 20 if accessibility_max > 0 else 0
        
        # Calculate final score
        final_score = deterministic_weighted + compliance_weighted + tone_weighted + accessibility_weighted
        normalized_score = min(100, max(0, final_score))
        
        # Determine risk level
        risk_level = self._determine_risk_level(normalized_score)
        
        return {
            "agent": "risk_scoring",
            "score": round(normalized_score, 2),
            "risk_level": risk_level,
            "issue_counts": dict(issue_counts),
            "breakdown": {
                "deterministic": {
                    "score": round(deterministic_weighted, 2),
                    "max": 40,
                    "raw_score": round(deterministic_score, 2),
                    "raw_max": round(deterministic_max, 2)
                },
                "compliance": {
                    "score": round(compliance_weighted, 2),
                    "max": 25,
                    "raw_score": round(compliance_score, 2),
                    "raw_max": round(compliance_max, 2)
                },
                "tone": {
                    "score": round(tone_weighted, 2),
                    "max": 15,
                    "raw_score": round(tone_score, 2),
                    "raw_max": round(tone_max, 2)
                },
                "accessibility": {
                    "score": round(accessibility_weighted, 2),
                    "max": 20,
                    "raw_score": round(accessibility_score, 2),
                    "raw_max": round(accessibility_max, 2)
                }
            },
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