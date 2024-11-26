# `/home/renaud/scripts`

 ### File: `src/cli.py`
```python
import typer
from .commands import dump

app = typer.Typer(help="Collection of utility scripts")

app.add_typer(dump.app, name="dump")

if __name__ == "__main__":
    app()

```

 ### File: `src/commands/dump.py`
```python
import typer
from pathlib import Path
import subprocess
from rich.console import Console
import platform
from rich import print

app = typer.Typer(help="Dump file contents with markdown code blocks")
console = Console()

DEFAULT_EXCLUSIONS = [
    ".git", ".idea", ".vscode", "node_modules", ".venv", "venv", "__pycache__",
    "dist", "build", "*.log", "*.tmp", ".DS_Store", ".pytest_cache", ".mypy_cache",
    ".tox", ".coverage", "coverage.xml", ".nyc_output", "*.pyc", "*.pyo",
    "Thumbs.db", ".sass-cache", "*.egg-info", "*.lock", "package-lock.json",
    "pip-wheel-metadata", ".parcel-cache", ".next", "target", ".gradle",
    ".history", ".ipynb_checkpoints"
]

LANGUAGE_MAPPING = {
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.sh': 'bash',
    '.html': 'html',
    '.css': 'css',
    '.json': 'json',
    '.xml': 'xml',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.md': 'markdown',
    '.cpp': 'cpp',
    '.hpp': 'cpp',
    '.java': 'java'
}

def get_language_type(file_path: Path) -> str:
    """Determine the language type based on file extension."""
    return LANGUAGE_MAPPING.get(file_path.suffix, '')

def copy_to_clipboard(text: str) -> bool:
    """Copy text to clipboard based on the platform."""
    system = platform.system().lower()

    try:
        if system == "windows":
            subprocess.run(['clip'], input=text.encode('utf-16-le'), check=True)
        elif system == "linux":
            with open('/proc/version', 'r') as f:
                if 'microsoft' in f.read().lower():
                    process = subprocess.Popen(['clip.exe'], stdin=subprocess.PIPE)
                    process.communicate(text.encode('utf-16-le'))
                else:
                    subprocess.run(['xclip', '-selection', 'clipboard'], input=text.encode(), check=True)
        elif system == "darwin":
            subprocess.run(['pbcopy'], input=text.encode(), check=True)
        else:
            return False
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def is_binary_file(file_path: Path) -> bool:
    """Check if a file is binary."""
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
        return b'\0' in chunk
    except (OSError, IOError):
        return False
def dump_content(
        path: Path,
        pattern: str,
        exclusions: list,
        output: list,
        excluded_files: list
) -> None:
    """Recursively dump file contents with markdown code blocks."""
    try:
        for item in path.iterdir():
            # Skip excluded patterns
            if any(item.match(excl) for excl in exclusions):
                excluded_files.append(str(item))
                continue

            if item.is_file():
                if not item.match(pattern):
                    excluded_files.append(str(item))
                    continue

                # Skip binary files
                if is_binary_file(item):
                    excluded_files.append(str(item))
                    continue

                # Skip empty files
                if item.stat().st_size == 0:
                    excluded_files.append(str(item))
                    continue

                try:
                    content = item.read_text(encoding='utf-8')
                except UnicodeDecodeError:
                    excluded_files.append(str(item))
                    continue  # Skip files with decoding errors

                lang = get_language_type(item)
                output.append(f" ### File: `{item}`")
                output.append(f"```{lang}")
                output.append(content)
                output.append("```")
                output.append("")  # Empty line between files

            elif item.is_dir():
                dump_content(item, pattern, exclusions, output, excluded_files)
    except PermissionError:
        excluded_files.append(str(path))


@app.callback(invoke_without_command=True)
def main(
        path: Path = typer.Argument(..., help="Path to search"),
        clipboard: bool = typer.Option(False, "--clipboard", "-c", help="Copy output to clipboard"),
        pattern: str = typer.Option("*", help="File pattern to match"),
        exclude: str = typer.Option(",".join(DEFAULT_EXCLUSIONS), help="Comma-separated paths to exclude"),
):
    """Dump file contents with markdown code blocks."""
    if not path.exists():
        print(f"Error: Path '{path}' does not exist")
        raise typer.Exit(1)

    exclusions = 
    output = []
    excluded_files = []

    dump_content(path, pattern, exclusions, output, excluded_files)

    # Add header with excluded files
    exclusion_footer = [
        "# Excluded Files",
        "The following files and directories were excluded during the dump:\n```",
        "\n".join(f"- {file}" for file in excluded_files),
        "```"
    ]

    header = f"# `{path.absolute()}`\n"

    output =  + output + exclusion_footer

    if not output:
        print("No matching files found")
        raise typer.Exit(0)

    result = "\n".join(output)

    if clipboard:
        if copy_to_clipboard(result):
            print(f"{len(output)} lines copied to clipboard")
        else:
            print("Error: Could not copy to clipboard. No clipboard utility available.")
            print(result)
    else:
        print(result)
```

 ### File: `.gitignore`
```
# Python-generated files
__pycache__/
*.py
build/
dist/
wheels/
*.egg-info

# Virtual environments
.venv

```

 ### File: `pyproject.toml`
```

name = "scripts"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "psutil>=6.1.0",
    "rich>=13.9.4",
    "typer>=0.13.1",
]



requires = ["hatchling"]
build-backend = "hatchling.build"


tz = "src.cli:app"


packages = ["src"]


dev = [
    "ruff>=0.8.0",
]

```

 ### File: `.python-version`
```
3.12

```

 ### File: `install.sh`
```bash
#!/bin/bash

# Chemin absolu du répertoire du script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Installer uv si nécessaire
if ! command -v uv &> /dev/null; then
    echo "Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Créer un environnement virtuel s'il n'existe pas déjà
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    echo "Creating virtual environment..."
    uv venv
fi

# Installer le package en mode éditable
echo "Installing package..."
source .venv/bin/activate
uv pip install -e .

# Ajouter le chemin au .zshrc s'il n'y est pas déjà
VENV_PATH_LINE="export PATH=\"$SCRIPT_DIR/.venv/bin:\$PATH\""
if ! grep -q "$VENV_PATH_LINE" "$HOME/.zshrc"; then
    echo "Adding virtual environment to PATH in .zshrc..."
    echo "" >> "$HOME/.zshrc"
    echo "# Added by my-scripts installer" >> "$HOME/.zshrc"
    echo "$VENV_PATH_LINE" >> "$HOME/.zshrc"
    echo "Virtual environment added to PATH. Please run 'source ~/.zshrc' to apply changes."
else
    echo "PATH already configured in .zshrc"
fi

echo "Installation completed! Please run 'source ~/.zshrc' to use the commands in your current shell."
```

# Excluded Files
The following files and directories were excluded during the dump:
```
- .venv
- src/__pycache__
- src/__init__.py
- src/commands/__pycache__
- src/commands/__init__.py
- .idea
- README.md
- .git
- uv.lock
- out.md
```
