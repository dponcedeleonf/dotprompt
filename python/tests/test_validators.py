import os
import unittest
import tempfile

from src.validators import PromptValidator, file_validator, text_validator, print_validation_result

class TestPromptValidator(unittest.TestCase):
    def test_valid_prompt(self):
        """Test a valid prompt file"""
        prompt_text = """[METADATA]
@format_version 1.0
@name Test Prompt

[DEFAULTS]
@var1 value1
@var2 value2

[CONTENT]
This is a test with {var1} and {var2}."""

        validator = PromptValidator(text=prompt_text)
        result = validator.validate()
        
        self.assertTrue(result["valid"])
        self.assertEqual(len(result["errors"]), 0)
        self.assertEqual(len(result["warnings"]), 0)
    
    def test_missing_required_sections(self):
        """Test validation of missing required sections"""
        # Missing METADATA
        prompt1 = """[CONTENT]
Test content"""
        validator = PromptValidator(text=prompt1)
        result = validator.validate()
        self.assertFalse(result["valid"])
        self.assertIn("Falta la sección obligatoria [METADATA]", result["errors"])
        
        # Missing CONTENT
        prompt2 = """[METADATA]
@format_version 1.0"""
        validator = PromptValidator(text=prompt2)
        result = validator.validate()
        self.assertFalse(result["valid"])
        self.assertIn("Falta la sección obligatoria [CONTENT]", result["errors"])
    
    def test_section_order(self):
        """Test validation of section order"""
        # CONTENT before METADATA
        prompt1 = """[CONTENT]
Test content

[METADATA]
@format_version 1.0"""
        validator = PromptValidator(text=prompt1)
        result = validator.validate()
        self.assertFalse(result["valid"])
        self.assertIn("Orden incorrecto", result["errors"][0])
        self.assertIn("METADATA", result["errors"][0])
        self.assertIn("CONTENT", result["errors"][0])
        
        # DEFAULTS after CONTENT
        prompt2 = """[METADATA]
@format_version 1.0

[CONTENT]
Test {var}

[DEFAULTS]
@var value"""
        validator = PromptValidator(text=prompt2)
        result = validator.validate()
        self.assertFalse(result["valid"])
        self.assertIn("Orden incorrecto", result["errors"][0])
        self.assertIn("DEFAULTS", result["errors"][0])
        self.assertIn("CONTENT", result["errors"][0])
        
        # DEFAULTS before METADATA
        prompt3 = """[DEFAULTS]
@var value

[METADATA]
@format_version 1.0

[CONTENT]
Test"""
        validator = PromptValidator(text=prompt3)
        result = validator.validate()
        self.assertFalse(result["valid"])
        self.assertIn("Orden incorrecto", result["errors"][0])
        self.assertIn("DEFAULTS", result["errors"][0])
        self.assertIn("METADATA", result["errors"][0])
    
    def test_missing_format_version(self):
        """Test validation of missing format_version"""
        prompt = """[METADATA]
@name Test Prompt

[CONTENT]
Test content"""
        validator = PromptValidator(text=prompt)
        result = validator.validate()
        self.assertFalse(result["valid"])
        self.assertIn("Falta el campo obligatorio @format_version", result["errors"][0])
    
    def test_empty_content(self):
        """Test validation of empty content"""
        prompt = """[METADATA]
@format_version 1.0

[CONTENT]
"""
        validator = PromptValidator(text=prompt)
        result = validator.validate()
        self.assertFalse(result["valid"])
        self.assertIn("La sección [CONTENT] está vacía", result["errors"][0])
    
    def test_variables_validation(self):
        """Test validation of variables"""
        # Variable without default
        prompt1 = """[METADATA]
@format_version 1.0

[CONTENT]
Test {var1} and {var2}"""
        validator = PromptValidator(text=prompt1)
        result = validator.validate()
        self.assertTrue(result["valid"])  # It's a warning, not an error
        self.assertIn("No hay sección [DEFAULTS]", result["warnings"][0])
        
        # Variable without default but with DEFAULTS section
        prompt2 = """[METADATA]
@format_version 1.0

[DEFAULTS]
@var1 value1

[CONTENT]
Test {var1} and {var2}"""
        validator = PromptValidator(text=prompt2)
        result = validator.validate()
        self.assertTrue(result["valid"])
        self.assertIn("Variables sin valor por defecto: var2", result["warnings"][0])
        
        # Unused variable default
        prompt3 = """[METADATA]
@format_version 1.0

[DEFAULTS]
@var1 value1
@unused value

[CONTENT]
Test {var1}"""
        validator = PromptValidator(text=prompt3)
        result = validator.validate()
        self.assertTrue(result["valid"])
        self.assertIn("Variables definidas pero no utilizadas", result["warnings"][0])
        self.assertIn("unused", result["warnings"][0])
    
    def test_invalid_syntax(self):
        """Test validation of invalid syntax"""
        # Invalid line in METADATA
        prompt1 = """[METADATA]
@format_version 1.0
invalid line

[CONTENT]
Test"""
        validator = PromptValidator(text=prompt1)
        result = validator.validate()
        self.assertTrue(result["valid"])  # It's just a warning
        self.assertIn("Línea inválida en [METADATA]", result["warnings"][0])
        
        # Invalid line in DEFAULTS
        prompt2 = """[METADATA]
@format_version 1.0

[DEFAULTS]
invalid line

[CONTENT]
Test"""
        validator = PromptValidator(text=prompt2)
        result = validator.validate()
        self.assertTrue(result["valid"])  # It's just a warning
        self.assertIn("Línea inválida en [DEFAULTS]", result["warnings"][0])
        
        # Possible unbalanced comment
        prompt3 = """[METADATA]
@format_version 1.0

[CONTENT]
Test with (# unbalanced comment"""
        validator = PromptValidator(text=prompt3)
        result = validator.validate()
        self.assertTrue(result["valid"])  # It's just a warning
        self.assertIn("Posible comentario inline desbalanceado", result["warnings"][0])
    
    def test_file_loading(self):
        """Test loading from file"""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".prompt", delete=False) as temp:
            temp.write("""[METADATA]
@format_version 1.0

[CONTENT]
Test content""".encode('utf-8'))
            temp_path = temp.name
        
        try:
            # Validate from file
            validator = PromptValidator(filepath=temp_path)
            result = validator.validate()
            self.assertTrue(result["valid"])
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_initialization_error(self):
        """Test initialization error"""
        with self.assertRaises(ValueError):
            PromptValidator()  # No text or filepath


