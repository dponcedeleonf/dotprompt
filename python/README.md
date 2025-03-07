# DotPrompt

A Python library for working with `.prompt` template files, allowing you to create, validate, and use prompt templates with variables.

## Installation

```bash
pip install dotprompt
```

## Basic Usage

```python
import dotprompt

# Load and use a prompt template
prompt = dotprompt.content("path/to/file.prompt", var1="value1", var2="value2")
print(prompt)

# Get metadata, defaults and variables
meta = dotprompt.metadata("path/to/file.prompt")
defs = dotprompt.defaults("path/to/file.prompt")
vars_info = dotprompt.variables("path/to/file.prompt")

# Validate a prompt
validation = dotprompt.validate("path/to/file.prompt")
if validation["valid"]:
    print("Prompt is valid!")
else:
    print("Errors:", validation["errors"])
```

## Working with Prompt Text

All functions accept either a file path or direct prompt text as a string. This allows you to work with prompts stored in variables, just like you would with JSON:

```python
# Using prompt text directly (without a file)
prompt_text = """[METADATA]
@format_version 1.0

[DEFAULTS]
@var1 default1
@var2 default2

[CONTENT]
This is a prompt with {var1} and {var2}."""

# Process the prompt text with variables
result = dotprompt.content(prompt_text, var1="custom1", var2="custom2")
print(result)

# Get metadata from text
meta = dotprompt.metadata(prompt_text)

# Validate prompt text
validation = dotprompt.validate(prompt_text)
```

This flexibility enables you to:

- Generate prompts dynamically at runtime
- Store prompts in databases instead of files
- Send prompts through APIs
- Manipulate prompts in memory before saving them

## Creating .prompt Files

You can programmatically create `.prompt` files with a fluent API:

```python
from dotprompt import PromptBuilder

builder = PromptBuilder()\
    .set_name("My Prompt")\
    .set_author("Author Name")\
    .set_description("A description of the prompt")\
    .set_defaults({
        "var1": "default1",
        "var2": "default2"
    })\
    .content("This is a prompt with {var1} and {var2}.")\
    .save("my_prompt.prompt")
```

Or more directly:

```python
from dotprompt import create_prompt_file

create_prompt_file(
    content="This is a prompt with {var1} and {var2}.",
    defaults={"var1": "default1", "var2": "default2"},
    metadata={"name": "My Prompt", "author": "Author Name"},
    filepath="my_prompt.prompt"
)
```

## .prompt File Format

The `.prompt` files follow this structure:

``` prompt
[METADATA]
@format_version 1.0
@name Prompt Name
@author Author Name
@description Description of the prompt

[DEFAULTS]
@var1 default1
@var2 default2

[CONTENT]
This is the content of the prompt with variables {var1} and {var2}.
```

## Advanced Validation

For comprehensive prompt validation:

```python
from dotprompt import file_validator, print_validation_result

result = file_validator("path/to/file.prompt")
print_validation_result(result)

# Or validate prompt text
from dotprompt import text_validator
result = text_validator(prompt_text)
print_validation_result(result)
```

## API Reference

### Core Functions

- `content(prompt, **kwargs)`: Load and process a prompt with variables
- `defaults(prompt)`: Get default values from a prompt
- `metadata(prompt)`: Get metadata from a prompt
- `variables(prompt)`: Get information about variables in a prompt
- `validate(prompt)`: Basic validation of a prompt

Where `prompt` can be either a file path or a string containing prompt text.

### Creator Functions

- `PromptBuilder()`: Fluent API for building prompts
- `create_prompt_text(content, defaults, metadata)`: Create a prompt object
- `create_prompt_file(content, filepath, defaults, metadata)`: Create and save a prompt file
- `detect_variables(content)`: Find variables in a content string

### Validator Functions

- `file_validator(filepath)`: Validate a prompt file
- `text_validator(text)`: Validate prompt text
- `print_validation_result(result)`: Print validation results

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
