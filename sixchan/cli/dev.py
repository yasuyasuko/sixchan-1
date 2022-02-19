from graphlib import TopologicalSorter
from importlib import import_module
from pathlib import Path

import click
import yaml
from flask import Blueprint

from sixchan.extensions import db

MOCKS_DIR = Path(__file__).parent / "mocks"
dev = Blueprint("dev", __name__)
dev.cli.help = "Group of development tools."


def _load_yaml(path: Path):
    with open(path, encoding="utf-8") as f:
        return yaml.load(f, yaml.CLoader)


@dev.cli.command("insert_mockdata")
def insert_mockdata():
    data_list = [_load_yaml(yml) for yml in MOCKS_DIR.glob("*.yml")]
    dependence_graph = {d["class"]: set(d.get("depends", {})) for d in data_list}
    ts = TopologicalSorter(dependence_graph)
    class_order = tuple(ts.static_order())
    models_module = import_module("sixchan.models")
    for class_name in class_order:
        class_ = getattr(models_module, class_name)
        records = [d for d in data_list if d["class"] == class_name][0]["records"]
        db.session.execute(class_.__table__.insert(), records)
        db.session.commit()

    click.secho("😀 Mockdata are inserted successfully.", fg="green")
