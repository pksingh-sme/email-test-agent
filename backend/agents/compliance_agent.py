"""
Compliance Agent for the Email QA Agentic Platform
Checks brand compliance including fonts, colors, spacing, logos, and headers/footers
"""

from typing import Dict, Any
import yaml
import os


class ComplianceAgent:
    def __init__(self):
        # Load brand rules
        self.brand_rules = self._load_brand_rules()
    
    def _load_brand_rules(self) -> Dict[str, Any]:
        """Load brand rules from config file"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'brand_rules.yaml')
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            # Return default rules if config file not found
            return {
                "font_family": "Arial",
                "cta_color": "#0085FF",
                "header_logo": "brandlogo.png",
                "spacing": {
                    "top_padding": "24px",
                    "bottom_padding": "24px"
                }
            }
    
    def analyze(self, email_id: str, html_content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze email for brand compliance
        
        Args:
            email_id: Unique identifier for the email
            html_content: HTML content of the email
            metadata: Metadata associated with the email
            
        Returns:
            Dict containing compliance analysis results
        """
        issues = []
        
        # Check font family compliance
        font_issues = self._check_font_compliance(html_content)
        issues.extend(font_issues)
        
        # Check CTA button color compliance
        cta_issues = self._check_cta_color_compliance(html_content)
        issues.extend(cta_issues)
        
        # Check spacing rules compliance
        spacing_issues = self._check_spacing_compliance(html_content)
        issues.extend(spacing_issues)
        
        # Check logo placement
        logo_issues = self._check_logo_placement(html_content)
        issues.extend(logo_issues)
        
        # Check header/footer consistency
        header_footer_issues = self._check_header_footer_consistency(html_content)
        issues.extend(header_footer_issues)
        
        return {
            "agent": "compliance",
            "email_id": email_id,
            "issues": issues,
            "summary": f"Found {len(issues)} compliance issues"
        }
    
    def _check_font_compliance(self, html_content: str) -> list:
        """Check if fonts comply with brand guidelines"""
        issues = []
        brand_font = self.brand_rules.get("font_family", "Arial")
        
        # Simple check for font-family in styles
        if f'font-family: {brand_font}' not in html_content:
            issues.append({
                "rule": "font_compliance",
                "description": f"Font does not match brand guidelines. Expected: {brand_font}",
                "severity": "medium"
            })
        
        return issues
    
    def _check_cta_color_compliance(self, html_content: str) -> list:
        """Check if CTA button colors comply with brand guidelines"""
        issues = []
        brand_cta_color = self.brand_rules.get("cta_color", "#0085FF")
        
        # Simple check for CTA color in styles
        if brand_cta_color not in html_content:
            issues.append({
                "rule": "cta_color_compliance",
                "description": f"CTA button color does not match brand guidelines. Expected: {brand_cta_color}",
                "severity": "medium"
            })
        
        return issues
    
    def _check_spacing_compliance(self, html_content: str) -> list:
        """Check if spacing complies with brand guidelines"""
        issues = []
        spacing_rules = self.brand_rules.get("spacing", {})
        
        # Check top padding
        top_padding = spacing_rules.get("top_padding", "24px")
        if top_padding not in html_content:
            issues.append({
                "rule": "spacing_compliance",
                "description": f"Top padding does not match brand guidelines. Expected: {top_padding}",
                "severity": "low"
            })
        
        # Check bottom padding
        bottom_padding = spacing_rules.get("bottom_padding", "24px")
        if bottom_padding not in html_content:
            issues.append({
                "rule": "spacing_compliance",
                "description": f"Bottom padding does not match brand guidelines. Expected: {bottom_padding}",
                "severity": "low"
            })
        
        return issues
    
    def _check_logo_placement(self, html_content: str) -> list:
        """Check if logo placement complies with brand guidelines"""
        issues = []
        brand_logo = self.brand_rules.get("header_logo", "brandlogo.png")
        
        # Check if brand logo is present
        if brand_logo not in html_content:
            issues.append({
                "rule": "logo_placement",
                "description": f"Brand logo not found. Expected: {brand_logo}",
                "severity": "medium"
            })
        
        return issues
    
    def _check_header_footer_consistency(self, html_content: str) -> list:
        """Check header/footer consistency"""
        issues = []
        
        # Simple checks for header/footer presence
        if "<header" not in html_content.lower() and "<div class='header'" not in html_content.lower():
            issues.append({
                "rule": "header_consistency",
                "description": "Header section not found or inconsistent",
                "severity": "low"
            })
        
        if "<footer" not in html_content.lower() and "<div class='footer'" not in html_content.lower():
            issues.append({
                "rule": "footer_consistency",
                "description": "Footer section not found or inconsistent",
                "severity": "low"
            })
        
        return issues