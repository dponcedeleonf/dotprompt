import re
from typing import Dict, List, Optional, Set, Any, Tuple

class PromptValidator:
    """Validates .prompt files for required sections, order, and content."""
    
    SECTION_PATTERN = re.compile(r'\[\s*(METADATA|DEFAULTS|CONTENT)\s*\]', re.IGNORECASE)
    FIELD_PATTERN = re.compile(r'^@(\w[\w\-_]{0,63})\s+(.+)$')
    MULTILINE_PATTERN = re.compile(r'^@(\w[\w\-_]{0,63})\s+>$')

    def __init__(self, text: str = None, filepath: str = None):
        """
        Initializes the validator with content from text or file.
        
        Args:
            text: Content of the .prompt file as a string
            filepath: Path to the .prompt file
            
        Raises:
            ValueError: If neither text nor filepath is provided
            FileNotFoundError: If the specified file doesn't exist
            ValueError: If there's an error reading the file
        """
        if text is None and filepath is None:
            raise ValueError("You must provide either the prompt content or a file path")
        
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.text = f.read()
                self.filepath = filepath
            except FileNotFoundError:
                raise FileNotFoundError(f"The file '{filepath}' was not found")
            except Exception as e:
                raise ValueError(f"Error reading file '{filepath}': {str(e)}")
        else:
            self.text = text
            self.filepath = None
        
        self.lines = self.text.splitlines()
        self._section_positions = self._calculate_section_positions()
        self.sections = {
            'METADATA': self._extract_section('METADATA'),
            'DEFAULTS': self._extract_section('DEFAULTS'),
            'CONTENT': self._extract_section('CONTENT')
        }

    def validate(self) -> Dict[str, Any]:
        """
        Runs all validations and returns the result with errors and warnings.
        
        Returns:
            Dictionary with 'valid', 'errors', and 'warnings' fields
        """
        self.result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        self._validate_sections_presence()
        self._validate_sections_order()
        self._validate_metadata()
        self._validate_defaults()
        self._validate_content()
        self._validate_variables()
        
        return self.result

    def _validate_sections_presence(self):
        """Validates that all required sections are present in the file."""
        found_sections = list(self._section_positions.keys())
        
        if 'METADATA' not in found_sections:
            self.result["valid"] = False
            self.result["errors"].append("Missing required section [METADATA]")
        
        if 'CONTENT' not in found_sections:
            self.result["valid"] = False
            self.result["errors"].append("Missing required section [CONTENT]")

    def _validate_sections_order(self):
        """Validates that sections appear in the correct order: METADATA -> DEFAULTS -> CONTENT."""
        section_positions = self._section_positions
        
        if 'METADATA' in section_positions and 'CONTENT' in section_positions:
            if section_positions['METADATA'] > section_positions['CONTENT']:
                self.result["valid"] = False
                self.result["errors"].append("Incorrect order: [METADATA] must appear before [CONTENT]")
        
        if 'DEFAULTS' in section_positions:
            if 'METADATA' in section_positions and section_positions['DEFAULTS'] < section_positions['METADATA']:
                self.result["valid"] = False
                self.result["errors"].append("Incorrect order: [DEFAULTS] must appear after [METADATA]")
            if 'CONTENT' in section_positions and section_positions['DEFAULTS'] > section_positions['CONTENT']:
                self.result["valid"] = False
                self.result["errors"].append("Incorrect order: [DEFAULTS] must appear before [CONTENT]")

    def _process_line(self, line: str) -> Tuple[Optional[str], bool]:
        """
        Processes a line to identify field names and if it's multiline.
        
        Args:
            line: The line to process
            
        Returns:
            Tuple containing (field_name, is_multiline) or (None, False) if not a field
        """
        line = line.strip()
        if not line or self._is_comment_line(line):
            return None, False
        
        match = self.FIELD_PATTERN.match(line)
        if match:
            return match.group(1), False
        
        match = self.MULTILINE_PATTERN.match(line)
        if match:
            return match.group(1), True
        
        return None, False
    
    def _validate_metadata(self):
        """Validates the METADATA section and its required fields."""
        metadata_section = self.sections['METADATA']
        if not metadata_section:
            return
        
        format_version_found = False
        current_field = None
        
        for line in metadata_section:
            field_name, is_multiline = self._process_line(line)
            if field_name:
                if field_name == 'format_version':
                    format_version_found = True
                current_field = field_name if is_multiline else None
            elif not current_field and line.strip() and not self._is_comment_line(line):
                self.result["warnings"].append(f"Invalid line in [METADATA]: '{line}'")
        
        if not format_version_found:
            self.result["valid"] = False
            self.result["errors"].append("Missing required field @format_version in [METADATA]")

    def _validate_defaults(self):
        """Validates the DEFAULTS section and its field format."""
        defaults_section = self.sections['DEFAULTS']
        if not defaults_section:
            return
        
        current_field = None
        
        for line in defaults_section:
            field_name, is_multiline = self._process_line(line)
            if field_name:
                current_field = field_name if is_multiline else None
            elif not current_field and line.strip() and not self._is_comment_line(line):
                self.result["warnings"].append(f"Invalid line in [DEFAULTS]: '{line}'")

    def _validate_content(self):
        """Validates the CONTENT section for emptiness and proper inline comments."""
        content_section = self.sections['CONTENT']
        if not content_section:
            return
        
        if not ''.join(content_section).strip():
            self.result["valid"] = False
            self.result["errors"].append("The [CONTENT] section is empty")
        
        inline_comment_pattern = re.compile(r'\(%.*?%\)')
        unbalanced_pattern = re.compile(r'\(%[^%]*$|^[^(]*%\)')
        content_text = '\n'.join(content_section)
        
        clean_content = inline_comment_pattern.sub('', content_text)
        if unbalanced_pattern.search(clean_content):
            self.result["warnings"].append("Possible unbalanced inline comment in [CONTENT]")

    def _validate_variables(self):
        """Validates variables and their references between CONTENT and DEFAULTS sections."""
        content_section = self.sections['CONTENT']
        defaults_section = self.sections['DEFAULTS']
        
        if not content_section:
            return
        
        content_text = '\n'.join(content_section)
        processed = re.sub(r'\(%.*?%\)', '', content_text)
        variables = set(re.findall(r'\{(\w+)\}', processed))
        
        if not defaults_section:
            if variables:
                self.result["warnings"].append(
                    f"No [DEFAULTS] section found but variables were detected: {', '.join(sorted(variables))}"
                )
            return
        
        defined_vars = set()
        for line in defaults_section:
            field_name, _ = self._process_line(line)
            if field_name:
                defined_vars.add(field_name)
        
        undefined_vars = variables - defined_vars
        if undefined_vars:
            self.result["warnings"].append(
                f"Variables without default values: {', '.join(sorted(undefined_vars))}"
            )
        
        unused_vars = defined_vars - variables
        if unused_vars:
            self.result["warnings"].append(
                f"Variables defined but not used in [CONTENT]: {', '.join(sorted(unused_vars))}"
            )

    def _is_comment_line(self, line: str) -> bool:
        """
        Determines if a line is a complete comment (% %).
        
        Args:
            line: Line to evaluate
            
        Returns:
            True if the line is a comment, False otherwise
        """
        return line.strip().startswith('(%') and line.strip().endswith('%)')
    
    def _calculate_section_positions(self) -> Dict[str, int]:
        """
        Calculates the positions of all sections in the file.
        
        Returns:
            Dictionary with section names as keys and line indices as values
        """
        positions = {}
        for i, line in enumerate(self.lines):
            match = self.SECTION_PATTERN.match(line.strip())
            if match:
                positions[match.group(1).upper()] = i
        return positions

    def _extract_section(self, section_name: str) -> List[str]:
        """
        Extracts the lines from a specific section.
        
        Args:
            section_name: Section name (METADATA, DEFAULTS, CONTENT)
            
        Returns:
            List of lines in the section or empty list if not found
        """
        if section_name.upper() not in self._section_positions:
            return []
        
        start_line = self._section_positions[section_name.upper()] + 1
        end_line = len(self.lines)
        
        for section, pos in self._section_positions.items():
            if pos > start_line and pos < end_line:
                end_line = pos
        
        return self.lines[start_line:end_line]

