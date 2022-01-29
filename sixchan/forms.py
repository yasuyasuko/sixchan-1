from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional


class ResForm(FlaskForm):
    author = StringField("名前(省略可)", validators=[Length(max=20)])
    email = StringField("メールアドレス(省略可)", validators=[Optional(), Email()])
    body = TextAreaField("コメント内容", validators=[DataRequired(), Length(max=1000)])
