import shutil
import subprocess
from pathlib import Path

import typer
from rich import print
from rich.console import Console
from rich.markdown import Markdown

app = typer.Typer(help="Dump file contents with markdown code blocks")
console = Console()



BASE_EXCLUSIONS = [
    ".*",
    "__*",
    "node_modules",
    "venv",
    "dist",
    "build",
    "*.log",
    "*.tmp",
    "coverage.xml",
    "*.pyc",
    "*.pyo",
    "Thumbs.db",
    "*.egg-info",
    "*.lock",
    "package-lock.json",
    "pip-wheel-metadata",
    "target",
    ".output", ".nuxt", ".git"
]

LANGUAGE_MAPPING = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".sh": "bash",
    ".html": "html",
    ".css": "css",
    ".json": "json",
    ".xml": "xml",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".md": "markdown",
    ".cpp": "cpp",
    ".hpp": "cpp",
    ".java": "java",
}


def get_language_type(file_path: Path) -> str:
    """Determine the language type based on file extension."""
    return LANGUAGE_MAPPING.get(file_path.suffix, "")


def copy_to_clipboard(text: str) -> bool:
    """Copy text to clipboard on Linux or Linux in WSL."""
    try:
        with open("/proc/version") as f:
            if "microsoft" in f.read().lower():
                # WSL-specific clipboard support
                clip_path = shutil.which("clip.exe")
                if not clip_path:
                    raise FileNotFoundError("clip.exe not found in PATH")
                process = subprocess.Popen([clip_path], stdin=subprocess.PIPE)  # noqa
                process.communicate(text.encode("utf-16-le"))
                return True

        # Standard Linux clipboard
        xclip_path = shutil.which("xclip")
        if not xclip_path:
            raise FileNotFoundError("xclip not found in PATH")
        subprocess.run(  # noqa
            [xclip_path, "-selection", "clipboard"], input=text.encode(), check=True
        )
        return True
    except (OSError, subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"[red]Error: {e}[/red]")
        return False


def is_binary_file(file_path: Path) -> bool:
    """Check if a file is binary."""
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
        return b"\0" in chunk
    except OSError:
        return False


def dump_content(
    path: Path,
    pattern: str,
    exclusions: list[str],
    output: list[str],
    excluded_files: list[str],
) -> None:
    """Recursively dump file contents with markdown code blocks."""
    try:
        for item in path.iterdir():
            # Skip excluded patterns
            if any(item.match(excl) for excl in exclusions):
                excluded_files.append(f"`{str(item)}`: _excluded_")
                continue

            if item.is_file():
                if not item.match(pattern):
                    excluded_files.append(f"`{str(item)}`: _do not match {pattern}_")
                    continue

                # Skip binary files
                if is_binary_file(item):
                    excluded_files.append(f"`{str(item)}`: _is binary_")
                    continue

                # Skip empty files
                if item.stat().st_size == 0:
                    excluded_files.append(f"`{str(item)}`: _empty_")
                    continue

                try:
                    content = item.read_text(encoding="utf-8")
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
    path: Path = typer.Argument(
        ...,
        help="Path to search",
    ),
    clipboard: bool = typer.Option(
        False,
        "--clipboard",
        "-c",
        help="Copy output to clipboard",
    ),
    pretty: bool = typer.Option(
        False,
        "--pretty",
        help="Display markdown markup",
    ),
    pattern: str = typer.Option(
        "*",
        help="File pattern to match",
    ),
    exclude: str = typer.Option(
        None,
        help=f"Comma-separated paths to exclude, "
        f"[default: {",".join(BASE_EXCLUSIONS)}]",
        show_default=False,
    ),
) -> None:
    """Dump file contents with Markdown code blocks."""
    if not path.exists():
        print(f"[red]Error: Path '{path}' does not exist[/red]")
        raise typer.Exit(1)

    additional_exclusions = [p.strip() for p in exclude.split(",")] if exclude else []
    exclusions = list(set(BASE_EXCLUSIONS + additional_exclusions))
    output: list[str] = []
    excluded_files: list[str] = []

    dump_content(path, pattern, exclusions, output, excluded_files)

    # Add header with excluded files
    exclusion_footer = [
        "# Excluded Files",
        "The following files and directories were excluded during the dump:\n",
        ">-" + "\n >-".join(f" {file}" for file in excluded_files),
        "",
    ]

    header = f"# `{path.absolute()}`\n"

    output = [header] + output + exclusion_footer

    if not output:
        print("[yellow]No matching files found[/yellow]")
        raise typer.Exit(0)

    result = "\n".join(output)

    if clipboard:
        if copy_to_clipboard(result):
            print(f"[green]{len(output)} lines copied to clipboard[/green]")
        else:
            print(
                "[red]Error: Could not copy to clipboard."
                " No clipboard utility available.[/red]"
            )
            _render_result_to_console(result, pretty)
    else:
        _render_result_to_console(result, pretty)


def _render_result_to_console(result: str, pretty: bool = False) -> None:
    if not pretty:
        console.print(result, markup=False)
    else:
        md = Markdown(result)
        console.print(md)
