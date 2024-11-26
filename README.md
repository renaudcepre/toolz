# Personal Scripts Collection

Collection of command-line utility scripts, focusing on developer productivity.

## Installation

### Prerequisites
- Python 3.12+
- zsh shell (for automatic PATH configuration)

### Quick Install
```bash
./install.sh
```

The installer will:
1. Install [uv](https://astral.sh/uv) package manager if not present
2. Create a Python virtual environment
3. Install the package in editable mode
4. Add the virtual environment to your PATH in `.zshrc`


## Available Tools

### `dump` - File Content Dumper

Dumps file contents with Markdown code blocks. Useful for:
- Sharing code snippets with proper syntax highlighting
- Creating documentation from source files
- Quick code reviews and sharing
- Creating Markdown-formatted file exports

#### Usage
```bash
# Basic usage - dump all files in current directory
tz dump .

# Dump specific file types only
tz dump . --pattern "*.py"

# Copy output to clipboard
tz dump . -c

# Pretty print with Markdown formatting
tz dump . --pretty

# Exclude additional patterns
tz dump . --exclude "tests,*.md"
```
