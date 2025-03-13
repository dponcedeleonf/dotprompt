# core.py
from .parse import PromptParser
from .models import PromptObject
from typing import Dict, Any

def content(filepath: str, **kwargs: Any) -> str:
    """Procesa el contenido de un archivo .prompt."""
    prompt = PromptParser.from_file(filepath)
    return prompt.process(**kwargs)

def defaults(filepath: str) -> Dict[str, str]:
    """Devuelve los defaults de un archivo .prompt."""
    return PromptParser.from_file(filepath).defaults

def metadata(filepath: str) -> Dict[str, str]:
    """Devuelve los metadata de un archivo .prompt."""
    return PromptParser.from_file(filepath).metadata

def variables(filepath: str) -> Dict[str, Dict[str, Any]]:
    """Devuelve información sobre las variables en el contenido."""
    prompt = PromptParser.from_file(filepath)
    return prompt.get_variables_info()