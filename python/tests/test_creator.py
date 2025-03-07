import os
import unittest
import tempfile
import datetime
import re

from src.creator import PromptBuilder, create_prompt_text, create_prompt_file, detect_variables
from src.models import PromptObject

class TestPromptBuilder(unittest.TestCase):
    def test_basic_building(self):
        """Test basic functionality of PromptBuilder"""
        builder = PromptBuilder()
        builder.set_name("Test Prompt")
        builder.set_author("Test Author")
        builder.set_description("Test Description")
        builder.set_version("0.1")
        builder.content("This is a test with {var1} and {var2}.")
        builder.set_default("var1", "value1")
        builder.set_default("var2", "value2")
        
        prompt = builder.build()
        
        # Check properties
        self.assertEqual(prompt.metadata["name"], "Test Prompt")
        self.assertEqual(prompt.metadata["author"], "Test Author")
        self.assertEqual(prompt.metadata["description"], "Test Description")
        self.assertEqual(prompt.metadata["version"], "0.1")
        self.assertEqual(prompt.metadata["format_version"], "1.0")
        
        self.assertEqual(prompt.defaults["var1"], "value1")
        self.assertEqual(prompt.defaults["var2"], "value2")
        
        self.assertEqual(prompt.content, "This is a test with {var1} and {var2}.")
        
        # Check text format
        text = prompt.text
        self.assertIn("[METADATA]", text)
        self.assertIn("@format_version 1.0", text)
        self.assertIn("@name Test Prompt", text)
        self.assertIn("[DEFAULTS]", text)
        self.assertIn("@var1 value1", text)
        self.assertIn("[CONTENT]", text)
        self.assertIn("This is a test with {var1} and {var2}.", text)
    
    def test_created_date(self):
        """Test set_created functionality"""
        # With specific date
        builder = PromptBuilder()
        builder.set_created("2023-01-01")
        builder.content("Test")
        prompt = builder.build()
        self.assertEqual(prompt.metadata["created"], "2023-01-01")
        
        # With auto date
        builder = PromptBuilder()
        builder.set_created()
        builder.content("Test")
        prompt = builder.build()
        
        # Check that the date format is YYYY-MM-DD
        date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
        self.assertTrue(date_pattern.match(prompt.metadata["created"]))
    
    def test_set_defaults_batch(self):
        """Test setting multiple defaults at once"""
        builder = PromptBuilder()
        builder.set_defaults({
            "var1": "value1",
            "var2": "value2",
            "var3": "value3"
        })
        builder.content("Test {var1} {var2} {var3}")
        
        prompt = builder.build()
        
        # Check values
        self.assertEqual(prompt.defaults["var1"], "value1")
        self.assertEqual(prompt.defaults["var2"], "value2")
        self.assertEqual(prompt.defaults["var3"], "value3")
    
    def test_set_metadata_batch(self):
        """Test setting multiple metadata fields at once"""
        builder = PromptBuilder()
        builder.set_metadata({
            "name": "Test",
            "author": "Author",
            "version": "0.1",
            "custom": "value"
        })
        builder.content("Test")
        
        prompt = builder.build()
        
        # Check values
        self.assertEqual(prompt.metadata["name"], "Test")
        self.assertEqual(prompt.metadata["author"], "Author")
        self.assertEqual(prompt.metadata["version"], "0.1")
        self.assertEqual(prompt.metadata["custom"], "value")
        self.assertEqual(prompt.metadata["format_version"], "1.0")  # Should be preserved
    
    def test_add_custom_metadata(self):
        """Test adding custom metadata fields"""
        builder = PromptBuilder()
        builder.add_metadata("custom1", "value1")
        builder.add_metadata("custom2", "value2")
        builder.content("Test")
        
        prompt = builder.build()
        
        # Check values
        self.assertEqual(prompt.metadata["custom1"], "value1")
        self.assertEqual(prompt.metadata["custom2"], "value2")
    
    def test_empty_content_error(self):
        """Test error when content is empty"""
        builder = PromptBuilder()
        with self.assertRaises(ValueError) as context:
            builder.build()
        self.assertIn("contenido", str(context.exception).lower())
    
    def test_multiline_values(self):
        """Test handling of multiline values"""
        builder = PromptBuilder()
        builder.set_description("Line 1\nLine 2\nLine 3")
        builder.set_default("var", "Value 1\nValue 2\nValue 3")
        builder.content("Test {var}")
        
        prompt = builder.build()
        text = prompt.text
        
        # Check multiline format
        self.assertIn("@description >", text)
        self.assertIn("  Line 1", text)
        self.assertIn("@var >", text)
        self.assertIn("  Value 1", text)
    
    def test_save_method(self):
        """Test saving to file"""
        builder = PromptBuilder()
        builder.content("Test content")
        
        with tempfile.NamedTemporaryFile(suffix=".prompt", delete=False) as temp:
            temp_path = temp.name
        
        try:
            # Save and check result
            saved_path = builder.save(temp_path)
            self.assertTrue(os.path.exists(saved_path))
            self.assertEqual(os.path.abspath(temp_path), saved_path)
            
            # Check file content
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn("[METADATA]", content)
                self.assertIn("[CONTENT]", content)
                self.assertIn("Test content", content)
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestHelperFunctions(unittest.TestCase):
    def test_create_prompt_text(self):
        """Test create_prompt_text helper function"""
        prompt = create_prompt_text(
            content="Test {var1}",
            defaults={"var1": "value1"},
            metadata={"name": "Test Prompt"}
        )
        
        # Check return type
        self.assertIsInstance(prompt, PromptObject)
        
        # Check values
        self.assertEqual(prompt.content, "Test {var1}")
        self.assertEqual(prompt.defaults["var1"], "value1")
        self.assertEqual(prompt.metadata["name"], "Test Prompt")
        self.assertEqual(prompt.metadata["format_version"], "1.0")
    
    def test_create_prompt_file(self):
        """Test create_prompt_file helper function"""
        with tempfile.NamedTemporaryFile(suffix=".prompt", delete=False) as temp:
            temp_path = temp.name
        
        try:
            # Create and save
            saved_path = create_prompt_file(
                content="Test {var1}",
                defaults={"var1": "value1"},
                metadata={"name": "Test Prompt"},
                filepath=temp_path
            )
            
            # Check result
            self.assertTrue(os.path.exists(saved_path))
            self.assertEqual(os.path.abspath(temp_path), saved_path)
            
            # Check file content
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn("[METADATA]", content)
                self.assertIn("@name Test Prompt", content)
                self.assertIn("@var1 value1", content)
                self.assertIn("Test {var1}", content)
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_detect_variables(self):
        """Test detect_variables helper function"""
        # Simple variables
        vars1 = detect_variables("Test {var1} and {var2}")
        self.assertEqual(vars1, {"var1", "var2"})
        
        # Repeated variables
        vars2 = detect_variables("Test {var1} and {var1} again")
        self.assertEqual(vars2, {"var1"})
        
        # Mixed with text
        vars3 = detect_variables("Normal text without vars")
        self.assertEqual(vars3, set())
        
        # Only alphanumeric chars are considered valid in var names
        vars4 = detect_variables("Test {var_1} and {var-2} and {!invalid}")
        self.assertEqual(vars4, {"var_1"})


if __name__ == '__main__':
    unittest.main()