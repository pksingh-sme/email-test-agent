"""
Test runner for the Email QA Agentic Platform
"""

import unittest
import sys
import os

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with error code if tests failed
    sys.exit(not result.wasSuccessful())