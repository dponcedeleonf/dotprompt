# models.py
import os
import json
from typing import Dict, Any

class PromptObject:
    def __init__(self, metadata: dict, defaults: dict, content: str):
        self.metadata = metadata
        self.defaults = defaults
        self.content = content
    
    @property
    def text(self) -> str:
        """Devuelve el texto completo en formato .prompt."""
        parts = ["[METADATA]"]
        parts.append(self._serialize_section(self.metadata))
        if self.defaults:
            parts.append("\n[DEFAULTS]")
            parts.append(self._serialize_section(self.defaults))
        parts.append("\n[CONTENT]")
        parts.append(self.content)
        return "\n".join(parts)
    
    def metadata_text(self) -> str:
        """Devuelve solo la sección [METADATA] como texto."""
        return "[METADATA]\n" + self._serialize_section(self.metadata)
    
    def defaults_text(self) -> str:
        """Devuelve solo la sección [DEFAULTS] como texto, o '' si no hay defaults."""
        return "[DEFAULTS]\n" + self._serialize_section(self.defaults) if self.defaults else ""
    
    def content_text(self) -> str:
        """Devuelve solo la sección [CONTENT] como texto."""
        return "[CONTENT]\n" + self.content
    
    def _serialize_section(self, section: Dict[str, Any]) -> str:
        lines = []
        for key, value in section.items():
            if "\n" in str(value):
                lines.append(f"@{key} >")
                for line in str(value).split("\n"):
                    lines.append(f"  {line}")
            else:
                lines.append(f"@{key} {value}")
        return "\n".join(lines)
    
    def get_variables_info(self) -> Dict[str, Dict[str, Any]]:
        """Devuelve información sobre las variables en el contenido."""
        import re
        processed = re.sub(r'\(%[^%]*?%\)', '', self.content, flags=re.DOTALL)
        processed = re.sub(r'{{(.*?)}}', r'{\1}', processed)
        variables = set(re.findall(r'\{(\w+)\}', processed))
        result = {}
        for var in variables:
            has_default = var in self.defaults
            default_value = self.defaults.get(var, None)
            result[var] = {
                "has_default": has_default,
                "default_value": default_value
            }
        return result
    
    def process(self, **kwargs: Any) -> str:
        """Procesa el contenido sustituyendo variables."""
        import re
        import warnings
        processed = re.sub(r'\(%[^%]*?%\)', '', self.content, flags=re.DOTALL)
        processed = re.sub(r'{{(.*?)}}', r'{\1}', processed)
        variables = set(re.findall(r'\{(\w+)\}', processed))
        
        extra_kwargs = set(kwargs.keys()) - variables
        if extra_kwargs:
            raise ValueError(f"Los siguientes kwargs no corresponden a variables: {', '.join(sorted(extra_kwargs))}")
        
        values = {}
        for key in variables:
            values[key] = kwargs.get(key, self.defaults.get(key))
        
        warnings_messages = []
        used_defaults = {key for key in variables if key not in kwargs and key in self.defaults}
        if used_defaults:
            warnings_messages.append(f"Using default values for: {', '.join(sorted(used_defaults))}.")
        missing_keys = {key for key in variables if values[key] is None}
        if missing_keys:
            warnings_messages.append(f"The following variables were not provided: {', '.join(sorted(missing_keys))}.")
        if warnings_messages:
            warnings.warn("\n".join(warnings_messages), stacklevel=2)
        
        return re.sub(r'\{(\w+)\}', 
                      lambda m: str(values[m.group(1)]) if values[m.group(1)] is not None else m.group(0), 
                      processed)
    
    def to_json(self) -> str:
        """Convierte el PromptObject a JSON."""
        data = {
            "metadata": self.metadata,
            "defaults": self.defaults if self.defaults else None,
            "content": self.content
        }
        return json.dumps(data, ensure_ascii=False, indent=4)
    
    def to_text(self) -> str:
        """Alias para .text."""
        return self.text
    
    @classmethod
    def from_json(cls, json_str: str) -> 'PromptObject':
        """Crea un PromptObject desde JSON."""
        data = json.loads(json_str)
        if not isinstance(data, dict) or "metadata" not in data or "content" not in data:
            raise ValueError("JSON inválido: debe contener 'metadata' y 'content'")
        if "format_version" not in data["metadata"]:
            raise ValueError("El campo 'format_version' es obligatorio en metadata")
        return cls(
            metadata=data["metadata"],
            defaults=data.get("defaults") or {},
            content=data["content"]
        )

    def save(self, filepath: str) -> str:
        """
        Guarda el objeto en un archivo .prompt.
        
        Args:
            filepath (str): Ruta donde guardar el archivo.
        
        Returns:
            str: Ruta absoluta del archivo guardado.
        """
        import os
        
        # Asegurar que la ruta sea absoluta
        absolute_path = os.path.abspath(filepath)
        
        # Crear el directorio si no existe
        directory = os.path.dirname(absolute_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        # Escribir el contenido del prompt al archivo
        with open(absolute_path, 'w', encoding='utf-8') as f:
            f.write(self.text)
        
        return absolute_path

    def add_metadata(self, key: str, value: str) -> 'PromptObject':
        """
        Agrega o actualiza un metadato.
        
        Args:
            key: Clave del metadato
            value: Valor a asignar
            
        Returns:
            PromptObject: La instancia actual para encadenamiento
        """
        self.metadata[key] = value
        return self

    def remove_metadata(self, key: str) -> 'PromptObject':
        """
        Elimina un metadato si existe.
        
        Args:
            key: Clave del metadato a eliminar
            
        Returns:
            PromptObject: La instancia actual para encadenamiento
        """
        if key in self.metadata:
            del self.metadata[key]
        return self

    def add_default(self, key: str, value: str) -> 'PromptObject':
        """
        Agrega o actualiza un valor por defecto.
        
        Args:
            key: Clave del valor por defecto
            value: Valor a asignar
            
        Returns:
            PromptObject: La instancia actual para encadenamiento
        """
        self.defaults[key] = value
        return self

    def remove_default(self, key: str) -> 'PromptObject':
        """
        Elimina un valor por defecto si existe.
        
        Args:
            key: Clave del valor por defecto a eliminar
            
        Returns:
            PromptObject: La instancia actual para encadenamiento
        """
        if key in self.defaults:
            del self.defaults[key]
        return self

    def update_metadata(self, metadata_dict: dict) -> 'PromptObject':
        """
        Actualiza múltiples metadatos a la vez.
        
        Args:
            metadata_dict: Diccionario con metadatos a agregar o actualizar
            
        Returns:
            PromptObject: La instancia actual para encadenamiento
        """
        self.metadata.update(metadata_dict)
        return self

    def update_defaults(self, defaults_dict: dict) -> 'PromptObject':
        """
        Actualiza múltiples valores por defecto a la vez.
        
        Args:
            defaults_dict: Diccionario con valores por defecto a agregar o actualizar
            
        Returns:
            PromptObject: La instancia actual para encadenamiento
        """
        self.defaults.update(defaults_dict)
        return self

    def remove_metadata_keys(self, keys: list) -> 'PromptObject':
        """
        Elimina múltiples metadatos si existen.
        
        Args:
            keys: Lista de claves de metadatos a eliminar
            
        Returns:
            PromptObject: La instancia actual para encadenamiento
        """
        for key in keys:
            if key in self.metadata:
                del self.metadata[key]
        return self

    def remove_default_keys(self, keys: list) -> 'PromptObject':
        """
        Elimina múltiples valores por defecto si existen.
        
        Args:
            keys: Lista de claves de valores por defecto a eliminar
            
        Returns:
            PromptObject: La instancia actual para encadenamiento
        """
        for key in keys:
            if key in self.defaults:
                del self.defaults[key]
        return self

    def update_content(self, new_content: str) -> 'PromptObject':
        """
        Actualiza el contenido del prompt.
        
        Args:
            new_content: Nuevo contenido
            
        Returns:
            PromptObject: La instancia actual para encadenamiento
        """
        self.content = new_content.strip()
        return self

    def to_builder(self) -> 'PromptBuilder': # type: ignore
        """
        Convierte este PromptObject en un nuevo PromptBuilder para modificaciones extensas.
        
        Returns:
            PromptBuilder: Un nuevo builder inicializado con los datos actuales
        """
        from .creator import PromptBuilder
        builder = PromptBuilder()
        builder.metadata(self.metadata)
        builder.defaults(self.defaults)
        builder.content(self.content)
        return builder