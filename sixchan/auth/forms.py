from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, Regexp

from sixchan.config import (
    DISPLAY_NAME_MAX_LENGTH,
    PASSWORD_REGEX,
    USERNAME_MAX_LENGTH,
    USERNAME_REGEX,
)


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
