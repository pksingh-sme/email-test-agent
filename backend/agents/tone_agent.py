"""
Tone Agent for the Email QA Agentic Platform
Checks copy clarity, tone, grammar, and spam indicators
"""

from typing import Dict, Any
import re


class ToneAgent:
    def __init__(self):
        # Define spam keywords and phrases
        self.spam_keywords = [
            "urgent", "act now", "limited time", "free", "guarantee", 
            "no obligation", "click here", "buy now", "instant", "miracle"
        ]
        
        # Define complex sentence indicators
        self.complex_sentence_indicators = [
            "however", "nevertheless", "moreover", "furthermore", "consequently",
            "therefore", "thus", "hence", "accordingly", "notwithstanding"
        ]
    
    def analyze(self, email_id: str, html_content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze email for copy clarity, tone, and spam indicators
        
        Args:
            email_id: Unique identifier for the email
            html_content: HTML content of the email
            metadata: Metadata associated with the email
            
        Returns:
            Dict containing tone analysis results
        """
        issues = []
        
        # Extract text content from HTML
        text_content = self._extract_text_content(html_content)
        
        # Check subject line for spam indicators
        subject = metadata.get("subject", "")
        subject_spam_issues = self._check_subject_for_spam(subject)
        issues.extend(subject_spam_issues)
        
        # Check for complex sentences
        complex_sentence_issues = self._check_complex_sentences(text_content)
        issues.extend(complex_sentence_issues)
        
        # Check for clarity issues
        clarity_issues = self._check_clarity(text_content)
        issues.extend(clarity_issues)
        
        # Check for grammar issues (simplified)
        grammar_issues = self._check_grammar(text_content)
        issues.extend(grammar_issues)
        
        return {
            "agent": "tone",
            "email_id": email_id,
            "issues": issues,
            "summary": f"Found {len(issues)} tone/clarity issues"
        }
    
    def _extract_text_content(self, html_content: str) -> str:
        """Extract text content from HTML"""
        # Remove HTML tags
        clean_text = re.sub('<[^<]+?>', '', html_content)
        # Remove extra whitespace
        clean_text = re.sub('\s+', ' ', clean_text).strip()
        return clean_text
    
    def _check_subject_for_spam(self, subject: str) -> list:
        """Check subject line for spam indicators"""
        issues = []
        
        # Convert to lowercase for comparison
        subject_lower = subject.lower()
        
        # Check for spam keywords
        found_spam_keywords = [keyword for keyword in self.spam_keywords if keyword in subject_lower]
        
        if found_spam_keywords:
            issues.append({
                "rule": "spam_indicators",
                "description": f"Spam keywords detected in subject: {', '.join(found_spam_keywords)}",
                "severity": "high"
            })
        
        # Check for excessive exclamation marks
        if subject.count('!') > 2:
            issues.append({
                "rule": "spam_indicators",
                "description": "Too many exclamation marks in subject",
                "severity": "medium"
            })
        
        # Check for all caps
        if subject.isupper() and len(subject) > 10:
            issues.append({
                "rule": "spam_indicators",
                "description": "Subject line is all caps",
                "severity": "medium"
            })
        
        return issues
    
    def _check_complex_sentences(self, text_content: str) -> list:
        """Check for overly complex sentences"""
        issues = []
        
        # Split text into sentences
        sentences = re.split(r'[.!?]+', text_content)
        
        # Check for sentences with too many complex indicators
        for sentence in sentences:
            complex_count = sum(1 for indicator in self.complex_sentence_indicators 
                              if indicator in sentence.lower())
            
            if complex_count > 2:
                issues.append({
                    "rule": "complex_sentences",
                    "description": f"Sentence contains too many complex connectors: {sentence[:50]}...",
                    "severity": "low"
                })
        
        return issues
    
    def _check_clarity(self, text_content: str) -> list:
        """Check for clarity issues"""
        issues = []
        
        # Check for passive voice (simplified detection)
        passive_voice_patterns = [
            r'\b\w+ed\b',  # Words ending in 'ed'
            r'\bbeen\b',   # 'been' verb
            r'\bbeing\b'   # 'being' verb
        ]
        
        passive_count = 0
        for pattern in passive_voice_patterns:
            passive_count += len(re.findall(pattern, text_content, re.IGNORECASE))
        
        # If too many passive constructions
        if passive_count > 10:
            issues.append({
                "rule": "clarity",
                "description": "Text contains excessive passive voice constructions",
                "severity": "low"
            })
        
        return issues
    
    def _check_grammar(self, text_content: str) -> list:
        """Check for basic grammar issues (simplified)"""
        issues = []
        
        # Check for repeated words
        repeated_words = re.findall(r'\b(\w+)\s+\1\b', text_content, re.IGNORECASE)
        
        if repeated_words:
            issues.append({
                "rule": "grammar",
                "description": f"Repeated words found: {', '.join(set(repeated_words))}",
                "severity": "low"
            })
        
        return issues