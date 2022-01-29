import json
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Res(db.Model):
    __tablename__ = "reses"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    who = db.Column(db.String(22), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


def insert_mock_reses():
    with open("mockdata.json", encoding="utf-8") as f:
        mock_data = json.load(f)
    for res in mock_data["reses"]:
        created_at = datetime.fromisoformat(res.pop("created_at"))
        db.session.add(Res(created_at=created_at, **res))
    db.session.commit()
