import typer

from .commands.dump import dump

app = typer.Typer(help="Collection of utility scripts", no_args_is_help=True)

app.add_typer(dump.app, name="dump", no_args_is_help=True)

if __name__ == "__main__":
    app()
