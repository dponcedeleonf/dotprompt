# `.prompt`  - A semi-structured text format for AI prompts

Welcome to the DOTPROMPT project, a lightweight and semi-structured format designed for defining and managing prompts for generative AI models. The `.prompt` format aims to standardize the creation, versioning, and processing of prompts. This repository serves as the central hub for the format specification and its implementations.

## Overview

The `.prompt` format is a **semi-structured text format** designed for defining and managing prompts for generative AI models, featuring three sections:

- `[METADATA]`: Descriptive information (e.g., name, version, author).
- `[DEFAULTS]`: Default values for variables.
- `[CONTENT]`: The prompt text with placeholders for dynamic content.

This design supports dynamic prompt generation, metadata management, and collaboration, making it ideal for AI-driven workflows and agent systems.

## Implementations

This repository contains not only the format specification but also its reference implementations. Currently, there is a Python implementation available, with potential for additional language implementations in the future. Each implementation has its own documentation in its respective directory.

## Documentation

- **[SPECIFICATION.md](docs/SPECIFICATION.md)**: Detailed rules of the `.prompt` format.
- **[RATIONALE.md](docs/RATIONALE.md)**: Why `.prompt` is necessary and its advantages over alternatives.

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

For questions or feedback, please open an issue or reach out via the repository.
