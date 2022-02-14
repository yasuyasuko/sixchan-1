from flask import Blueprint
from flask.cli import with_appcontext

from sixchan.models import db

database = Blueprint("database", __name__)


@database.cli.command("create_tables")
@with_appcontext
def create_tables():
    db.create_all()
    for table_name in db.metadata.tables.keys():
        print(f"Table: {table_name}")
    print("😀 The above tables are created successfully.")


@database.cli.command("drop_tables")
@with_appcontext
def drop_tables():
    db.drop_all()
    for table_name in db.metadata.tables.keys():
        print(f"Table: {table_name}")
    print("😀 The above tables are dropped successfully.")
