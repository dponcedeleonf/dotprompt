#core.py
import os
import re
import warnings
from typing import Tuple, Dict, Any, List, Set

class PromptParser:
    def __init__(self, text: str):
        self.metadata, self.defaults, self.content = self._parse(text)
        # Procesar el contenido para obtener placeholders
        processed = re.sub(r'\(%.*?%\)', '', self.content)
        processed = re.sub(r'{{(.*?)}}', r'{\1}', processed)
        self.variables = set(re.findall(r'\{(\w+)\}', processed))
        
    def _parse(self, text: str) -> Tuple[Dict[str, str], Dict[str, str], str]:
        sections = {"metadata": {}, "defaults": {}, "content": []}
        current_section = None
        current_key = None

        # Se permite espacios en blanco dentro de los corchetes
        section_header = re.compile(r'\[\s*(METADATA|DEFAULTS|CONTENT)\s*\]', re.IGNORECASE)

        # Primero detectamos las posiciones de las secciones para validar el orden
        section_positions = {}
        for i, raw_line in enumerate(text.splitlines()):
            line = raw_line.strip()
            if not line or line.startswith('#'):
                continue
                
            header_match = section_header.fullmatch(line)
            if header_match:
                section_type = header_match.group(1).lower()
                section_positions[section_type] = i

        # Validar el orden de las secciones si existen
        if 'content' in section_positions and 'defaults' in section_positions:
            if section_positions['defaults'] > section_positions['content']:
                raise ValueError("Orden de secciones incorrecto: [DEFAULTS] debe aparecer antes que [CONTENT]")

        # Ahora procesamos el contenido de las secciones
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line or (line.strip().startswith('(%') and line.strip().endswith('%)')):
                continue  # Ignorar líneas completas encerradas en (% ... %)

            # Verificamos si es un encabezado de sección
            header_match = section_header.fullmatch(line)
            if header_match:
                current_section = header_match.group(1).lower()
                current_key = None
                continue

            if current_section in ("metadata", "defaults"):
                if line.startswith('@'):
                    # Se maneja la posibilidad de valores multilínea
                    if '>' in line:
                        key = line.split('>', 1)[0][1:].strip()
                        current_key = key
                        sections[current_section][key] = ""
                    else:
                        try:
                            key, value = line[1:].split(' ', 1)
                        except ValueError:
                            raise ValueError(f"Error al parsear la línea: {line}")
                        sections[current_section][key.strip()] = value.strip()
                elif current_key:
                    sections[current_section][current_key] += "\n" + line
            elif current_section == "content":
                sections["content"].append(line)

        # Validaciones finales
        if not sections["content"]:
            if 'content' in section_positions:
                raise ValueError("La sección [CONTENT] está vacía")
            else:
                raise ValueError("Falta la sección [CONTENT]")
                
        if 'format_version' not in sections["metadata"]:
            raise ValueError("Falta @format_version en [METADATA]")

        return sections["metadata"], sections["defaults"], "\n".join(sections["content"])
        
    def get_variables_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Devuelve información detallada sobre las variables en el contenido.
        
        Returns:
            Dict[str, Dict[str, Any]]: Diccionario con información de cada variable:
                - has_default: Si tiene valor por defecto
                - default_value: El valor por defecto (si existe)
        """
        result = {}
        
        for var in self.variables:
            has_default = var in self.defaults
            default_value = self.defaults.get(var, None)
            
            result[var] = {
                "has_default": has_default,
                "default_value": default_value
            }
            
        return result

    def process(self, **kwargs: Any) -> str:
        # Eliminar comentarios en el contenido
        processed = re.sub(r'\(%.*?%\)', '', self.content)
        # Ajustar sintaxis de las variables: de {{var}} a {var}
        processed = re.sub(r'{{(.*?)}}', r'{\1}', processed)

        # Extraer todos los nombres de variables (placeholders) del contenido
        placeholders = self.variables

        # Verificar que los kwargs proporcionados correspondan a alguna variable del contenido
        extra_kwargs = set(kwargs.keys()) - placeholders
        if extra_kwargs:
            raise ValueError(
                f"Los siguientes kwargs no corresponden a variables en el contenido: {', '.join(sorted(extra_kwargs))}"
            )

        # Construir el diccionario final de variables según la prioridad
        variables = {}
        for key in placeholders:
            if key in kwargs:
                variables[key] = kwargs[key]
            elif key in self.defaults:
                variables[key] = self.defaults[key]
            else:
                variables[key] = None

        # Preparar mensajes de advertencia
        warnings_messages = []
        
        # Advertencia de defaults usados
        used_defaults = {key for key in placeholders if key not in kwargs and key in self.defaults}
        if used_defaults:
            warnings_messages.append(f"Se están usando valores por defecto para: {', '.join(sorted(used_defaults))}.")
        
        # Advertencia de variables que quedarán como placeholder
        missing_keys = {key for key in placeholders if variables[key] is None}
        if missing_keys:
            warnings_messages.append(f"Las siguientes variables no fueron proporcionadas y permanecerán como placeholder: {', '.join(sorted(missing_keys))}.")
        
        # Emitir todas las advertencias juntas
        if warnings_messages:
            warnings.warn("\n".join(warnings_messages), stacklevel=2)

        # Realizar el reemplazo: si la variable tiene valor se usa, sino se mantiene el placeholder
        return re.sub(r'\{(\w+)\}', 
                    lambda m: str(variables[m.group(1)]) if variables[m.group(1)] is not None else m.group(0),
                    processed)

def _load_prompt(prompt: str) -> str:
    """Carga el prompt desde un archivo si 'prompt' es una ruta, o lo devuelve directamente si es un string."""
    if os.path.exists(prompt):
        with open(prompt, encoding='utf-8') as f:
            return f.read()
    return prompt

def content(prompt: str, **kwargs: Any) -> str:
    """
    Devuelve el contenido del prompt procesado con las variables sustituidas.
    
    Ejemplo:
      >>> resultado = content("saludo.prompt", name="Bob", adjective="awesome")
      >>> print(resultado)
    """
    text = _load_prompt(prompt)
    parser = PromptParser(text)
    return parser.process(**kwargs)

def defaults(prompt: str) -> dict:
    """
    Devuelve el diccionario de defaults del prompt.
    
    Ejemplo:
      >>> defs = defaults("saludo.prompt")
      >>> print(defs)
    """
    text = _load_prompt(prompt)
    parser = PromptParser(text)
    return parser.defaults

def metadata(prompt: str) -> dict:
    """
    Devuelve el diccionario de metadata del prompt.
    
    Ejemplo:
      >>> meta = metadata("saludo.prompt")
      >>> print(meta)
    """
    text = _load_prompt(prompt)
    parser = PromptParser(text)
    return parser.metadata

def variables(prompt: str) -> Dict[str, Dict[str, Any]]:
    """
    Devuelve información sobre las variables encontradas en el contenido del prompt.
    
    Ejemplo:
      >>> vars_info = variables("saludo.prompt")
      >>> for var, info in vars_info.items():
      >>>     print(f"{var}: tiene default: {info['has_default']}, valor: {info['default_value']}")
    
    Returns:
        Dict[str, Dict[str, Any]]: Diccionario con información de cada variable
    """
    text = _load_prompt(prompt)
    parser = PromptParser(text)
    return parser.get_variables_info()

def validate(prompt: str) -> dict:
    """
    Valida básicamente un archivo .prompt y devuelve el resultado de la validación.
    Este validador es más simple que el de validators.py. Para una validación
    más completa use file_validator o text_validator.
    
    Ejemplo:
      >>> resultado = validate("saludo.prompt")
      >>> if resultado["valid"]:
      >>>     print("El archivo es válido")
      >>> else:
      >>>     print("Errores:", resultado["errors"])
    
    Returns:
        dict: Diccionario con los campos 'valid' (bool), 'errors' (list) y 'warnings' (list)
    """
    try:
        text = _load_prompt(prompt)
        parser = PromptParser(text)
        
        # Verificar variables sin defaults
        vars_info = parser.get_variables_info()
        missing_defaults = [var for var, info in vars_info.items() if not info["has_default"]]
        
        warnings = []
        if missing_defaults:
            warnings.append(f"Las siguientes variables no tienen valores por defecto: {', '.join(sorted(missing_defaults))}")
        
        return {
            "valid": True,
            "errors": [],
            "warnings": warnings
        }
    except ValueError as e:
        return {
            "valid": False,
            "errors": [str(e)],
            "warnings": []
        }