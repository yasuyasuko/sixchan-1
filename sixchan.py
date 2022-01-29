import base64
import hashlib
import json
from datetime import datetime, timezone

import pytz
from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from markupsafe import Markup, escape
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional


class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://sixchan:password@localhost:54321/sixchan"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "bazinga"


app = Flask(__name__)
app.config.from_object(Config)
csrf = CSRFProtect(app)
db = SQLAlchemy(app)


class Res(db.Model):
    __tablename__ = "reses"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    who = db.Column(db.String(22), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


def insert_mock_reses():
    with open("mockdata.json", encoding="utf-8") as f:
        mock_data = json.load(f)
    for res in mock_data["reses"]:
        created_at = datetime.fromisoformat(res.pop("created_at"))
        db.session.add(Res(created_at=created_at, **res))
    db.session.commit()


@app.template_filter("authorformat")
def authorformat(author, email):
    if not author:
        author = "null"
    else:
        author = escape(author)

    if email:
        html = f'<a href="mailto:{email}" class="text-blue-500">{author}</a>'
    else:
        html = f'<span class="text-green-500">{author}</span>'

    return Markup(html)


@app.template_filter("datetimeformat")
def datetimeformat(dt: datetime):
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=timezone.utc)
    dt_jp = dt.astimezone(pytz.timezone("Asia/Tokyo"))
    msec = int(dt_jp.microsecond / 1000)
    html = f'{dt_jp.strftime("%Y/%m/%d(%a) %H:%M:%S")}<span class="text-xs text-gray-300">.{msec:03}</span>'
    return Markup(html)


@app.template_filter("whoformat")
def whoformat(who):
    return Markup(f"<span title={who}>{who[:10]}</span>")


class ResFrom(FlaskForm):
    author = StringField("名前(省略可)", validators=[Length(max=20)])
    email = StringField("メールアドレス(省略可)", validators=[Optional(), Email()])
    body = TextAreaField("コメント内容", validators=[DataRequired(), Length(max=1000)])


def get_b64encoded_digest_string_from_words(*words: list[str]) -> str:
    digest = hashlib.md5("".join(words).encode()).digest()
    return base64.b64encode(digest).decode().strip("=")


@app.route("/", methods=["GET", "POST"])
def index():
    form = ResFrom()
    if form.validate_on_submit():
        ip = request.environ.get("HTTP_X_REAL_IP", request.remote_addr)
        today_utc = datetime.utcnow().strftime("%Y%m%d")
        res = Res(
            author=form.author.data or None,
            email=form.email.data or None,
            who=get_b64encoded_digest_string_from_words(ip, today_utc),
            body=form.body.data,
        )
        db.session.add(res)
        db.session.commit()
        return redirect("/")

    reses = Res.query.all()
    return render_template("index.html", reses=reses, num_reses=len(reses), form=form)
