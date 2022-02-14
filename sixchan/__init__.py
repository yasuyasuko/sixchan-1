from datetime import datetime
from typing import Optional

from flask import Flask, abort, flash, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
)
from flask_wtf.csrf import CSRFProtect

from sixchan.config import FLASH_LEVEL, FLASH_MESSAGE, Config
from sixchan.email import mail
from sixchan.filters import authorformat, datetimeformat, uuidshort, whoformat
from sixchan.forms import AccountForm, ResForm, ThreadForm
from sixchan.models import (
    AnonymousUser,
    Board,
    BoardCategory,
    Thread,
    UserAccount,
    db,
)
from sixchan.utils import normalize_uuid_string
from sixchan.cli.database import database
from sixchan.cli.dev import dev

app = Flask(__name__)
app.config.from_object(Config)
csrf = CSRFProtect(app)
db.init_app(app)
mail.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = FLASH_MESSAGE.LOGIN_REQUIRED
login_manager.login_message_category = FLASH_LEVEL.ERROR
login_manager.anonymous_user = AnonymousUser
app.add_template_filter(datetimeformat)
app.add_template_filter(authorformat)
app.add_template_filter(whoformat)
app.add_template_filter(uuidshort)
app.jinja_env.globals["get_flash_color"] = FLASH_LEVEL.get_flash_color
app.register_blueprint(database)
app.register_blueprint(dev)


@login_manager.user_loader
def load_user(username: str) -> Optional[UserAccount]:
    return UserAccount.query.filter_by(username=username).first()


if app.config["DEBUG"]:

    @app.get("/debug")
    def debug():
        return "this is a page for debug"


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@app.get("/")
def index():
    board_categories = BoardCategory.query.all()
    return render_template("index.html", board_categories=board_categories)


@app.route("/boards/<board_id>", methods=["GET", "POST"])
def board(board_id: str):
    try:
        board_uuid = normalize_uuid_string(board_id)
    except ValueError:
        abort(404)

    board = Board.query.get_or_404(board_uuid)

    form = ThreadForm()
    if form.validate_on_submit():
        new_thread = board.post_thread(form.thread_name.data)
        ip = request.environ.get("HTTP_X_REAL_IP", request.remote_addr)
        today_utc = datetime.utcnow().strftime("%Y%m%d")
        new_thread.post_res(
            body=form.body.data,
            who_seeds=[ip, today_utc],
            anon_name=form.anon_name.data,
            anon_email=form.anon_email.data,
        )
        db.session.commit()
        return redirect(url_for("board", board_id=board_id, _anchor="thread-form"))

    anchor = "thread-form" if form.is_submitted() else None
    return render_template("board.html", board=board, form=form, anchor=anchor)


@app.route("/threads/<thread_id>", methods=["GET", "POST"])
def thread(thread_id: str):
    try:
        thread_uuid = normalize_uuid_string(thread_id)
    except ValueError:
        abort(404)

    thread = Thread.query.get_or_404(thread_uuid)

    form = ResForm()
    if form.validate_on_submit():
        ip = request.environ.get("HTTP_X_REAL_IP", request.remote_addr)
        today_utc = datetime.utcnow().strftime("%Y%m%d")
        thread.post_res(
            body=form.body.data,
            who_seeds=[ip, today_utc],
            anon_name=form.anon_name.data,
            anon_email=form.anon_email.data,
        )
        db.session.commit()
        return redirect(url_for("thread", thread_id=thread_id, _anchor="res-form"))

    anchor = "res-form" if form.is_submitted() else None
    return render_template("thread.html", thread=thread, form=form, anchor=anchor)


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = AccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.display_name = form.display_name.data
        db.session.commit()
        flash(FLASH_MESSAGE.USER_INFO_UPDATE, FLASH_LEVEL.SUCCESS)
        return redirect(url_for("account"))

    if not form.is_submitted():
        form.username.data = current_user.username
        form.display_name.data = current_user.display_name

    return render_template("account.html", form=form)
