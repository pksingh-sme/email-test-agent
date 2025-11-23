"""
Deterministic QA tests for email validation.
All tests return a list of issues in the format:
{
    "test_name": str,
    "status": "pass" | "fail",
    "details": str
}
"""

from typing import List, Dict, Any
from bs4 import BeautifulSoup
import re


def check_alt_text(html_content: str) -> List[Dict[str, Any]]:
    """Check for missing ALT text in images"""
    soup = BeautifulSoup(html_content, 'html.parser')
    images = soup.find_all('img')
    
    issues = []
    for img in images:
        alt_text = img.get('alt')
        if not alt_text or alt_text.strip() == '':
            issues.append({
                "test_name": "alt_text",
                "status": "fail",
                "details": f"Image missing ALT text: {img}"
            })
        else:
            issues.append({
                "test_name": "alt_text",
                "status": "pass",
                "details": "ALT text present"
            })
    
    if not issues:
        issues.append({
            "test_name": "alt_text",
            "status": "pass",
            "details": "No images found, ALT text check passed"
        })
    
    return issues


def check_links(html_content: str) -> List[Dict[str, Any]]:
    """Check for broken or malformed links"""
    soup = BeautifulSoup(html_content, 'html.parser')
    links = soup.find_all('a', href=True)
    
    issues = []
    for link in links:
        href = link['href']
        # Check for malformed URLs
        if not href.startswith(('http://', 'https://', 'mailto:', '#')):
            issues.append({
                "test_name": "links",
                "status": "fail",
                "details": f"Malformed link: {href}"
            })
        else:
            issues.append({
                "test_name": "links",
                "status": "pass",
                "details": f"Valid link: {href}"
            })
    
    if not issues:
        issues.append({
            "test_name": "links",
            "status": "pass",
            "details": "No links found, link check passed"
        })
    
    return issues


def check_subject_line(metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Check for missing subject line"""
    subject = metadata.get('subject', '')
    
    if not subject or subject.strip() == '':
        return [{
            "test_name": "subject_line",
            "status": "fail",
            "details": "Missing subject line"
        }]
    else:
        return [{
            "test_name": "subject_line",
            "status": "pass",
            "details": f"Subject line present: {subject}"
        }]


def check_preheader(metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Check for missing preheader"""
    preheader = metadata.get('preheader', '')
    
    if not preheader or preheader.strip() == '':
        return [{
            "test_name": "preheader",
            "status": "fail",
            "details": "Missing preheader"
        }]
    else:
        return [{
            "test_name": "preheader",
            "status": "pass",
            "details": "Preheader present"
        }]


def check_template_meta(metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Check template metadata (name, locale)"""
    issues = []
    
    template_name = metadata.get('template_name', '')
    if not template_name or template_name.strip() == '':
        issues.append({
            "test_name": "template_meta",
            "status": "fail",
            "details": "Missing template name"
        })
    else:
        issues.append({
            "test_name": "template_meta",
            "status": "pass",
            "details": f"Template name present: {template_name}"
        })
    
    locale = metadata.get('locale', '')
    if not locale or locale.strip() == '':
        issues.append({
            "test_name": "template_meta",
            "status": "fail",
            "details": "Missing locale"
        })
    else:
        issues.append({
            "test_name": "template_meta",
            "status": "pass",
            "details": f"Locale present: {locale}"
        })
    
    return issues


def check_width(html_content: str) -> List[Dict[str, Any]]:
    """Check for width mismatch"""
    # This is a simplified check - in practice, this would be more complex
    # depending on the email framework being used
    issues = []
    
    # Look for common width attributes
    if 'width=' not in html_content and 'style=' not in html_content:
        issues.append({
            "test_name": "width",
            "status": "fail",
            "details": "No width attributes found in email"
        })
    else:
        issues.append({
            "test_name": "width",
            "status": "pass",
            "details": "Width attributes found"
        })
    
    return issues


def check_background_color(html_content: str) -> List[Dict[str, Any]]:
    """Check for background color mismatch"""
    issues = []
    
    # Simple check for background color declarations
    if 'background-color:' not in html_content and 'bgcolor=' not in html_content:
        issues.append({
            "test_name": "background_color",
            "status": "fail",
            "details": "No background color declarations found"
        })
    else:
        issues.append({
            "test_name": "background_color",
            "status": "pass",
            "details": "Background color declarations found"
        })
    
    return issues


def check_image_dimensions(html_content: str) -> List[Dict[str, Any]]:
    """Check for missing image dimensions"""
    soup = BeautifulSoup(html_content, 'html.parser')
    images = soup.find_all('img')
    
    issues = []
    for img in images:
        width = img.get('width')
        height = img.get('height')
        
        if not width and not height:
            issues.append({
                "test_name": "image_dimensions",
                "status": "fail",
                "details": f"Image missing dimensions: {img}"
            })
        else:
            issues.append({
                "test_name": "image_dimensions",
                "status": "pass",
                "details": "Image dimensions present"
            })
    
    if not issues:
        issues.append({
            "test_name": "image_dimensions",
            "status": "pass",
            "details": "No images found, dimension check passed"
        })
    
    return issues


def check_long_copy(html_content: str) -> List[Dict[str, Any]]:
    """Check for long text lines (>200 chars)"""
    soup = BeautifulSoup(html_content, 'html.parser')
    # Get all text content
    text_elements = soup.find_all(string=True)
    
    issues = []
    for text in text_elements:
        # Skip whitespace-only text
        if text.strip() and len(text.strip()) > 200:
            issues.append({
                "test_name": "long_copy",
                "status": "fail",
                "details": f"Long text line found ({len(text.strip())} chars)"
            })
    
    if not issues:
        issues.append({
            "test_name": "long_copy",
            "status": "pass",
            "details": "No excessively long text lines found"
        })
    
    return issues


# Main function to run all deterministic tests
def run_all_deterministic_tests(html_content: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Run all deterministic tests and return consolidated results"""
    all_issues = []
    
    # Run each test
    all_issues.extend(check_alt_text(html_content))
    all_issues.extend(check_links(html_content))
    all_issues.extend(check_subject_line(metadata))
    all_issues.extend(check_preheader(metadata))
    all_issues.extend(check_template_meta(metadata))
    all_issues.extend(check_width(html_content))
    all_issues.extend(check_background_color(html_content))
    all_issues.extend(check_image_dimensions(html_content))
    all_issues.extend(check_long_copy(html_content))
    
    return all_issues