from flask_wtf import FlaskForm
from wtforms import BooleanField
from wtforms import PasswordField
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms.validators import Email
from wtforms.validators import EqualTo
from wtforms.validators import Length
from wtforms.validators import Optional
from wtforms.validators import Regexp

from sixchan.config import DISPLAY_NAME_MAX_LENGTH
from sixchan.config import PASSWORD_REGEX
from sixchan.config import USERNAME_MAX_LENGTH
from sixchan.config import USERNAME_REGEX


class LoginForm(FlaskForm):
    username = StringField(
        "ユーザー名",
        validators=[
            DataRequired(),
            Regexp(USERNAME_REGEX),
            Length(max=USERNAME_MAX_LENGTH),
        ],
    )
    password = PasswordField(
        "パスワード",
        validators=[DataRequired(), Regexp(PASSWORD_REGEX)],
    )
    remember_me = BooleanField(
        "ログインしたままにする",
        default=False,
    )


class SignupForm(FlaskForm):
    email = StringField(
        "メールアドレス",
        validators=[Optional(), Email()],
    )
    username = StringField(
        "ユーザー名",
        validators=[
            DataRequired(),
            Regexp(USERNAME_REGEX),
            Length(max=USERNAME_MAX_LENGTH),
        ],
    )
    display_name = StringField(
        "表示名(省略可)",
        validators=[Length(max=DISPLAY_NAME_MAX_LENGTH)],
    )
    password = PasswordField(
        "パスワード",
        validators=[
            DataRequired(),
            Regexp(PASSWORD_REGEX),
            EqualTo("password_confirmation"),
        ],
    )
    password_confirmation = PasswordField(
        "パスワード(確認)",
        validators=[DataRequired(), Regexp(PASSWORD_REGEX)],
    )
    remember_me = BooleanField(
        "ログインしたままにする",
        default=False,
    )
