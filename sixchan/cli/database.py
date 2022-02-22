import click
from flask import Blueprint
from flask.cli import with_appcontext

from sixchan.extensions import db

database = Blueprint("database", __name__)
database.cli.help = "Group of database operations."


@database.cli.command("create_tables")
@with_appcontext
def create_tables() -> None:
    db.create_all()
    for table_name in db.metadata.tables.keys():
        click.echo(f"Table: {table_name}")
    click.secho("😀 The above tables are created successfully.", fg="green")


@database.cli.command("drop_tables")
@with_appcontext
def drop_tables() -> None:
    db.drop_all()
    for table_name in db.metadata.tables.keys():
        click.echo(f"Table: {table_name}")
    click.secho("😀 The above tables are dropped successfully.", fg="green")
