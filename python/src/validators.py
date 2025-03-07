import os
import re
from typing import Dict, List, Tuple, Optional, Set, Any
from collections import defaultdict

class PromptValidator:
    """
    Validador completo para archivos .prompt que verifica el cumplimiento 
    de las especificaciones.
    """
    
    def __init__(self, text: str = None, filepath: str = None):
        """
        Inicializa el validador con el contenido de un archivo .prompt.
        
        Args:
            text (str, optional): Contenido del archivo .prompt.
            filepath (str, optional): Ruta al archivo .prompt.
            
        Raises:
            ValueError: Si no se proporciona ni text ni filepath.
        """
        if text is None and filepath is None:
            raise ValueError("Debe proporcionar el contenido del prompt o la ruta a un archivo")
            
        if filepath:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.text = f.read()
            self.filepath = filepath
        else:
            self.text = text
            self.filepath = None
            
        self.lines = self.text.splitlines()
        self.result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
            
    def validate(self) -> Dict[str, Any]:
        """
        Valida el archivo .prompt y devuelve el resultado.
        
        Returns:
            Dict[str, Any]: Diccionario con los campos 'valid', 'errors' y 'warnings'.
        """
        # Reset result
        self.result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Realizar todas las validaciones
        self._validate_sections_presence()
        self._validate_sections_order()
        self._validate_metadata()
        self._validate_defaults()
        self._validate_content()
        self._validate_variables()
        
        return self.result
        
    def _validate_sections_presence(self):
        """Valida que estén presentes las secciones requeridas."""
        section_pattern = re.compile(r'\[\s*(METADATA|DEFAULTS|CONTENT)\s*\]', re.IGNORECASE)
        
        found_sections = []
        for line in self.lines:
            match = section_pattern.match(line.strip())
            if match:
                found_sections.append(match.group(1).upper())
        
        if 'METADATA' not in found_sections:
            self.result["valid"] = False
            self.result["errors"].append("Falta la sección obligatoria [METADATA]")
            
        if 'CONTENT' not in found_sections:
            self.result["valid"] = False
            self.result["errors"].append("Falta la sección obligatoria [CONTENT]")
        
    def _validate_sections_order(self):
        """Valida que las secciones estén en el orden correcto."""
        section_pattern = re.compile(r'\[\s*(METADATA|DEFAULTS|CONTENT)\s*\]', re.IGNORECASE)
        
        section_positions = {}
        for i, line in enumerate(self.lines):
            match = section_pattern.match(line.strip())
            if match:
                section_positions[match.group(1).upper()] = i
        
        # Verificar orden: METADATA -> DEFAULTS -> CONTENT
        if 'METADATA' in section_positions and 'CONTENT' in section_positions:
            if section_positions['METADATA'] > section_positions['CONTENT']:
                self.result["valid"] = False
                self.result["errors"].append("Orden incorrecto: [METADATA] debe aparecer antes que [CONTENT]")
        
        if 'DEFAULTS' in section_positions:
            if 'METADATA' in section_positions and section_positions['DEFAULTS'] < section_positions['METADATA']:
                self.result["valid"] = False
                self.result["errors"].append("Orden incorrecto: [DEFAULTS] debe aparecer después de [METADATA]")
                
            if 'CONTENT' in section_positions and section_positions['DEFAULTS'] > section_positions['CONTENT']:
                self.result["valid"] = False
                self.result["errors"].append("Orden incorrecto: [DEFAULTS] debe aparecer antes que [CONTENT]")
    
    def _validate_metadata(self):
        """Valida la sección METADATA y sus campos."""
        metadata_section = self._extract_section('METADATA')
        if not metadata_section:
            return  # Ya se reportó el error en _validate_sections_presence
        
        # Verificar format_version obligatorio
        format_version_found = False
        
        field_pattern = re.compile(r'^@(\w[\w\-_]{0,63})\s+(.+)$')
        multiline_pattern = re.compile(r'^@(\w[\w\-_]{0,63})\s+>$')
        
        current_field = None
        
        for line in metadata_section:
            line = line.strip()
            
            # Saltar líneas vacías y comentarios
            if not line or self._is_comment_line(line):
                continue
                
            # Verificar si es un campo normal
            match = field_pattern.match(line)
            if match:
                field_name = match.group(1)
                if field_name == 'format_version':
                    format_version_found = True
                current_field = None
                continue
                
            # Verificar si es un campo multilínea
            match = multiline_pattern.match(line)
            if match:
                field_name = match.group(1)
                if field_name == 'format_version':
                    format_version_found = True
                current_field = field_name
                continue
                
            # Si no es campo y no estamos en un campo multilínea, es un error
            if not current_field and line.strip() and not self._is_comment_line(line):
                self.result["warnings"].append(f"Línea inválida en [METADATA]: '{line}'")
        
        if not format_version_found:
            self.result["valid"] = False
            self.result["errors"].append("Falta el campo obligatorio @format_version en [METADATA]")
    
    def _validate_defaults(self):
        """Valida la sección DEFAULTS y sus campos."""
        defaults_section = self._extract_section('DEFAULTS')
        if not defaults_section:
            return  # No es obligatorio, así que no es un error
            
        field_pattern = re.compile(r'^@(\w[\w\-_]{0,63})\s+(.+)$')
        multiline_pattern = re.compile(r'^@(\w[\w\-_]{0,63})\s+>$')
        
        current_field = None
        
        for line in defaults_section:
            line = line.strip()
            
            # Saltar líneas vacías y comentarios
            if not line or self._is_comment_line(line):
                continue
                
            # Verificar si es un campo normal
            match = field_pattern.match(line)
            if match:
                current_field = None
                continue
                
            # Verificar si es un campo multilínea
            match = multiline_pattern.match(line)
            if match:
                current_field = match.group(1)
                continue
                
            # Si no es campo y no estamos en un campo multilínea, es un error
            if not current_field and line.strip() and not self._is_comment_line(line):
                self.result["warnings"].append(f"Línea inválida en [DEFAULTS]: '{line}'")
    
    def _validate_content(self):
        """Valida la sección CONTENT."""
        content_section = self._extract_section('CONTENT')
        if not content_section:
            return  # Ya se reportó el error en _validate_sections_presence
            
        if not ''.join(content_section).strip():
            self.result["valid"] = False
            self.result["errors"].append("La sección [CONTENT] está vacía")
            
        # Verificar comentarios inline correctos
        inline_comment_pattern = re.compile(r'\(%.*?%\)')
        unbalanced_pattern = re.compile(r'\(%[^%]*$|^[^(]*%\)')
        
        content_text = '\n'.join(content_section)
        
        # Eliminar comentarios correctos para buscar desbalanceados
        clean_content = inline_comment_pattern.sub('', content_text)
        
        if unbalanced_pattern.search(clean_content):
            self.result["warnings"].append("Posible comentario inline desbalanceado en [CONTENT]")
    
    def _validate_variables(self):
        """Valida las variables y sus referencias."""
        content_section = self._extract_section('CONTENT')
        defaults_section = self._extract_section('DEFAULTS')
        
        if not content_section:
            return  # Ya se reportó el error
            
        # Extraer variables del contenido
        content_text = '\n'.join(content_section)
        processed = re.sub(r'\(%.*?%\)', '', content_text)  # Eliminar comentarios
        variables = set(re.findall(r'\{(\w+)\}', processed))
        
        # Si no hay sección DEFAULTS, todas las variables quedarán sin valor
        if not defaults_section:
            if variables:
                self.result["warnings"].append(
                    f"No hay sección [DEFAULTS] pero se encontraron variables: {', '.join(sorted(variables))}"
                )
            return
            
        # Extraer variables definidas en DEFAULTS
        defined_vars = set()
        field_pattern = re.compile(r'^@(\w[\w\-_]{0,63})\s+(.+)$')
        multiline_pattern = re.compile(r'^@(\w[\w\-_]{0,63})\s+>$')
        
        for line in defaults_section:
            line = line.strip()
            
            # Saltar líneas vacías y comentarios
            if not line or self._is_comment_line(line):
                continue
                
            # Verificar si es un campo normal
            match = field_pattern.match(line)
            if match:
                defined_vars.add(match.group(1))
                continue
                
            # Verificar si es un campo multilínea
            match = multiline_pattern.match(line)
            if match:
                defined_vars.add(match.group(1))
                continue
        
        # Variables sin valor por defecto
        undefined_vars = variables - defined_vars
        if undefined_vars:
            self.result["warnings"].append(
                f"Variables sin valor por defecto: {', '.join(sorted(undefined_vars))}"
            )
        
        # Variables definidas pero no utilizadas
        unused_vars = defined_vars - variables
        if unused_vars:
            self.result["warnings"].append(
                f"Variables definidas pero no utilizadas en [CONTENT]: {', '.join(sorted(unused_vars))}"
            )
    
    def _is_comment_line(self, line: str) -> bool:
        """
        Determina si una línea es un comentario completo (% %).
        
        Args:
            line (str): Línea a evaluar
            
        Returns:
            bool: True si la línea es un comentario, False en caso contrario
        """
        # Verifica si la línea comienza con (% y termina con %)
        return line.strip().startswith('(%') and line.strip().endswith('%)')

    def _extract_section(self, section_name: str) -> List[str]:
        """
        Extrae las líneas de una sección específica.
        
        Args:
            section_name (str): Nombre de la sección (METADATA, DEFAULTS, CONTENT)
            
        Returns:
            List[str]: Lista de líneas de la sección o lista vacía si no se encuentra
        """
        section_pattern = re.compile(r'\[\s*(METADATA|DEFAULTS|CONTENT)\s*\]', re.IGNORECASE)
        
        # Encontrar todas las secciones
        section_positions = {}
        for i, line in enumerate(self.lines):
            match = section_pattern.match(line.strip())
            if match:
                section_positions[match.group(1).upper()] = i
        
        # Si no existe la sección, retornar lista vacía
        if section_name.upper() not in section_positions:
            return []
            
        start_line = section_positions[section_name.upper()] + 1
        end_line = len(self.lines)
        
        # Encontrar dónde termina la sección (en la siguiente sección)
        for section, pos in section_positions.items():
            if pos > start_line and pos < end_line:
                end_line = pos
        
        return self.lines[start_line:end_line]

