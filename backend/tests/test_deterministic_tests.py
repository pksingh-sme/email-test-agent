"""
Unit tests for deterministic QA tests
"""

import unittest
from deterministic_tests import (
    check_alt_text, check_links, check_subject_line, 
    check_preheader, check_template_meta, check_width,
    check_background_color, check_image_dimensions, check_long_copy
)


class TestDeterministicTests(unittest.TestCase):
    
    def test_check_alt_text_pass(self):
        """Test ALT text check passes when ALT text is present"""
        html = '<img src="image.jpg" alt="A beautiful image">'
        results = check_alt_text(html)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['status'], 'pass')
    
    def test_check_alt_text_fail(self):
        """Test ALT text check fails when ALT text is missing"""
        html = '<img src="image.jpg">'
        results = check_alt_text(html)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['status'], 'fail')
    
    def test_check_links_pass(self):
        """Test links check passes with valid links"""
        html = '<a href="https://example.com">Valid Link</a>'
        results = check_links(html)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['status'], 'pass')
    
    def test_check_links_fail(self):
        """Test links check fails with malformed links"""
        html = '<a href="javascript:alert()">Invalid Link</a>'
        results = check_links(html)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['status'], 'fail')
    
    def test_check_subject_line_pass(self):
        """Test subject line check passes when subject is present"""
        metadata = {'subject': 'Test Subject'}
        results = check_subject_line(metadata)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['status'], 'pass')
    
    def test_check_subject_line_fail(self):
        """Test subject line check fails when subject is missing"""
        metadata = {'subject': ''}
        results = check_subject_line(metadata)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['status'], 'fail')
    
    def test_check_preheader_pass(self):
        """Test preheader check passes when preheader is present"""
        metadata = {'preheader': 'Test Preheader'}
        results = check_preheader(metadata)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['status'], 'pass')
    
    def test_check_preheader_fail(self):
        """Test preheader check fails when preheader is missing"""
        metadata = {'preheader': ''}
        results = check_preheader(metadata)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['status'], 'fail')


if __name__ == '__main__':
    unittest.main()