def file_validator(filepath: str) -> Dict[str, Any]:
    """
    Validates a .prompt file and returns detailed results.
    
    Args:
        filepath: Path to the .prompt file
        
    Returns:
        Dictionary with 'valid', 'errors', and 'warnings' fields
    """
    validator = PromptValidator(filepath=filepath)
    return validator.validate()

def text_validator(text: str) -> Dict[str, Any]:
    """
    Validates the content of a .prompt file and returns detailed results.
    
    Args:
        text: Content of the .prompt file
        
    Returns:
        Dictionary with 'valid', 'errors', and 'warnings' fields
    """
    validator = PromptValidator(text=text)
    return validator.validate()

def print_validation_result(result: Dict[str, Any], filepath: str = None):
    """
    Prints the validation result in a readable format.
    
    Args:
        result: Validation result dictionary
        filepath: Path to the validated file (optional)
    """
    file_info = f" '{filepath}'" if filepath else ""
    
    if result["valid"]:
        print(f"✅ The file{file_info} is valid according to the specification.")
        if result["warnings"]:
            print("\n⚠️ Warnings:")
            for warning in result["warnings"]:
                print(f"  - {warning}")
    else:
        print(f"❌ The file{file_info} has the following errors:")
        for error in result["errors"]:
            print(f"  - {error}")
        if result["warnings"]:
            print("\n⚠️ Warnings:")
            for warning in result["warnings"]:
                print(f"  - {warning}")