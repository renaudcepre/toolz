import typer

from .commands import dump

app = typer.Typer(help="Collection of utility scripts")

app.add_typer(dump.app, name="dump")

if __name__ == "__main__":
    app()
