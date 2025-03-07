import os
import unittest
import tempfile
import warnings
from unittest.mock import patch

from src.core import PromptParser, content, defaults, metadata, variables, validate

class TestPromptParser(unittest.TestCase):
    def test_basic_parsing(self):
        """Test basic parsing of a simple prompt"""
        prompt_text = """[METADATA]
@format_version 1.0
@name Test Prompt

[DEFAULTS]
@var1 value1
@var2 value2

[CONTENT]
This is a test with {var1} and {var2}."""

        parser = PromptParser(prompt_text)
        
        # Check metadata
        self.assertEqual(parser.metadata["format_version"], "1.0")
        self.assertEqual(parser.metadata["name"], "Test Prompt")
        
        # Check defaults
        self.assertEqual(parser.defaults["var1"], "value1")
        self.assertEqual(parser.defaults["var2"], "value2")
        
        # Check content
        self.assertIn("This is a test with {var1} and {var2}", parser.content)
        
        # Check variables
        self.assertEqual(parser.variables, {"var1", "var2"})
    
    def test_multiline_values(self):
        """Test parsing with multiline values"""
        prompt_text = """[METADATA]
@format_version 1.0
@description >
  This is a
  multiline description

[DEFAULTS]
@var1 >
  This is a
  multiline value

[CONTENT]
Using {var1} here."""

        parser = PromptParser(prompt_text)
        
        # Check multiline values
        self.assertEqual(parser.metadata["description"], "This is a\n  multiline description")
        self.assertEqual(parser.defaults["var1"], "This is a\n  multiline value")
    
    def test_comments(self):
        """Test parsing with comments"""
        prompt_text = """[METADATA]
# This is a comment
@format_version 1.0

[CONTENT]
This is content with a (# comment #) inside."""

        parser = PromptParser(prompt_text)
        processed = parser.process()
        
        # Comments in CONTENT should be removed
        self.assertNotIn("comment", processed)
    
    def test_variable_placeholders(self):
        """Test variable placeholder syntax"""
        prompt_text = """[METADATA]
@format_version 1.0

[CONTENT]
Normal {var1} and {{var2}} should both work."""

        parser = PromptParser(prompt_text)
        
        # Both syntaxes should be detected
        self.assertEqual(parser.variables, {"var1", "var2"})
    
    def test_process_with_values(self):
        """Test processing with variable values"""
        prompt_text = """[METADATA]
@format_version 1.0

[DEFAULTS]
@var1 default1

[CONTENT]
Values: {var1}, {var2}."""

        parser = PromptParser(prompt_text)
        
        # Process with custom values
        with warnings.catch_warnings(record=True) as w:
            result = parser.process(var1="custom1", var2="custom2")
            
            # No warnings should be raised
            self.assertEqual(len(w), 0)
        
        # Check substitution
        self.assertEqual(result, "Values: custom1, custom2.")
    
    def test_process_with_defaults(self):
        """Test processing with default values"""
        prompt_text = """[METADATA]
@format_version 1.0

[DEFAULTS]
@var1 default1

[CONTENT]
Values: {var1}, {var2}."""

        parser = PromptParser(prompt_text)
        
        # Process with only var2, var1 should use default
        with warnings.catch_warnings(record=True) as w:
            result = parser.process(var2="custom2")
            
            # Warning for using default
            self.assertEqual(len(w), 1)
            self.assertIn("default", str(w[0].message))
        
        # Check substitution
        self.assertEqual(result, "Values: default1, custom2.")
    
    def test_process_with_missing_values(self):
        """Test processing with missing values"""
        prompt_text = """[METADATA]
@format_version 1.0

[CONTENT]
Values: {var1}, {var2}."""

        parser = PromptParser(prompt_text)
        
        # Process with only var1, var2 should remain as placeholder
        with warnings.catch_warnings(record=True) as w:
            result = parser.process(var1="custom1")
            
            # Warning for missing value
            self.assertEqual(len(w), 1)
            self.assertIn("placeholder", str(w[0].message))
        
        # Check that var2 remains as placeholder
        self.assertEqual(result, "Values: custom1, {var2}.")
    
    def test_invalid_kwargs(self):
        """Test processing with invalid kwargs"""
        prompt_text = """[METADATA]
@format_version 1.0

[CONTENT]
Value: {var1}."""

        parser = PromptParser(prompt_text)
        
        # Process with invalid kwargs
        with self.assertRaises(ValueError) as context:
            parser.process(var1="valid", invalid_var="value")
        
        self.assertIn("invalid_var", str(context.exception))
    
    def test_validation_errors(self):
        """Test validation errors"""
        # Missing CONTENT section
        with self.assertRaises(ValueError) as context:
            PromptParser("[METADATA]\n@format_version 1.0")
        self.assertIn("CONTENT", str(context.exception))
        
        # Missing format_version
        with self.assertRaises(ValueError) as context:
            PromptParser("[METADATA]\n@name Test\n\n[CONTENT]\nTest")
        self.assertIn("format_version", str(context.exception))
        
        # Wrong order of sections
        with self.assertRaises(ValueError) as context:
            PromptParser("[CONTENT]\nTest\n\n[DEFAULTS]\n@var val")
        self.assertIn("orden", str(context.exception))
    
    def test_get_variables_info(self):
        """Test getting variable information"""
        prompt_text = """[METADATA]
@format_version 1.0

[DEFAULTS]
@var1 default1

[CONTENT]
Values: {var1}, {var2}."""

        parser = PromptParser(prompt_text)
        vars_info = parser.get_variables_info()
        
        # Check variable info
        self.assertTrue(vars_info["var1"]["has_default"])
        self.assertEqual(vars_info["var1"]["default_value"], "default1")
        
        self.assertFalse(vars_info["var2"]["has_default"])
        self.assertIsNone(vars_info["var2"]["default_value"])


