import base64
import hashlib
from datetime import datetime

from flask import Flask, redirect, render_template, request
from flask_wtf.csrf import CSRFProtect


from sixchan.config import Config
from sixchan.filters import authorformat, datetimeformat, whoformat
from sixchan.models import Res, db
from sixchan.forms import ResForm

app = Flask(__name__)
app.config.from_object(Config)
csrf = CSRFProtect(app)
db.init_app(app)

app.jinja_env.filters["datetimeformat"] = datetimeformat
app.jinja_env.filters["authorformat"] = authorformat
app.jinja_env.filters["whoformat"] = whoformat


def get_b64encoded_digest_string_from_words(*words: list[str]) -> str:
    digest = hashlib.md5("".join(words).encode()).digest()
    return base64.b64encode(digest).decode().strip("=")


@app.route("/", methods=["GET", "POST"])
def index():
    form = ResForm()
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
