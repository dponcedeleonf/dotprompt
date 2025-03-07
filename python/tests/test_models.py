import os
import unittest
import tempfile

from src.models import PromptObject

class TestPromptObject(unittest.TestCase):
    def test_initialization(self):
        """Test basic initialization"""
        metadata = {"format_version": "1.0", "name": "Test"}
        defaults = {"var1": "value1"}
        content = "Test {var1}"
        text = "[METADATA]\n@format_version 1.0\n@name Test\n\n[DEFAULTS]\n@var1 value1\n\n[CONTENT]\nTest {var1}"
        
        obj = PromptObject(metadata, defaults, content, text)
        
        # Check properties
        self.assertEqual(obj.metadata, metadata)