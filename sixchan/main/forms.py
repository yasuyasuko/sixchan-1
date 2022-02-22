from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms import StringField
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from wtforms.validators import Email
from wtforms.validators import Length
from wtforms.validators import Optional

from sixchan.config import ANON_NAME_MAX_LENGTH
from sixchan.config import BODY_MAX_LENGTH
from sixchan.config import THREAD_NAME_MAX_LENGTH


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


class FavoriteForm(FlaskForm):
    pass


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


class ReportForm(FlaskForm):
    reason = SelectField("報告理由", coerce=str, validators=[DataRequired()])
    detail = TextAreaField("詳細", validators=[Length(max=BODY_MAX_LENGTH)])