def file_validator(filepath: str) -> Dict[str, Any]:
    """
    Valida un archivo .prompt y devuelve el resultado detallado.
    
    Args:
        filepath (str): Ruta al archivo .prompt
        
    Returns:
        Dict[str, Any]: Diccionario con los campos 'valid', 'errors' y 'warnings'
    """
    validator = PromptValidator(filepath=filepath)
    return validator.validate()

def text_validator(text: str) -> Dict[str, Any]:
    """
    Valida el contenido de un archivo .prompt y devuelve el resultado detallado.
    
    Args:
        text (str): Contenido del archivo .prompt
        
    Returns:
        Dict[str, Any]: Diccionario con los campos 'valid', 'errors' y 'warnings'
    """
    validator = PromptValidator(text=text)
    return validator.validate()

def print_validation_result(result: Dict[str, Any], filepath: str = None):
    """
    Imprime el resultado de la validación de manera legible.
    
    Args:
        result (Dict[str, Any]): Resultado de la validación
        filepath (str, optional): Ruta al archivo validado
    """
    file_info = f" '{filepath}'" if filepath else ""
    
    if result["valid"]:
        print(f"✅ El archivo{file_info} es válido según la especificación.")
        
        if result["warnings"]:
            print("\n⚠️ Advertencias:")
            for warning in result["warnings"]:
                print(f"  - {warning}")
    else:
        print(f"❌ El archivo{file_info} tiene los siguientes errores:")
        for error in result["errors"]:
            print(f"  - {error}")
        
        if result["warnings"]:
            print("\n⚠️ Advertencias:")
            for warning in result["warnings"]:
                print(f"  - {warning}")