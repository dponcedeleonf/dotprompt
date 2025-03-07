"""
dotprompt - A library for working with prompt template files using the .prompt format

This package provides tools to work with .prompt files, including parsing,
creating, validating, and using prompt templates.

"""

# Version
__version__ = "0.0.1"

# Import main API functions to expose at top level
from .core import content, defaults, metadata, variables, validate
from .creator import PromptBuilder, create_prompt_text, create_prompt_file, detect_variables
from .validators import file_validator, text_validator, print_validation_result

# Import main classes for advanced usage
from .core import PromptParser
from .models import PromptObject
from .validators import PromptValidator

# For cleaner imports
__all__ = [
    # Core functions
    'content',
    'defaults',
    'metadata',
    'variables',
    'validate',
    
    # Creator functions
    'PromptBuilder',
    'create_prompt_text',
    'create_prompt_file',
    'detect_variables',
    
    # Validator functions
    'file_validator',
    'text_validator',
    'print_validation_result',
    
    # Classes for advanced usage
    'PromptParser',
    'PromptObject',
    'PromptValidator',
]