#creator.py
import os
import re
import datetime
from typing import Dict, Any, Optional, Union, TextIO

# Importamos PromptObject desde models.py
from models import PromptObject

class PromptBuilder:
    """
    Constructor fluido para crear archivos .prompt programáticamente.
    
    """
    
    def __init__(self):
        """Inicializa un nuevo constructor de prompts."""
        self._metadata = {"format_version": "1.0"}
        self._defaults = {}
        self._content = ""
    
    # Métodos para metadata
    
    def set_name(self, name: str) -> 'PromptBuilder':
        """Establece el nombre del prompt."""
        self._metadata["name"] = name
        return self
    
    def set_author(self, author: str) -> 'PromptBuilder':
        """Establece el autor del prompt."""
        self._metadata["author"] = author
        return self
    
    def set_description(self, description: str) -> 'PromptBuilder':
        """Establece la descripción del prompt."""
        self._metadata["description"] = description
        return self
    
    def set_version(self, version: str) -> 'PromptBuilder':
        """Establece la versión del prompt."""
        self._metadata["version"] = version
        return self
    
    def set_created(self, date: Optional[str] = None) -> 'PromptBuilder':
        """
        Establece la fecha de creación del prompt.
        
        Args:
            date (str, optional): Fecha en formato YYYY-MM-DD. Si no se especifica, se usa la fecha actual.
        """
        if date is None:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        self._metadata["created"] = date
        return self
    
    def add_metadata(self, key: str, value: str) -> 'PromptBuilder':
        """
        Añade un campo personalizado a la metadata.
        
        Args:
            key (str): Nombre del campo.
            value (str): Valor del campo.
        """
        self._metadata[key] = value
        return self
    
    def set_metadata(self, metadata: Dict[str, str]) -> 'PromptBuilder':
        """
        Establece múltiples campos de metadata a la vez.
        
        Args:
            metadata (Dict[str, str]): Diccionario con los campos a establecer.
        
        Note:
            El campo format_version siempre se mantiene con el valor por defecto.
        """
        # Preservar format_version
        format_version = self._metadata.get("format_version", "1.0")
        self._metadata.update(metadata)
        self._metadata["format_version"] = format_version
        return self
    
    # Métodos para defaults
    
    def set_default(self, key: str, value: str) -> 'PromptBuilder':
        """
        Establece un valor por defecto para una variable.
        
        Args:
            key (str): Nombre de la variable.
            value (str): Valor por defecto.
        """
        self._defaults[key] = value
        return self
    
    def set_defaults(self, defaults: Dict[str, str]) -> 'PromptBuilder':
        """
        Establece múltiples valores por defecto a la vez.
        
        Args:
            defaults (Dict[str, str]): Diccionario con las variables y sus valores por defecto.
        """
        self._defaults.update(defaults)
        return self
    
    # Métodos para content
    
    def content(self, text: str) -> 'PromptBuilder':
        """
        Establece el contenido del prompt.
        
        Args:
            text (str): Contenido del prompt, puede incluir variables como {variable}.
        """
        self._content = text.strip()
        return self
    
    # Métodos para generar el prompt
    
    def build(self) -> PromptObject:
        """
        Construye y devuelve un objeto PromptObject con las partes del prompt.
        
        Returns:
            PromptObject: Objeto con acceso estructurado al prompt.
        """
        if not self._content:
            raise ValueError("El contenido del prompt no puede estar vacío")
        
        lines = ["[METADATA]"]
        
        # Agregar campos de metadata
        for key, value in self._metadata.items():
            if "\n" in str(value):
                # Valor multilínea
                lines.append(f"@{key} >")
                for line in str(value).split("\n"):
                    lines.append(f"  {line}")
            else:
                lines.append(f"@{key} {value}")
        
        # Agregar defaults si hay
        if self._defaults:
            lines.append("")
            lines.append("[DEFAULTS]")
            
            for key, value in self._defaults.items():
                if "\n" in str(value):
                    # Valor multilínea
                    lines.append(f"@{key} >")
                    for line in str(value).split("\n"):
                        lines.append(f"  {line}")
                else:
                    lines.append(f"@{key} {value}")
        
        # Agregar contenido
        lines.append("")
        lines.append("[CONTENT]")
        lines.append(self._content)
        
        # Crear el texto completo
        prompt_text = "\n".join(lines)
        
        # Devolver un PromptObject
        return PromptObject(
            metadata=self._metadata.copy(),
            defaults=self._defaults.copy(),
            content=self._content,
            text=prompt_text
        )
    
    def save(self, filepath: str) -> str:
        """
        Construye el prompt y lo guarda en un archivo.
        
        Args:
            filepath (str): Ruta donde guardar el archivo.
        
        Returns:
            str: Ruta absoluta al archivo guardado.
        """
        prompt_obj = self.build()
        return prompt_obj.save(filepath)

def create_prompt_text(content: str, 
                     defaults: Optional[Dict[str, str]] = None, 
                     metadata: Optional[Dict[str, str]] = None) -> PromptObject:
    """
    Crea un objeto PromptObject que representa un archivo .prompt.
    
    Args:
        content (str): Contenido del prompt.
        defaults (Dict[str, str], optional): Valores por defecto para las variables.
        metadata (Dict[str, str], optional): Campos de metadata adicionales.
        
    Returns:
        PromptObject: Un objeto con acceso estructurado al prompt.
        
    """
    builder = PromptBuilder().content(content)
    
    if defaults:
        builder.set_defaults(defaults)
    
    if metadata:
        builder.set_metadata(metadata)
    
    return builder.build()

def create_prompt_file(content: str, 
                      filepath: str,
                      defaults: Optional[Dict[str, str]] = None, 
                      metadata: Optional[Dict[str, str]] = None) -> str:
    """
    Crea un archivo .prompt y lo guarda en la ruta especificada.
    
    Args:
        content (str): Contenido del prompt.
        filepath (str): Ruta donde guardar el archivo.
        defaults (Dict[str, str], optional): Valores por defecto para las variables.
        metadata (Dict[str, str], optional): Campos de metadata adicionales.
        
    Returns:
        str: Ruta absoluta al archivo guardado.
        
    """
    prompt = create_prompt_text(content, defaults, metadata)
    return prompt.save(filepath)

def detect_variables(content: str) -> set:
    """
    Detecta las variables en el contenido de un prompt.
    
    Args:
        content (str): Texto del contenido que puede contener variables como {variable}.
        
    Returns:
        set: Conjunto con los nombres de las variables detectadas.
    """
    # Patrón para detectar variables como {variable}
    variable_pattern = re.compile(r'\{(\w+)\}')
    
    # Encontrar todas las coincidencias
    matches = variable_pattern.findall(content)
    
    # Devolver conjunto de nombres de variables únicos
    return set(matches)