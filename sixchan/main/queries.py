from dataclasses import dataclass
from datetime import datetime
from typing import NamedTuple, Optional

from sixchan.models import (
    UUID,
    AnonymousAuthor,
    OnymousAuthor,
    Res,
    UserAccount,
    UserProfile,
)


class ResRow(NamedTuple):
    number: int
    who: str
    body: str
    created_at: datetime
    anon_name: Optional[str]
    anon_email: Optional[str]
    username: Optional[str]
    display_name: Optional[str]


@dataclass
class ResQueryModel:
    number: int
    who: str
    body: str
    posted_at: datetime
    is_anonymous: bool
    name: str
    username: Optional[str] = None
    email: Optional[str] = None

    @classmethod
    def from_row(cls, row: ResRow) -> "ResQueryModel":
        is_anonymous = bool(row.username)
        return cls(
            number=row.number,
            who=row.number,
            body=row.body,
            posted_at=row.created_at,
            is_anonymous=is_anonymous,
            name=row.anon_name or "null" if is_anonymous else row.display_name,
            username=None if is_anonymous else row.username,
            email=row.anon_email if is_anonymous else None,
        )


@dataclass
class UserQueryModel:
    username: str
    display_name: str
    introduction: str


def get_reses(thread_id: UUID) -> list[ResQueryModel]:
    query = (
        Res.query.filter_by(thread_id=thread_id)
        .with_entities(
            Res.number,
            Res.who,
            Res.body,
            Res.created_at,
            AnonymousAuthor.name.label("anon_name"),
            AnonymousAuthor.email.label("anon_email"),
            UserAccount.username,
            UserProfile.display_name,
        )
        .outerjoin(AnonymousAuthor)
        .outerjoin(OnymousAuthor)
        .outerjoin(UserAccount, OnymousAuthor.author_id == UserAccount.id)
        .outerjoin(AnonymousAuthor)
    )

    reses = [ResQueryModel.from_row(row) for row in query.all()]
    reses.sort(key=lambda x: x.number)
    return reses


def get_user(username: str) -> UserQueryModel:
    query = (
        UserAccount.query.filter_by(username=username)
        .with_entities(
            UserAccount.username,
            UserProfile.display_name,
            UserProfile.introduction,
        )
        .join(UserProfile)
    )
    return UserQueryModel(**query.first())