class TestHelperFunctions(unittest.TestCase):
    def setUp(self):
        # Create a temporary file with test content
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".prompt")
        self.temp_file.write("""[METADATA]
@format_version 1.0
@name Test

[DEFAULTS]
@var1 default1

[CONTENT]
Test {var1} and {var2}""".encode('utf-8'))
        self.temp_file.close()
    
    def tearDown(self):
        # Clean up the temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_content_function(self):
        """Test the content helper function"""
        # With file
        result = content(self.temp_file.name, var2="value2")
        self.assertEqual(result, "Test default1 and value2")
        
        # With string
        prompt_str = "[METADATA]\n@format_version 1.0\n\n[CONTENT]\nTest {var}"
        result = content(prompt_str, var="value")
        self.assertEqual(result, "Test value")
    
    def test_defaults_function(self):
        """Test the defaults helper function"""
        # With file
        result = defaults(self.temp_file.name)
        self.assertEqual(result, {"var1": "default1"})
        
        # With string
        prompt_str = "[METADATA]\n@format_version 1.0\n\n[DEFAULTS]\n@var value\n\n[CONTENT]\nTest"
        result = defaults(prompt_str)
        self.assertEqual(result, {"var": "value"})
    
    def test_metadata_function(self):
        """Test the metadata helper function"""
        # With file
        result = metadata(self.temp_file.name)
        self.assertEqual(result["name"], "Test")
        
        # With string
        prompt_str = "[METADATA]\n@format_version 1.0\n@key value\n\n[CONTENT]\nTest"
        result = metadata(prompt_str)
        self.assertEqual(result["key"], "value")
    
    def test_variables_function(self):
        """Test the variables helper function"""
        # With file
        result = variables(self.temp_file.name)
        self.assertTrue(result["var1"]["has_default"])
        self.assertFalse(result["var2"]["has_default"])
        
        # With string
        prompt_str = "[METADATA]\n@format_version 1.0\n\n[CONTENT]\nTest {var}"
        result = variables(prompt_str)
        self.assertFalse(result["var"]["has_default"])
    
    def test_validate_function(self):
        """Test the validate helper function"""
        # Valid prompt
        result = validate(self.temp_file.name)
        self.assertTrue(result["valid"])
        
        # Invalid prompt
        prompt_str = "[METADATA]\n@wrong format\n\n[CONTENT]\nTest"
        result = validate(prompt_str)
        self.assertFalse(result["valid"])


if __name__ == '__main__':
    unittest.main()