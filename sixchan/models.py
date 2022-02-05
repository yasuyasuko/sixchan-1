import json
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Any, Optional, Text

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID as PostgreUUID
from sqlalchemy.engine import Dialect
from sqlalchemy.types import CHAR, TypeDecorator, TypeEngine
from werkzeug.security import check_password_hash, generate_password_hash

from sixchan.config import (
    ANON_NAME_MAX_LENGTH,
    BOARD_CATEGORY_NAME_MAX_LENGTH,
    BOARD_NAME_MAX_LENGTH,
    DISPLAY_NAME_MAX_LENGTH,
    EMAIL_MAX_LENGTH,
    THREAD_NAME_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
)
from sixchan.utils import get_b64encoded_digest_string_from_words

db = SQLAlchemy()


class UUID(TypeDecorator):
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect: Dialect) -> TypeEngine[Any]:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PostgreUUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(
        self, value: Optional[Any], dialect: Dialect
    ) -> Optional[Text]:
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value).hex
            else:
                return f"{value.int:032x}"

    def process_result_value(
        self, value: Optional[Any], dialect: Dialect
    ) -> Optional[Any]:
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


class UUIDMixin:
    id = db.Column(UUID(), primary_key=True, default=uuid.uuid4)


class TimestampMixin:
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class ActivationToken(db.Model):
    __tablename__ = "activation_tokens"
    token = db.Column(db.String(128), primary_key=True, nullable=False)
    user_id = db.Column(UUID(), db.ForeignKey("users.id"), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)

    @classmethod
    def generate(cls, user, expire_duration: timedelta) -> str:
        token = secrets.token_urlsafe()
        expires_at = datetime.utcnow() + expire_duration
        obj = cls(token=token, user_id=user.id, expires_at=expires_at)
        db.session.add(obj)
        return token

    @property
    def expired(self):
        return self.expires_at < datetime.utcnow()


class User(UUIDMixin, TimestampMixin, UserMixin, db.Model):
    __tablename__ = "users"
    username = db.Column(db.String(USERNAME_MAX_LENGTH), unique=True, nullable=False)
    display_name = db.Column(db.String(DISPLAY_NAME_MAX_LENGTH), nullable=True)
    email = db.Column(db.String(EMAIL_MAX_LENGTH), unique=True, nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)
    activated = db.Column(db.Boolean, default=False, nullable=False)
    introduction = db.Column(db.Text, nullable=True)
    reses = db.relationship("Res", backref="author")

    def get_id(self):
        """flask-login requires this method to identify users"""
        return self.username

    def is_active(self):
        """flask-login requires this method to know whether or not a user is active"""
        return self.activated

    @property
    def password(self):
        raise AttributeError("password is not a readable")

    @password.setter
    def password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password: str):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def signup(
        cls,
        username: str,
        email: str,
        password: str,
        display_name: Optional[str] = None,
    ):
        new_user = cls(
            username=username,
            display_name=display_name or username,
            email=email,
            activated=False,
        )
        new_user.password = password
        db.session.add(new_user)
        db.session.flush()
        return new_user

    def activate(self):
        self.activated = True


class Res(UUIDMixin, TimestampMixin, db.Model):
    __tablename__ = "reses"
    number = db.Column(db.Integer, nullable=False)
    anon_name = db.Column(db.String(ANON_NAME_MAX_LENGTH), nullable=True)
    anon_email = db.Column(db.String(EMAIL_MAX_LENGTH), nullable=True)
    author_id = db.Column(UUID(), db.ForeignKey("users.id"), nullable=True)
    who = db.Column(db.String(22), nullable=False)
    body = db.Column(db.Text, nullable=False)
    thread_id = db.Column(UUID(), db.ForeignKey("threads.id"), nullable=False)


class Thread(UUIDMixin, TimestampMixin, db.Model):
    __tablename__ = "threads"
    name = db.Column(db.String(THREAD_NAME_MAX_LENGTH), nullable=False)
    board_id = db.Column(UUID(), db.ForeignKey("boards.id"), nullable=False)
    reses = db.relationship("Res", backref="thread")

    @property
    def reses_count(self) -> int:
        return len(self.reses)

    @property
    def next_res_number(self) -> int:
        return self.reses_count + 1

    @property
    def last_posted_at(self) -> datetime:
        last_res = (
            Res.query.filter_by(thread_id=self.id)
            .order_by(Res.created_at.desc())
            .first()
        )
        return last_res.created_at

    def post_res(
        self,
        body: str,
        who_seeds: list[str],
        anon_name: Optional[str] = None,
        anon_email: Optional[str] = None,
    ):
        new_res = Res(
            number=self.next_res_number,
            anon_name=anon_name or None,
            anon_email=anon_email or None,
            who=get_b64encoded_digest_string_from_words(*who_seeds),
            body=body,
        )
        self.reses.append(new_res)
        return new_res


class Board(UUIDMixin, TimestampMixin, db.Model):
    __tablename__ = "boards"
    name = db.Column(db.String(BOARD_NAME_MAX_LENGTH), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    category_id = db.Column(
        UUID(), db.ForeignKey("board_categories.id"), nullable=False
    )
    threads = db.relationship("Thread", backref="board")

    def post_thread(self, thread_name: str):
        new_thread = Thread(name=thread_name, board_id=self.id)
        self.threads.append(new_thread)
        return new_thread


class BoardCategory(UUIDMixin, TimestampMixin, db.Model):
    __tablename__ = "board_categories"
    name = db.Column(
        db.String(BOARD_CATEGORY_NAME_MAX_LENGTH), unique=True, nullable=False
    )
    boards = db.relationship("Board", backref="board_category")


def insert_mockdata():
    with open("mockdata.json", encoding="utf-8") as f:
        mock_data = json.load(f)

    for category in mock_data["board_categories"]:
        id = uuid.UUID(category.pop("id"))
        created_at = datetime.fromisoformat(category.pop("created_at"))
        db.session.add(BoardCategory(id=id, created_at=created_at, **category))

    for board in mock_data["boards"]:
        id = uuid.UUID(board.pop("id"))
        created_at = datetime.fromisoformat(board.pop("created_at"))
        category_id = uuid.UUID(board.pop("category_id"))
        db.session.add(
            Board(id=id, created_at=created_at, category_id=category_id, **board)
        )

    for thread in mock_data["threads"]:
        id = uuid.UUID(thread.pop("id"))
        created_at = datetime.fromisoformat(thread.pop("created_at"))
        board_id = uuid.UUID(thread.pop("board_id"))
        db.session.add(
            Thread(id=id, created_at=created_at, board_id=board_id, **thread)
        )

    for res in mock_data["reses"]:
        id = uuid.UUID(res.pop("id"))
        created_at = datetime.fromisoformat(res.pop("created_at"))
        thread_id = uuid.UUID(res.pop("thread_id"))
        db.session.add(Res(id=id, created_at=created_at, thread_id=thread_id, **res))

    for user in mock_data["users"]:
        id = uuid.UUID(user.pop("id"))
        created_at = datetime.fromisoformat(user.pop("created_at"))
        updated_at = datetime.fromisoformat(user.pop("updated_at"))
        password_hash = generate_password_hash(user.pop("password"))
        db.session.add(
            User(
                id=id,
                created_at=created_at,
                updated_at=updated_at,
                password_hash=password_hash,
                **user,
            )
        )

    db.session.commit()
