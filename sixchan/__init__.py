import base64
import hashlib
from datetime import datetime

from flask import Flask, redirect, render_template, request
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional

from sixchan.config import Config
from sixchan.filters import authorformat, datetimeformat, whoformat
from sixchan.models import Res, db

app = Flask(__name__)
app.config.from_object(Config)
csrf = CSRFProtect(app)
db.init_app(app)

app.jinja_env.filters["datetimeformat"] = datetimeformat
app.jinja_env.filters["authorformat"] = authorformat
app.jinja_env.filters["whoformat"] = whoformat


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
