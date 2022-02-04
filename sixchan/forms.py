from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, Regexp

from sixchan.config import (
    ANON_NAME_MAX_LENGTH,
    BODY_MAX_LENGTH,
    DISPLAY_NAME_MAX_LENGTH,
    PASSWORD_REGEX,
    THREAD_NAME_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
    USERNAME_REGEX,
)


class ResForm(FlaskForm):
    anon_name = StringField(
        "名前(省略可)",
        validators=[Length(max=ANON_NAME_MAX_LENGTH)],
    )
    anon_email = StringField(
        "メールアドレス(省略可)",
        validators=[Optional(), Email()],
    )
    body = TextAreaField(
        "コメント内容",
        validators=[DataRequired(), Length(max=BODY_MAX_LENGTH)],
    )


class ThreadForm(FlaskForm):
    thread_name = StringField(
        "スレッド名",
        validators=[Length(max=THREAD_NAME_MAX_LENGTH)],
    )
    anon_name = StringField(
        "名前(省略可)",
        validators=[Length(max=ANON_NAME_MAX_LENGTH)],
    )
    anon_email = StringField(
        "メールアドレス(省略可)",
        validators=[Optional(), Email()],
    )
    body = TextAreaField(
        "コメント内容",
        validators=[DataRequired(), Length(max=BODY_MAX_LENGTH)],
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


class AccountForm(FlaskForm):
    username = StringField(
        "ユーザー名",
        validators=[
            DataRequired(),
            Regexp(USERNAME_REGEX),
            Length(max=USERNAME_MAX_LENGTH),
        ],
    )
    display_name = StringField(
        "表示名",
        validators=[Length(max=DISPLAY_NAME_MAX_LENGTH)],
    )
