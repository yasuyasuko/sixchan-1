import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import NamedTuple

from sqlalchemy import desc, func

from sixchan.models import Board, OnymousAuthor, Res, Thread, UserAccount
from sixchan.queries import PaginationQueryModel
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
    if page < 1 or not isinstance(page, int):
        raise ValueError(
            f"page must be integer greater than or equal to 1, page:{page}"
        )
    if per_page < 1 or not isinstance(per_page, int):
        raise ValueError(
            f"per_page must be integer greater than or equal to 1, per_page:{per_page}"
        )

    total_query = (
        OnymousAuthor.query.join(Res)
        .filter(OnymousAuthor.author_id == user.id)
        .with_entities(Res.thread_id)
        .group_by(Res.thread_id)
    )

    total = total_query.count()
    if total <= 0:
        return PaginationQueryModel(1, 1, [])

    pages = total // per_page + 1
    limit = per_page
    offset = per_page * (page - 1)

    subquery = (
        total_query.add_entity(func.max(Res.created_at).label("last_created_at"))
        .order_by(desc("last_created_at"))
        .limit(limit)
        .offset(offset)
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

    return PaginationQueryModel(page, pages, items)
