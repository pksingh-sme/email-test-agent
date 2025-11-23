"""
Accessibility Agent for the Email QA Agentic Platform
Checks WCAG compliance, ALT text quality, semantic HTML, and color contrast
"""

from typing import Dict, Any
from bs4 import BeautifulSoup
import re


class AccessibilityAgent:
    def __init__(self):
        # Define accessibility standards
        self.min_contrast_ratio = 4.5  # WCAG AA standard
        self.max_link_text_length = 80  # Recommended max length
    
    def analyze(self, email_id: str, html_content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze email for accessibility issues
        
        Args:
            email_id: Unique identifier for the email
            html_content: HTML content of the email
            metadata: Metadata associated with the email
            
        Returns:
            Dict containing accessibility analysis results
        """
        issues = []
        
        # Parse HTML content
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Check ALT text quality
        alt_text_issues = self._check_alt_text_quality(soup)
        issues.extend(alt_text_issues)
        
        # Check semantic HTML structure
        semantic_issues = self._check_semantic_html(soup)
        issues.extend(semantic_issues)
        
        # Check link text clarity
        link_text_issues = self._check_link_text_clarity(soup)
        issues.extend(link_text_issues)
        
        # Check color contrast (simplified)
        contrast_issues = self._check_color_contrast(html_content)
        issues.extend(contrast_issues)
        
        return {
            "agent": "accessibility",
            "email_id": email_id,
            "issues": issues,
            "summary": f"Found {len(issues)} accessibility issues"
        }
    
    def _check_alt_text_quality(self, soup: BeautifulSoup) -> list:
        """Check quality of ALT text"""
        issues = []
        images = soup.find_all('img')
        
        for img in images:
            alt_text = img.get('alt', '').strip()
            
            # Check if ALT text is missing
            if not alt_text:
                issues.append({
                    "rule": "alt_text_quality",
                    "description": f"Image missing descriptive ALT text: {str(img)[:50]}...",
                    "severity": "high"
                })
            # Check if ALT text is placeholder text
            elif alt_text.lower() in ['image', 'photo', 'picture', 'graphic']:
                issues.append({
                    "rule": "alt_text_quality",
                    "description": f"Image has non-descriptive ALT text: '{alt_text}'",
                    "severity": "medium"
                })
            # Check if ALT text is too long
            elif len(alt_text) > 125:  # Recommended max length
                issues.append({
                    "rule": "alt_text_quality",
                    "description": f"ALT text is too long ({len(alt_text)} chars): '{alt_text[:50]}...'",
                    "severity": "low"
                })
        
        return issues
    
    def _check_semantic_html(self, soup: BeautifulSoup) -> list:
        """Check for proper semantic HTML structure"""
        issues = []
        
        # Check for heading structure
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        if not headings:
            issues.append({
                "rule": "semantic_html",
                "description": "No heading elements found",
                "severity": "medium"
            })
        else:
            # Check if h1 is present
            h1_tags = soup.find_all('h1')
            if not h1_tags:
                issues.append({
                    "rule": "semantic_html",
                    "description": "Missing main heading (h1)",
                    "severity": "medium"
                })
            elif len(h1_tags) > 1:
                issues.append({
                    "rule": "semantic_html",
                    "description": "Multiple h1 headings found",
                    "severity": "low"
                })
        
        # Check for proper list structure
        lists = soup.find_all(['ul', 'ol'])
        list_items = soup.find_all('li')
        
        if list_items and not lists:
            issues.append({
                "rule": "semantic_html",
                "description": "List items found without proper list container",
                "severity": "low"
            })
        
        return issues
    
    def _check_link_text_clarity(self, soup: BeautifulSoup) -> list:
        """Check link text for clarity and descriptiveness"""
        issues = []
        links = soup.find_all('a', href=True)
        
        for link in links:
            link_text = link.get_text(strip=True)
            
            # Check if link text is missing
            if not link_text:
                issues.append({
                    "rule": "link_text_clarity",
                    "description": f"Link with no text content: {str(link)[:50]}...",
                    "severity": "high"
                })
            # Check if link text is too generic
            elif link_text.lower() in ['click here', 'read more', 'link', 'here']:
                issues.append({
                    "rule": "link_text_clarity",
                    "description": f"Non-descriptive link text: '{link_text}'",
                    "severity": "medium"
                })
            # Check if link text is too long
            elif len(link_text) > self.max_link_text_length:
                issues.append({
                    "rule": "link_text_clarity",
                    "description": f"Link text is too long ({len(link_text)} chars): '{link_text[:50]}...'",
                    "severity": "low"
                })
        
        return issues
    
    def _check_color_contrast(self, html_content: str) -> list:
        """Check color contrast (simplified implementation)"""
        issues = []
        
        # This is a simplified check - in practice, this would use a color contrast analyzer
        # For now, we'll just flag if no explicit contrast checking is done
        
        # Look for inline styles with color declarations
        color_styles = re.findall(r'color\s*:\s*#[0-9a-fA-F]{3,6}', html_content)
        background_styles = re.findall(r'background(-color)?\s*:\s*#[0-9a-fA-F]{3,6}', html_content)
        
        if color_styles and not background_styles:
            issues.append({
                "rule": "color_contrast",
                "description": "Text color specified without background color - contrast cannot be verified",
                "severity": "low"
            })
        
        return issues