class TestHelperFunctions(unittest.TestCase):
    def setUp(self):
        # Create a temporary file with test content
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".prompt")
        self.temp_file.write("""[METADATA]
@format_version 1.0

[CONTENT]
Test content""".encode('utf-8'))
        self.temp_file.close()
    
    def tearDown(self):
        # Clean up the temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_file_validator(self):
        """Test file_validator helper function"""
        result = file_validator(self.temp_file.name)
        self.assertTrue(result["valid"])
    
    def test_text_validator(self):
        """Test text_validator helper function"""
        # Valid text
        result1 = text_validator("""[METADATA]
@format_version 1.0

[CONTENT]
Test""")
        self.assertTrue(result1["valid"])
        
        # Invalid text
        result2 = text_validator("""[METADATA]
@missing_format_version

[CONTENT]
Test""")
        self.assertFalse(result2["valid"])
    
    def test_print_validation_result(self):
        """Test print_validation_result function"""
        # This is mainly to check that the function runs without errors
        # since it just prints to stdout
        
        # Valid result
        result1 = {
            "valid": True,
            "errors": [],
            "warnings": ["Warning 1", "Warning 2"]
        }
        
        # Invalid result
        result2 = {
            "valid": False,
            "errors": ["Error 1", "Error 2"],
            "warnings": ["Warning 1"]
        }
        
        # These should not raise exceptions
        with unittest.mock.patch('builtins.print'):
            print_validation_result(result1, "test.prompt")
            print_validation_result(result2)


if __name__ == '__main__':
    unittest.main()