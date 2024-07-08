import typer

from app.accounts.cli import app as accounts_cli

app = typer.Typer()
app.add_typer("accounts", accounts_cli)
