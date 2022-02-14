from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms import StringField
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from wtforms.validators import Email
from wtforms.validators import EqualTo
from wtforms.validators import Length
from wtforms.validators import Regexp

from sixchan.config import DISPLAY_NAME_MAX_LENGTH
from sixchan.config import PASSWORD_REGEX
from sixchan.config import USERNAME_MAX_LENGTH
from sixchan.config import USERNAME_REGEX


class ChangeUsernameForm(FlaskForm):
    username = StringField(
        "ユーザー名",
        validators=[
            DataRequired(),
            Regexp(USERNAME_REGEX),
            Length(max=USERNAME_MAX_LENGTH),
        ],
    )


class ChangeEmailForm(FlaskForm):
    new_email = StringField(
        "新しいメールアドレス",
        validators=[DataRequired(), Email()],
    )


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(
        "現在のパスワード",
        validators=[
            DataRequired(),
            Regexp(PASSWORD_REGEX),
        ],
    )
    new_password = PasswordField(
        "新しいパスワード",
        validators=[
            DataRequired(),
            Regexp(PASSWORD_REGEX),
            EqualTo("new_password_confirmation"),
        ],
    )
    new_password_confirmation = PasswordField(
        "新しいパスワード(確認)",
        validators=[DataRequired(), Regexp(PASSWORD_REGEX)],
    )


class ProfileForm(FlaskForm):
    display_name = StringField(
        "表示名",
        validators=[Length(max=DISPLAY_NAME_MAX_LENGTH)],
    )
    introduction = TextAreaField(
        "自己紹介",
        validators=[Length(max=DISPLAY_NAME_MAX_LENGTH)],
    )
