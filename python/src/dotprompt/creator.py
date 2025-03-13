#creator.py
import datetime
from typing import Dict, Optional, Union
from .models import PromptObject

class PromptBuilder:
    """
    Constructor fluido para crear archivos .prompt de manera programática.
    
    Permite configurar metadatos, valores por defecto y contenido mediante una interfaz
    encadenable y consistente.
    """
    
    def __init__(self):
        """Inicializa el builder con valores por defecto."""
        self._metadata = {"format_version": "0.0.1"}
        self._defaults = {}
        self._content = ""
    
    def metadata(self, key: Union[str, Dict[str, str]], value: Optional[str] = None) -> 'PromptBuilder':
        """
        Agrega metadatos al prompt, ya sea un solo campo o múltiples.
        Preserva el format_version por defecto si no se especifica otro.
        
        Args:
            key: Una clave (str) o un diccionario de metadatos (Dict[str, str]).
            value: El valor asociado a la clave si key es str (opcional).
        
        Returns:
            PromptBuilder: La instancia actual para encadenamiento.
        
        Raises:
            ValueError: Si se pasa un solo campo pero no se proporciona valor.
        """
        if isinstance(key, dict):
            # Si se pasa un diccionario, actualizar los metadatos
            format_version = self._metadata.get("format_version", "0.0.1")
            self._metadata.update(key)
            self._metadata["format_version"] = format_version
        elif isinstance(key, str):
            # Si se pasa una clave individual, requerir un valor
            if value is None:
                raise ValueError("Debe proporcionar un valor cuando se pasa una sola clave")
            self._metadata[key] = value
        else:
            raise ValueError("El argumento 'key' debe ser str o Dict[str, str]")
        return self
    
    def defaults(self, key: Union[str, Dict[str, str]], value: Optional[str] = None) -> 'PromptBuilder':
        """
        Agrega valores por defecto al prompt, ya sea un solo campo o múltiples.
        
        Args:
            key: Una clave (str) o un diccionario de valores por defecto (Dict[str, str]).
            value: El valor asociado a la clave si key es str (opcional).
        
        Returns:
            PromptBuilder: La instancia actual para encadenamiento.
        
        Raises:
            ValueError: Si se pasa un solo campo pero no se proporciona valor.
        """
        if isinstance(key, dict):
            # Si se pasa un diccionario, actualizar los valores por defecto
            self._defaults.update(key)
        elif isinstance(key, str):
            # Si se pasa una clave individual, requerir un valor
            if value is None:
                raise ValueError("Debe proporcionar un valor cuando se pasa una sola clave")
            self._defaults[key] = value
        else:
            raise ValueError("El argumento 'key' debe ser str o Dict[str, str]")
        return self
    
    def content(self, text: str) -> 'PromptBuilder':
        """
        Establece el contenido del prompt.
        
        Args:
            text (str): El contenido del prompt.
        
        Returns:
            PromptBuilder: La instancia actual para encadenamiento.
        """
        self._content = text.strip()
        return self
    
    def build(self) -> PromptObject:
        """
        Construye un PromptObject con los componentes configurados.
        
        Returns:
            PromptObject: El objeto construido.
        
        Raises:
            ValueError: Si el contenido está vacío.
        """
        if not self._content:
            raise ValueError("El contenido del prompt no puede estar vacío")
        return PromptObject(
            metadata=self._metadata.copy(),
            defaults=self._defaults.copy(),
            content=self._content
        )
    
    def save(self, filepath: str) -> str:
        """
        Guarda el prompt en un archivo y devuelve la ruta absoluta.
        
        Args:
            filepath (str): Ruta donde guardar el archivo.
        
        Returns:
            str: Ruta absoluta del archivo guardado.
        """
        prompt_obj = self.build()
        return prompt_obj.save(filepath)

# Añadir al final del archivo creator.py, después de la clase PromptBuilder

def create(metadata=None, defaults=None, content=None, **kwargs):
    """
    Crea un PromptObject desde cero con una sintaxis clara y flexible.
    
    Permite dos formas principales de especificar metadatos y valores por defecto:
    1. Usando diccionarios (forma tradicional)
    2. Usando argumentos con prefijos 'meta_' y 'default_'
    
    Args:
        metadata: Diccionario con los metadatos
        defaults: Diccionario con los valores por defecto
        content: El contenido del prompt
        **kwargs: Argumentos adicionales con prefijos 'meta_' o 'default_'
        
    Returns:
        PromptObject: El objeto construido
        
    Examples:
        # Forma tradicional con diccionarios
        prompt1 = create(
            metadata={"name": "Ejemplo", "format_version": "0.0.1"},
            defaults={"variable": "valor"},
            content="Texto con {variable}"
        )
        
        # Forma con prefijos
        prompt2 = create(
            meta_name="Ejemplo",
            meta_format_version="0.0.1",
            default_variable="valor",
            content="Texto con {variable}"
        )
    """
    builder = PromptBuilder()
    
    # Procesar metadatos (forma diccionario)
    if metadata is not None:
        if not isinstance(metadata, dict):
            raise ValueError("El argumento 'metadata' debe ser un diccionario")
        builder.metadata(metadata)
    
    # Procesar defaults (forma diccionario)
    if defaults is not None:
        if not isinstance(defaults, dict):
            raise ValueError("El argumento 'defaults' debe ser un diccionario")
        builder.defaults(defaults)
    
    # Procesar content
    if content is not None:
        builder.content(content)
    
    # Procesar kwargs adicionales con prefijos
    meta_dict = {}
    default_dict = {}
    
    for key, value in kwargs.items():
        if key.startswith("meta_"):
            meta_dict[key[5:]] = value  # Eliminar el prefijo 'meta_'
        elif key.startswith("default_"):
            default_dict[key[8:]] = value  # Eliminar el prefijo 'default_'
    
    # Agregar los metadatos y defaults de kwargs si existen
    if meta_dict:
        builder.metadata(meta_dict)
    
    if default_dict:
        builder.defaults(default_dict)
    
    return builder.build()

# Ejemplo de uso
if __name__ == "__main__":
    # Ejemplo 1: Usando campos individuales
    builder1 = PromptBuilder()
    prompt1 = (
        builder1
        .metadata("name", "Saludo Simple")
        .metadata("author", "Juan Pérez")
        .defaults("nombre", "Usuario")
        .content("Hola, {nombre}! ¿Cómo estás?")
        .build()
    )
    print("Ejemplo 1:")
    print(prompt1.text)

    # Ejemplo 2: Usando diccionarios
    builder2 = PromptBuilder()
    prompt2 = (
        builder2
        .metadata({
            "name": "Saludo Completo",
            "author": "Ana López",
            "created": datetime.datetime.now().strftime("%Y-%m-%d")
        })
        .defaults({"nombre": "Amigo", "saludo": "Hola"})
        .content("{saludo}, {nombre}! Bienvenido.")
        .build()
    )
    print("\nEjemplo 2:")
    print(prompt2.text)