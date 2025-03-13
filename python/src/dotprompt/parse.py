# parse.py
import os
from typing import Dict
from .models import PromptObject

class PromptParser:
    """Parsea texto en formato .prompt y devuelve un PromptObject."""
    
    def __init__(self, text: str):
        import re
        if not text.strip():
            raise ValueError("El texto del prompt no puede estar vacío")
        
        sections = {"metadata": {}, "defaults": {}, "content": []}
        current_section = None
        current_key = None
        section_header = re.compile(r'\[\s*(METADATA|DEFAULTS|CONTENT)\s*\]', re.IGNORECASE)
        comment_pattern = re.compile(r'\(%[^%]*?%\)$')
        
        section_positions = {}
        for i, raw_line in enumerate(text.splitlines()):
            line = raw_line.strip()
            if not line or line.startswith('#'):
                continue
            header_match = section_header.fullmatch(line)
            if header_match:
                section_positions[header_match.group(1).lower()] = i
        
        if 'content' in section_positions and 'defaults' in section_positions:
            if section_positions['defaults'] > section_positions['content']:
                raise ValueError("Incorrect section order: [DEFAULTS] must appear before [CONTENT]")
        
        for i, raw_line in enumerate(text.splitlines()):
            line = raw_line.strip()
            if not line or (line.startswith('(%') and line.endswith('%)')):
                continue
            header_match = section_header.fullmatch(line)
            if header_match:
                current_section = header_match.group(1).lower()
                current_key = None
                continue
            if current_section in ("metadata", "defaults"):
                if line.startswith('@'):
                    if '>' in line:
                        key = line.split('>', 1)[0][1:].strip()
                        current_key = key
                        sections[current_section][key] = ""
                    else:
                        parts = line[1:].split(' ', 1)
                        key = parts[0].strip()
                        value = parts[1].strip() if len(parts) > 1 else ""
                        if current_section == "metadata" and not value:
                            raise ValueError(f"Linea {i+1}: Metadata '@{key}' no puede tener valor vacío")
                        sections[current_section][key] = value
                elif current_key:
                    sections[current_section][current_key] += "\n" + line
            elif current_section == "content":
                line = comment_pattern.sub('', line).strip()
                if line:
                    sections["content"].append(line)
        
        if not sections["content"]:
            raise ValueError("Falta o está vacía la sección [CONTENT]")
        if 'format_version' not in sections["metadata"]:
            raise ValueError("Falta @format_version en [METADATA]")
        
        self.obj = PromptObject(
            metadata=sections["metadata"],
            defaults=sections["defaults"],
            content="\n".join(sections["content"])
        )

    @classmethod
    def from_file(cls, filepath: str) -> PromptObject:
        """Lee un archivo .prompt y devuelve un PromptObject."""
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"El archivo '{filepath}' no existe")
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        return cls(text).obj

def from_file(filepath: str) -> PromptObject:
    """Función de alto nivel para parsear un archivo .prompt."""
    return PromptParser.from_file(filepath)