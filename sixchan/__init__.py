from datetime import datetime

from flask import Flask, flash, redirect, render_template, request
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_wtf.csrf import CSRFProtect

from sixchan.config import Config
from sixchan.filters import authorformat, datetimeformat, whoformat, uuidshort
from sixchan.forms import LoginForm, ResForm, ThreadForm
from sixchan.models import Board, BoardCategory, Res, Thread, User, db
from sixchan.utils import get_b64encoded_digest_string_from_words, normalize_uuid_string

app = Flask(__name__)
app.config.from_object(Config)
csrf = CSRFProtect(app)
db.init_app(app)
login_manager = LoginManager(app)

app.jinja_env.filters["datetimeformat"] = datetimeformat
app.jinja_env.filters["authorformat"] = authorformat
app.jinja_env.filters["whoformat"] = whoformat
app.jinja_env.filters["uuidshort"] = uuidshort


@login_manager.user_loader
def load_user(username: str):
    return User.query.filter_by(username=username).first()


@app.get("/")
def index():
    board_categories = BoardCategory.query.all()
    return render_template("index.html", board_categories=board_categories)


@app.route("/boards/<board_id>", methods=["GET", "POST"])
def board(board_id):
    board_uuid = normalize_uuid_string(board_id)
    board = Board.query.get(board_uuid)

    form = ThreadForm()
    if form.validate_on_submit():
        thread = Thread(name=form.thread_name.data, board_id=board_uuid)
        ip = request.environ.get("HTTP_X_REAL_IP", request.remote_addr)
        today_utc = datetime.utcnow().strftime("%Y%m%d")
        res = Res(
            number=thread.next_res_number,
            anon_name=form.anon_name.data or None,
            anon_email=form.anon_email.data or None,
            who=get_b64encoded_digest_string_from_words(ip, today_utc),
            body=form.body.data,
        )
        thread.reses.append(res)
        db.session.add(thread)
        db.session.commit()
        return redirect(request.url)

    return render_template("board.html", board=board, form=form)


@app.route("/threads/<thread_id>", methods=["GET", "POST"])
def thread(thread_id):
    thread_uuid = normalize_uuid_string(thread_id)
    thread = Thread.query.get(thread_uuid)

    form = ResForm()
    if form.validate_on_submit():
        ip = request.environ.get("HTTP_X_REAL_IP", request.remote_addr)
        today_utc = datetime.utcnow().strftime("%Y%m%d")
        res = Res(
            number=thread.next_res_number,
            anon_name=form.anon_name.data or None,
            anon_email=form.anon_email.data or None,
            who=get_b64encoded_digest_string_from_words(ip, today_utc),
            body=form.body.data,
        )
        thread.reses.append(res)
        db.session.commit()
        return redirect(request.url)

    return render_template("thread.html", thread=thread, form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash("ログインしました")
            return redirect("/")
        else:
            flash("認証に失敗しました")
    return render_template("login.html", form=form)


@app.get("/logout")
def logout():
    logout_user()
    flash("ログアウトしました")
    return redirect("/")
