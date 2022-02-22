import uuid
from graphlib import TopologicalSorter
from importlib import import_module
from pathlib import Path
from random import randint

import click
import yaml
from faker import Faker
from flask import Blueprint

from sixchan.extensions import db
from sixchan.models import UUID
from sixchan.models import Res
from sixchan.models import Thread

MOCKS_DIR = Path(__file__).parent / "mocks"
dev = Blueprint("dev", __name__)
dev.cli.help = "Group of development tools."


def _load_yaml(path: Path):
    with open(path, encoding="utf-8") as f:
        return yaml.load(f, yaml.CLoader)


@dev.cli.command("insert_mockdata")
def insert_mockdata() -> None:
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


@dev.cli.group()
def fake():
    pass


@fake.command()
@click.option("-b", "--board_id", required=True, type=click.UUID)
@click.option("-n", "--num", required=True, type=int)
def thread(board_id: UUID, num: int) -> None:
    faker = Faker("ja_JP")
    threads = []
    reses = []
    for _ in range(num):
        thread_id = uuid.uuid4()
        threads.append(
            {"id": thread_id, "name": faker.sentence(), "board_id": board_id}
        )
        for n in range(1, randint(2, 1001)):
            reses.append(
                {
                    "id": uuid.uuid4(),
                    "number": n,
                    "who": "ThisIsFake123456789012",
                    "body": faker.text(),
                    "thread_id": thread_id,
                }
            )
    db.session.execute(Thread.__table__.insert(), threads)
    db.session.commit()
    db.session.execute(Res.__table__.insert(), reses)
    db.session.commit()
    click.secho(f"😀 {num} fake threads are inserted successfully.", fg="green")


@fake.command()
@click.option("-t", "--thread_id", required=True, type=click.UUID)
@click.option("-n", "--num", required=True, type=int)
def res(thread_id: UUID, num: int) -> None:
    faker = Faker("ja_JP")
    thread = Thread.query.get(thread_id)
    current_number = thread.reses_count
    reses = []
    for n in range(1, num + 1):
        reses.append(
            {
                "id": uuid.uuid4(),
                "number": current_number + n,
                "who": "ThisIsFake123456789012",
                "body": faker.text(),
                "thread_id": thread_id,
            }
        )
    db.session.execute(Res.__table__.insert(), reses)
    db.session.commit()
    click.secho(f"😀 {num} fake reses are inserted successfully.", fg="green")
