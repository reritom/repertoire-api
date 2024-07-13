import json
import logging

import typer

from app.accounts.cli import app as accounts_cli
from app.database import Base, engine

logger = logging.getLogger(__name__)

app = typer.Typer()
app.add_typer(accounts_cli, name="accounts")


@app.command("generate-openapi")
def generate_openapi(output_path: str):
    from app.application import create_app

    data = create_app().openapi()

    for path_data in data["paths"].values():
        for operation in path_data.values():
            operation["operationId"] = operation["operationId"].split("_api_")[0]

    with open(output_path, "w") as f:
        json.dump(
            data,
            f,
            indent=2,
        )


@app.command("init-db")
def init_db():
    Base.metadata.create_all(engine)
    logger.info("Database tables created")


if __name__ == "__main__":
    app()
