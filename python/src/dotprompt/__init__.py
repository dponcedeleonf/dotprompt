# __init__.py
from typing import Dict, Optional, Any
__version__ = "0.0.1"

from .core import content, defaults, metadata, variables
from .creator import PromptBuilder, create
from .models import PromptObject
from .validators import file_validator

def save(obj: PromptObject, filepath: str) -> str:
    """Guarda un PromptObject en un archivo .prompt."""
    return obj.save(filepath)

def open(filepath: str) -> PromptObject:
    """Abre un archivo .prompt y devuelve un PromptObject."""
    from .parse import PromptParser
    return PromptParser.from_file(filepath)

def from_text(text: str) -> PromptObject:
    """Parsea texto en formato .prompt y devuelve un PromptObject."""
    from .parse import PromptParser
    return PromptParser(text).obj

def from_json(json_str: str) -> PromptObject:
    """Crea un PromptObject desde un string JSON."""
    return PromptObject.from_json(json_str)

def validate(filepath: str) -> Dict[str, Any]:
    """Valida un archivo .prompt y devuelve un reporte."""
    return file_validator(filepath)

__all__ = [
    'create', 'save', 'open', 'from_text', 'from_json', 'to_json', 'to_text','validate',
    'content', 'defaults', 'metadata', 'variables',
    'PromptObject', 'PromptBuilder'
]