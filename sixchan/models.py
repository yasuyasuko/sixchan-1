import secrets
import uuid
from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import Optional
from typing import Text
from typing import Union

from flask_login import AnonymousUserMixin
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import UUID as PostgreUUID
from sqlalchemy.engine import Dialect
from sqlalchemy.types import CHAR
from sqlalchemy.types import TypeDecorator
from sqlalchemy.types import TypeEngine
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from sixchan.config import ANON_NAME_MAX_LENGTH, MAX_RESES_PER_THREAD
from sixchan.config import BOARD_CATEGORY_NAME_MAX_LENGTH
from sixchan.config import BOARD_NAME_MAX_LENGTH
from sixchan.config import DISPLAY_NAME_MAX_LENGTH
from sixchan.config import EMAIL_MAX_LENGTH
from sixchan.config import THREAD_NAME_MAX_LENGTH
from sixchan.config import USERNAME_MAX_LENGTH
from sixchan.extensions import db
from sixchan.utils import get_hash_from_words


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


class ExpirableTokenMixin:
    token = db.Column(db.String(128), primary_key=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)

    @property
    def expired(self):
        return self.expires_at < datetime.utcnow()


class ActivationToken(ExpirableTokenMixin, db.Model):
    __tablename__ = "activation_tokens"
    account_id = db.Column(UUID(), db.ForeignKey("user_accounts.id"), nullable=False)

    @classmethod
    def generate(cls, user, expires_duration: timedelta) -> str:
        token = secrets.token_urlsafe()
        expires_at = datetime.utcnow() + expires_duration
        obj = cls(token=token, user_id=user.id, expires_at=expires_at)
        db.session.add(obj)
        return token


class ChangeEmailConfiramtionToken(ExpirableTokenMixin, db.Model):
    __tablename__ = "change_email_confirmation_tokens"
    account_id = db.Column(UUID(), db.ForeignKey("user_accounts.id"), nullable=False)
    new_email = db.Column(db.String(128), nullable=False)

    @classmethod
    def generate(cls, user, expires_duration: timedelta, new_email: str) -> str:
        token = secrets.token_urlsafe()
        expires_at = datetime.utcnow() + expires_duration
        obj = cls(
            token=token, user_id=user.id, expires_at=expires_at, new_email=new_email
        )
        db.session.add(obj)
        return token


class AnonymousUser(AnonymousUserMixin):
    def __init__(self, name: Optional[str] = None, email: Optional[str] = None) -> None:
        self.name = name
        self.email = email

    @property
    def has_personal_information(self) -> bool:
        return bool(self.name or self.email)


class UserAccount(UUIDMixin, TimestampMixin, UserMixin, db.Model):
    __tablename__ = "user_accounts"
    username = db.Column(db.String(USERNAME_MAX_LENGTH), unique=True, nullable=False)
    email = db.Column(db.String(EMAIL_MAX_LENGTH), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    activated = db.Column(db.Boolean, default=False, nullable=False)
    profile = db.relationship("UserProfile", uselist=False)

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
        new_account = cls(
            username=username,
            display_name=display_name or username,
            email=email,
            activated=False,
        )
        new_account.password = password
        new_account.profile = UserProfile(display_name=display_name or username)
        db.session.add(new_account)
        db.session.flush()
        return new_account

    def activate(self):
        self.activated = True


class UserProfile(TimestampMixin, db.Model):
    __tablename__ = "user_profiles"
    account_id = db.Column(UUID(), db.ForeignKey("user_accounts.id"), primary_key=True)
    display_name = db.Column(db.String(DISPLAY_NAME_MAX_LENGTH), nullable=True)
    introduction = db.Column(db.Text, nullable=True)
    reses = db.relationship(
        "Res", backref=db.backref("author", uselist=False), secondary="onymous_authors"
    )


class AnonymousAuthor(db.Model):
    __tablename__ = "anonymous_authors"
    res_id = db.Column(UUID(), db.ForeignKey("reses.id"), primary_key=True)
    name = db.Column(db.String(ANON_NAME_MAX_LENGTH), nullable=True)
    email = db.Column(db.String(EMAIL_MAX_LENGTH), nullable=True)


class OnymousAuthor(db.Model):
    __tablename__ = "onymous_authors"
    res_id = db.Column(UUID(), db.ForeignKey("reses.id"), primary_key=True)
    author_id = db.Column(
        UUID(), db.ForeignKey("user_profiles.account_id"), nullable=False
    )


class Res(UUIDMixin, TimestampMixin, db.Model):
    __tablename__ = "reses"
    number = db.Column(db.Integer, nullable=False)
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
        self, body: str, who_seeds: list[str], user: Union[UserAccount, AnonymousUser]
    ):
        if self.next_res_number > MAX_RESES_PER_THREAD:
            raise RuntimeError("This thread reaches limit.")

        new_res_id = uuid.uuid4()
        new_res = Res(
            id=new_res_id,
            number=self.next_res_number,
            who=get_hash_from_words(*who_seeds),
            body=body,
        )
        self.reses.append(new_res)

        if isinstance(user, UserAccount):
            db.session.add(OnymousAuthor(res_id=new_res_id, author_id=user.id))
        elif isinstance(user, AnonymousUser):
            if user.has_personal_information:
                db.session.add(
                    AnonymousAuthor(res_id=new_res_id, name=user.name, email=user.email)
                )
        else:
            pass

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
