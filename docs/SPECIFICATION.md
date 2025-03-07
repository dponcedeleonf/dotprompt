# Specification for `.prompt` Files

**Version**: 0.0.1
**Date**: February 24, 2025  
**Repository**: [dotprompt](https://github.com/dponcedeleonf/dotprompt)

This document defines the specification for files with the `.prompt` extension, designed to store reusable instructions for AI models. The format is simple, text-based, and supports metadata, variables, and comments.

## General Structure

A `.prompt` file consists of two mandatory sections and one optional section:

1. `[METADATA]`: Structured information about the file (mandatory).
2. `[DEFAULTS]`: Default values for variables (optional).
3. `[CONTENT]`: The main instructions or text for the AI model (mandatory).

Sections are identified by square brackets (`[]`) and must appear in this order if present. Each section contains text lines with specific rules.

### General Rules

- **Encoding**: UTF-8.
- **Empty Lines**: Ignored by processors.
- **Comments**: Text enclosed in (% ... %) is ignored, whether it appears at the start of a line (commenting the entire line) or within a line (inline comments), and is removed during processing.

## `[METADATA]` Section

Contains metadata in the `@key value` format.  

- **Location**: Must be the first section in the file.
- **Format**: Each valid line starts with `@`, followed by a key, a single space, and a value. Example: `@name Greeting`.
- **Rules**:
  - Keys must be unique within `[METADATA]`.
  - Keys are alphanumeric with optional hyphens (`-`) or underscores (`_`).
  - A single space after `@key` is mandatory.
  - Values can be single-line (`@key value`) or multi-line using `>` (see below).
  - Lines without `@` or without a space after the key are invalid and ignored.
  - Comments enclosed in (% ... %) are allowed, either at the start of a line or within a line.

### Multi-line Values with `>` in `[METADATA]` fields

- For multi-line values, use `>` after the key: `@key >`.
- All subsequent lines until the next `@` or section end are part of the value, concatenated with newline characters (`\n`).
- Leading and trailing whitespace in each line is trimmed unless explicitly intended.

### Mandatory Field

- `@dotprompt_format_version`: Specifies the version of the `.prompt` specification (e.g., `@dotprompt_format_version 0.0.1`). Required in all files.

## `[DEFAULTS]` Section

Defines default values for variables used in `[CONTENT]`.

- **Location**: Optional, must follow `[METADATA]` and precede `[CONTENT]` if present.
- **Format**: Each line starts with `@`, followed by a variable name, a single space, and a value. Example: `@name Ana`.
- **Rules**:
  - Keys must be unique within `[DEFAULTS]`.
  - Keys are alphanumeric with optional hyphens (`-`) or underscores (`_`).
  - A single space after `@key` is mandatory.
  - Values can be single-line (`@key value`) or multi-line using `>` (see below).
  - Lines without `@` or without a space after the key are invalid and ignored.
  - Comments enclosed in (% ... %) are allowed, either at the start of a line or within a line.
- **Purpose**: Provides fallback values for variables in `[CONTENT]` if not overridden by external inputs during processing.

### Multi-line Values with `>` in `[DEFAULTS]` fields

- For multi-line values, use `>` after the variable: `@variable >`.
- All subsequent lines until the next `@` or section end are part of the value, concatenated with newline characters (`\n`).
- Leading and trailing whitespace in each line is trimmed unless explicitly intended.

## `[CONTENT]` Section

Contains the main text or instructions for the AI model.  

- **Location**: Must be the last section, following `[METADATA]` and `[DEFAULTS]` (if present).
- **Format**: Free text with support for variables and literal braces.
- **Rules**:
  - Must be present (a file without `[CONTENT]` is invalid).
  - Supports comments enclosed in (% ... %) that are removed during processing, applicable at the start of lines or within the text.
  - Variables are written as `{variable}` and replaced with provided values (or defaults from `[DEFAULTS]` if applicable).
  - Literal braces are written as `{{text}}` and converted to `{text}` in the final output.

### Processing `[CONTENT]`

1. Remove comments: Text between (%and%) is discarded, whether at the start of a line or inline.
2. Reduce literal braces: `{{text}}` becomes `{text}`.
3. Substitute variables: `{variable}` is replaced with its value if provided (first checking external inputs, then `[DEFAULTS]`); if neither is available, it remains as `{variable}` in the output.

## Full Example

```prompt
(% Example .prompt file for AI agent instructions %)
[METADATA]
@dotprompt_format_version 0.0.1
@name AgentRoleplayPrompt
@description >
  This prompt instructs an AI agent to role-play as a fictional character
  in a specified environment and century, with a defined hobby and task.
(% The description is generic to allow flexibility across use cases %)
@model_tested GPT-4o
@created 2025-01-15

[DEFAULTS]
@character Sherlock Holmes
@environment Victorian London
@century 19 (% Use numbers %)
@hobby playing the violin
@task investigate a mysterious case

[CONTENT]
(% Agent instructions %)
Act as {character} in {environment} during the {century}th century. 
Your hobby is {hobby}. Your task is to {task}. 
Provide a detailed response in the style of the character, 
using {{literal quotes}} where appropriate (% e.g., "Elementary, my dear Watson" %), 
and adapt to user input, {clue}.
```

## Implementation Notes

- **Validation**: Processors must:
  - Require `[CONTENT]`.
  - Ignore invalid lines in `[METADATA]` and `[DEFAULTS]`.
  - Support a validation mode to report errors (e.g., invalid lines, undefined variables).
- **Errors**: A file missing `[CONTENT]` must be considered invalid.
- **Flexibility**: Variables not defined in `[DEFAULTS]` or provided externally remain as `{variable}` in the output.

## Versioning

This is the initial standard (v0.0.1). Future changes will be documented with updated versions.
