#models.py
import os
from typing import Dict, Any

class PromptObject:
    """
    Representa un prompt completo con acceso estructurado a sus partes.
    
    Attributes:
        metadata (dict): Metadatos del prompt
        defaults (dict): Valores por defecto para variables
        content (str): Contenido del prompt
        text (str): Representación textual completa del prompt en formato .prompt
    """
    
    def __init__(self, metadata: dict, defaults: dict, content: str, text: str):
        """
        Inicializa un objeto PromptObject.
        
        Args:
            metadata (dict): Metadatos del prompt
            defaults (dict): Valores por defecto para variables
            content (str): Contenido del prompt
            text (str): Representación textual completa del prompt
        """
        self.metadata = metadata
        self.defaults = defaults
        self.content = content
        self.text = text
    
    def __str__(self) -> str:
        """Devuelve la representación textual completa del prompt."""
        return self.text
    
    def save(self, filepath: str) -> str:
        """
        Guarda el prompt en un archivo.
        
        Args:
            filepath (str): Ruta donde guardar el archivo
            
        Returns:
            str: Ruta absoluta al archivo guardado
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.text)
        return os.path.abspath(filepath)