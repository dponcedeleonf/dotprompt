import dotprompt

# 1. Usando diccionarios
prompt1 = dotprompt.create(
    metadata={
        "format_version": "0.0.1",
        "name": "Ejemplo 1"
    },
    defaults={
        "nombre": "Usuario",
        "saludo": "Hola"
    },
    content="{saludo}, {nombre}! Bienvenido a dotprompt."
)

print("=== Prompt 1 (diccionarios) ===")
print(prompt1.text)
print()

# 2. Usando tuplas para pares clave-valor individuales
prompt2 = dotprompt.create(
    metadata=("name", "Ejemplo 2"),
    metadata=("format_version","0.0.1"), 
    defaults=("nombre", "Cliente"),
    defaults=("saludo", "Hola"),
    content="{saludo}, {nombre}! Gracias por usar dotprompt."
)

print("=== Prompt 2 (tuplas y prefijos) ===")
print(prompt2)
print()

# 3. Usando solo argumentos con prefijos
prompt3 = dotprompt.create(
    meta_format_version="0.0.1",
    meta_name="Ejemplo 3",
    meta_author="Equipo IA",
    default_rol="asistente",
    default_nivel="experto",
    default_tono="profesional",
    content="Actúa como un {rol} de nivel {nivel} y usa un tono {tono}."
)

print("=== Prompt 3 (solo prefijos) ===")
print(prompt3.text)
print()

# 4. Mezclando estilos (un poco de todo)
prompt4 = dotprompt.create(
    metadata={
        "format_version": "0.0.1",
        "type": "instruction"
    },
    meta_name="Ejemplo Mixto",  # Esto se añadirá al diccionario metadata
    defaults=("modelo", "gpt-4"),  # Un par defaults
    default_temperatura="0.7",    # Otro defaults con prefijo
    default_tokens="2048",        # Otro más
    content="Genera una respuesta usando {modelo} con temperatura {temperatura} y máximo {tokens} tokens."
)

print("=== Prompt 4 (estilos mixtos) ===")
print(prompt4.text)