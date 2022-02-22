from dataclasses import dataclass
from datetime import datetime
from typing import NamedTuple
from typing import Optional
from uuid import UUID

from sqlalchemy import func

from sixchan.config import INAPPROPRIATE_RES_BODY
from sixchan.models import AnonymousAuthor
from sixchan.models import OnymousAuthor
from sixchan.models import Res
from sixchan.models import Thread
from sixchan.models import UserAccount
from sixchan.models import UserProfile
from sixchan.utils import Pagination


class ThreadOverviewRow(NamedTuple):
    id: UUID
    name: str
    reses_count: int
    last_created_at: datetime


@dataclass
class ThreadOverviewQueryModel:
    id: UUID
    name: str
    reses_count: int
    last_posted_at: datetime

    @classmethod
    def from_row(cls, row: ThreadOverviewRow) -> "ThreadOverviewQueryModel":
        return cls(
            id=row.id,
            name=row.name,
            reses_count=row.reses_count,
            last_posted_at=row.last_created_at,
        )


class ResRow(NamedTuple):
    id: UUID
    number: int
    who: str
    body: str
    inappropriate: bool
    created_at: datetime
    anon_name: Optional[str]
    anon_email: Optional[str]
    username: Optional[str]
    display_name: Optional[str]


@dataclass
class ResQueryModel:
    id: UUID
    number: int
    who: str
    _body: str
    inappropriate: bool
    posted_at: datetime
    is_anonymous: bool
    name: str
    username: Optional[str] = None
    email: Optional[str] = None

    @property
    def body(self) -> str:
        if self.inappropriate:
            return INAPPROPRIATE_RES_BODY
        else:
            return self._body

    @classmethod
    def from_row(cls, row: ResRow) -> "ResQueryModel":
        is_anonymous = not bool(row.username)
        name = row.anon_name if is_anonymous else row.display_name
        name = name or "null"
        return cls(
            id=row.id,
            number=row.number,
            who=row.who,
            _body=row.body,
            inappropriate=row.inappropriate,
            posted_at=row.created_at,
            is_anonymous=is_anonymous,
            name=name,
            username=None if is_anonymous else row.username,
            email=row.anon_email if is_anonymous else None,
        )


@dataclass
class UserQueryModel:
    username: str
    display_name: str
    introduction: str


def get_threads_pagination(board_id: UUID, page: int, per_page: int):
    pagination = Pagination(page, per_page)

    total = Thread.query.filter_by(board_id=board_id).count()
    if total <= 0:
        return pagination.get_empty_query_model()
    else:
        pagination.total = total

    subquery = (
        Res.query.group_by(Res.thread_id)
        .with_entities(
            Res.thread_id,
            func.count(Res.id).label("reses_count"),
            func.max(Res.created_at).label("last_created_at"),
        )
        .subquery("reses")
    )
    query = (
        Thread.query.filter_by(board_id=board_id)
        .join(subquery, Thread.id == subquery.c.thread_id)
        .with_entities(
            Thread.id,
            Thread.name,
            subquery.c.reses_count,
            subquery.c.last_created_at,
        )
        .order_by(subquery.c.last_created_at.desc())
        .limit(pagination.limit)
        .offset(pagination.offset)
    )

    items = [ThreadOverviewQueryModel.from_row(row) for row in query.all()]
    return pagination.get_query_model(items)


def get_reses(thread_id: UUID) -> list[ResQueryModel]:
    query = (
        Res.query.filter_by(thread_id=thread_id)
        .with_entities(
            Res.id,
            Res.number,
            Res.who,
            Res.body,
            Res.inappropriate,
            Res.created_at,
            AnonymousAuthor.name.label("anon_name"),
            AnonymousAuthor.email.label("anon_email"),
            UserAccount.username,
            UserProfile.display_name,
        )
        .outerjoin(AnonymousAuthor)
        .outerjoin(OnymousAuthor)
        .outerjoin(UserAccount, OnymousAuthor.author_id == UserAccount.id)
        .outerjoin(UserProfile)
    )

    reses = [ResQueryModel.from_row(row) for row in query.all()]
    reses.sort(key=lambda x: x.number)
    return reses


def get_res(res_id: UUID) -> ResQueryModel:
    query = (
        Res.query.filter_by(id=res_id)
        .outerjoin(AnonymousAuthor)
        .outerjoin(OnymousAuthor)
        .outerjoin(UserAccount, OnymousAuthor.author_id == UserAccount.id)
        .outerjoin(UserProfile)
        .with_entities(
            Res.id,
            Res.number,
            Res.who,
            Res.body,
            Res.inappropriate,
            Res.created_at,
            AnonymousAuthor.name.label("anon_name"),
            AnonymousAuthor.email.label("anon_email"),
            UserAccount.username,
            UserProfile.display_name,
        )
    )
    row = query.first()
    return ResQueryModel.from_row(row)


def get_user(username: str) -> UserQueryModel:
    query = (
        UserAccount.query.filter_by(username=username)
        .join(UserProfile)
        .with_entities(
            UserAccount.username,
            UserProfile.display_name,
            UserProfile.introduction,
        )
    )
    return UserQueryModel(**query.first())
