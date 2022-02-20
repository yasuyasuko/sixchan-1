import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import NamedTuple

from sqlalchemy import desc
from sqlalchemy import func

from sixchan.models import Board
from sixchan.models import OnymousAuthor
from sixchan.models import Res
from sixchan.models import Thread
from sixchan.models import UserAccount
from sixchan.utils import Pagination
from sixchan.utils import group_by


class UserResRow(NamedTuple):
    board_id: uuid.UUID
    board_name: str
    thread_id: uuid.UUID
    thread_name: str
    res_number: uuid.UUID
    res_who: str
    res_body: str
    res_created_at: datetime


@dataclass
class UserResQueryModel:
    number: int
    who: str
    body: str
    posted_at: datetime


@dataclass
class UserThreadQueryModel:
    id: uuid.UUID
    name: str
    board_id: uuid.UUID
    board_name: str
    reses: list[UserResQueryModel]

    @classmethod
    def from_rows(cls, rows: list[UserResRow]):
        reses = [
            UserResQueryModel(
                number=row.res_number,
                who=row.res_who,
                body=row.res_body,
                posted_at=row.res_created_at,
            )
            for row in rows
        ]
        reses.sort(key=lambda x: x.number)
        representative = rows[0]
        return cls(
            id=representative.thread_id,
            name=representative.thread_name,
            board_id=representative.board_id,
            board_name=representative.board_name,
            reses=reses,
        )


def get_threads_pagination(user: UserAccount, page: int, per_page: int):
    pagination = Pagination(page, per_page)

    total_query = (
        OnymousAuthor.query.join(Res)
        .filter(OnymousAuthor.author_id == user.id)
        .with_entities(Res.thread_id)
        .group_by(Res.thread_id)
    )

    total = total_query.count()
    if total <= 0:
        return pagination.get_empty_query_model()
    else:
        pagination.total = total

    subquery = (
        total_query.add_entity(func.max(Res.created_at).label("last_created_at"))
        .order_by(desc("last_created_at"))
        .limit(pagination.limit)
        .offset(pagination.offset)
        .subquery()
    )

    query = (
        OnymousAuthor.query.join(Res)
        .filter(OnymousAuthor.author_id == user.id)
        .with_entities(
            Board.id.label("board_id"),
            Board.name.label("board_name"),
            Res.thread_id,
            Thread.name.label("thread_name"),
            Res.number.label("res_number"),
            Res.who.label("res_who"),
            Res.body.label("res_body"),
            Res.created_at.label("res_created_at"),
        )
        .join(subquery, Res.thread_id == subquery.c.thread_id)
        .join(Thread)
        .join(Board)
    )

    items = [
        UserThreadQueryModel.from_rows(rows)
        for rows in group_by(query.all(), "thread_id", as_list=True)
    ]

    return pagination.get_query_model(items)
