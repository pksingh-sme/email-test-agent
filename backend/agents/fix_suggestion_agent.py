"""
Fix Suggestion Agent for the Email QA Agentic Platform
Generates actionable fixes for identified issues
"""

from typing import Dict, Any, List


class FixSuggestionAgent:
    def __init__(self):
        # Define fix templates
        self.fix_templates = {
            "alt_text": "Add descriptive ALT text to image: {element}",
            "links": "Fix malformed link: {url}",
            "subject_line": "Add a compelling subject line",
            "preheader": "Add a preheader text",
            "template_meta": "Add missing template metadata: {missing_field}",
            "width": "Specify width attributes for email elements",
            "background_color": "Define background colors for all sections",
            "image_dimensions": "Add width and height attributes to image: {element}",
            "long_copy": "Break up long text block into shorter paragraphs",
            "font_compliance": "Update font family to brand standard: {expected_font}",
            "cta_color_compliance": "Update CTA button color to brand standard: {expected_color}",
            "spacing_compliance": "Adjust spacing to brand guidelines: {spacing_rule}",
            "logo_placement": "Add brand logo to header: {expected_logo}",
            "header_consistency": "Ensure consistent header structure",
            "footer_consistency": "Ensure consistent footer structure",
            "spam_indicators": "Remove or rephrase spammy language: {spam_text}",
            "complex_sentences": "Simplify complex sentence structure",
            "clarity": "Rewrite passive voice to active voice",
            "grammar": "Fix grammar issue: {grammar_issue}",
            "alt_text_quality": "Improve ALT text descriptiveness: {current_text}",
            "semantic_html": "Add proper heading structure",
            "link_text_clarity": "Make link text more descriptive: {current_text}",
            "color_contrast": "Ensure sufficient color contrast for readability"
        }
    
    def generate_fixes(self, all_agent_results: Dict[str, Any], risk_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate fix suggestions based on all analysis results
        
        Args:
            all_agent_results: Combined results from all agents
            risk_results: Risk scoring results
            
        Returns:
            List of fix suggestions
        """
        fixes = []
        
        # Generate fixes from deterministic test results
        deterministic_results = all_agent_results.get("deterministic", [])
        for test in deterministic_results:
            if test["status"] == "fail":
                fix = self._generate_deterministic_fix(test)
                if fix:
                    fixes.append(fix)
        
        # Generate fixes from compliance results
        compliance_results = all_agent_results.get("compliance", {})
        for issue in compliance_results.get("issues", []):
            fix = self._generate_compliance_fix(issue)
            if fix:
                fixes.append(fix)
        
        # Generate fixes from tone results
        tone_results = all_agent_results.get("tone", {})
        for issue in tone_results.get("issues", []):
            fix = self._generate_tone_fix(issue)
            if fix:
                fixes.append(fix)
        
        # Generate fixes from accessibility results
        accessibility_results = all_agent_results.get("accessibility", {})
        for issue in accessibility_results.get("issues", []):
            fix = self._generate_accessibility_fix(issue)
            if fix:
                fixes.append(fix)
        
        # Prioritize fixes based on severity
        fixes = self._prioritize_fixes(fixes)
        
        return fixes
    
    def _generate_deterministic_fix(self, test_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fix for deterministic test failure"""
        test_name = test_result["test_name"]
        template = self.fix_templates.get(test_name, "Fix {test_name} issue")
        
        # Create a safe copy of test_result with default values for missing keys
        safe_test_result = test_result.copy()
        safe_test_result.setdefault("element", "element")
        safe_test_result.setdefault("url", "link")
        safe_test_result.setdefault("missing_field", "field")
        safe_test_result.setdefault("expected_font", "Arial")
        safe_test_result.setdefault("expected_color", "#0085FF")
        safe_test_result.setdefault("spacing_rule", "padding")
        safe_test_result.setdefault("expected_logo", "logo")
        safe_test_result.setdefault("spam_text", "text")
        safe_test_result.setdefault("grammar_issue", "issue")
        safe_test_result.setdefault("current_text", "text")
        
        return {
            "type": "deterministic",
            "issue": test_name,
            "description": test_result["details"],
            "suggestion": template.format(**safe_test_result),
            "priority": "high"
        }
    
    def _generate_compliance_fix(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fix for compliance issue"""
        rule = issue.get("rule", "compliance")
        template = self.fix_templates.get(rule, "Fix compliance issue: {description}")
        
        # Create a safe copy of issue with default values for missing keys
        safe_issue = issue.copy()
        safe_issue.setdefault("element", "element")
        safe_issue.setdefault("url", "link")
        safe_issue.setdefault("missing_field", "field")
        safe_issue.setdefault("expected_font", "Arial")
        safe_issue.setdefault("expected_color", "#0085FF")
        safe_issue.setdefault("spacing_rule", "padding")
        safe_issue.setdefault("expected_logo", "logo")
        safe_issue.setdefault("spam_text", "text")
        safe_issue.setdefault("grammar_issue", "issue")
        safe_issue.setdefault("current_text", "text")
        safe_issue.setdefault("description", "issue")
        
        return {
            "type": "compliance",
            "issue": rule,
            "description": issue.get("description", ""),
            "suggestion": template.format(**safe_issue),
            "priority": issue.get("severity", "medium")
        }
    
    def _generate_tone_fix(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fix for tone issue"""
        rule = issue.get("rule", "tone")
        template = self.fix_templates.get(rule, "Improve tone/clarity: {description}")
        
        # Create a safe copy of issue with default values for missing keys
        safe_issue = issue.copy()
        safe_issue.setdefault("element", "element")
        safe_issue.setdefault("url", "link")
        safe_issue.setdefault("missing_field", "field")
        safe_issue.setdefault("expected_font", "Arial")
        safe_issue.setdefault("expected_color", "#0085FF")
        safe_issue.setdefault("spacing_rule", "padding")
        safe_issue.setdefault("expected_logo", "logo")
        safe_issue.setdefault("spam_text", "text")
        safe_issue.setdefault("grammar_issue", "issue")
        safe_issue.setdefault("current_text", "text")
        safe_issue.setdefault("description", "issue")
        
        return {
            "type": "tone",
            "issue": rule,
            "description": issue.get("description", ""),
            "suggestion": template.format(**safe_issue),
            "priority": issue.get("severity", "medium")
        }
    
    def _generate_accessibility_fix(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fix for accessibility issue"""
        rule = issue.get("rule", "accessibility")
        template = self.fix_templates.get(rule, "Improve accessibility: {description}")
        
        # Create a safe copy of issue with default values for missing keys
        safe_issue = issue.copy()
        safe_issue.setdefault("element", "element")
        safe_issue.setdefault("url", "link")
        safe_issue.setdefault("missing_field", "field")
        safe_issue.setdefault("expected_font", "Arial")
        safe_issue.setdefault("expected_color", "#0085FF")
        safe_issue.setdefault("spacing_rule", "padding")
        safe_issue.setdefault("expected_logo", "logo")
        safe_issue.setdefault("spam_text", "text")
        safe_issue.setdefault("grammar_issue", "issue")
        safe_issue.setdefault("current_text", "text")
        safe_issue.setdefault("description", "issue")
        
        return {
            "type": "accessibility",
            "issue": rule,
            "description": issue.get("description", ""),
            "suggestion": template.format(**safe_issue),
            "priority": issue.get("severity", "medium")
        }
    
    def _prioritize_fixes(self, fixes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize fixes based on severity"""
        priority_order = {"critical": 1, "high": 2, "medium": 3, "low": 4}
        
        # Sort fixes by priority
        fixes.sort(key=lambda x: priority_order.get(x.get("priority", "medium"), 3))
        
        return fixes