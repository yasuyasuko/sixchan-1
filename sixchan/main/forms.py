from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional

from sixchan.config import ANON_NAME_MAX_LENGTH, BODY_MAX_LENGTH, THREAD_NAME_MAX_LENGTH


class AnonymousResForm(FlaskForm):
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


class OnymousResForm(FlaskForm):
    body = TextAreaField(
        "コメント内容",
        validators=[DataRequired(), Length(max=BODY_MAX_LENGTH)],
    )


class AnonymousThreadForm(FlaskForm):
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


class OnymousThreadForm(FlaskForm):
    thread_name = StringField(
        "スレッド名",
        validators=[Length(max=THREAD_NAME_MAX_LENGTH)],
    )
    body = TextAreaField(
        "コメント内容",
        validators=[DataRequired(), Length(max=BODY_MAX_LENGTH)],
    )
