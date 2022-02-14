from datetime import datetime, timedelta
from typing import Optional

from flask import Flask, abort, flash, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_wtf.csrf import CSRFProtect

from sixchan.config import FLASH_LEVEL, FLASH_MESSAGE, Config
from sixchan.email import mail, send_email
from sixchan.filters import authorformat, datetimeformat, uuidshort, whoformat
from sixchan.forms import AccountForm, LoginForm, ResForm, SignupForm, ThreadForm
from sixchan.models import (
    ActivationToken,
    AnonymousUser,
    Board,
    BoardCategory,
    Thread,
    UserAccount,
    db,
)
from sixchan.utils import normalize_uuid_string
from sixchan.cli import database

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


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = UserAccount.query.filter_by(username=form.username.data).first_or_404()
        if not user.activated:
            flash(FLASH_MESSAGE.ACTIVATION_INCOMPLETE, FLASH_LEVEL.ERROR)
            return redirect(url_for("index"))
        if user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash(FLASH_MESSAGE.LOGIN, FLASH_LEVEL.SUCCESS)
            return redirect(url_for("index"))
        else:
            flash(FLASH_MESSAGE.AUTHENTICATION_FAILED, FLASH_LEVEL.ERROR)
    return render_template("login.html", form=form)


@app.get("/logout")
def logout():
    logout_user()
    flash(FLASH_MESSAGE.LOGOUT, FLASH_LEVEL.SUCCESS)
    return redirect(url_for("index"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        if UserAccount.query.filter_by(username=form.username.data).first():
            flash(FLASH_MESSAGE.USERNAME_ALREADY_EXISTS, FLASH_LEVEL.ERROR)
            return render_template("signup.html", form=form)
        if UserAccount.query.filter_by(email=form.email.data).first():
            flash(FLASH_MESSAGE.EMAIL_ALREADY_EXISTS, FLASH_LEVEL.ERROR)
            return render_template("signup.html", form=form)

        new_user = UserAccount.signup(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            display_name=form.display_name.data,
        )
        token_string = ActivationToken.generate(new_user, timedelta(days=1))
        db.session.commit()
        send_email(
            new_user.email,
            "6channel ご本人確認",
            "mail/activate",
            activation_link=url_for(
                "activate", token_string=token_string, _external=True
            ),
        )
        flash(FLASH_MESSAGE.ACTIVATION_LINK_SEND, FLASH_LEVEL.SUCCESS)
        return redirect(url_for("index"))

    return render_template("signup.html", form=form)


@app.get("/activate/<token_string>")
def activate(token_string: str):
    token = ActivationToken.query.get(token_string)
    if not token:
        flash(FLASH_MESSAGE.ACTIVATION_TOKEN_INVALID, FLASH_LEVEL.ERROR)
        return redirect(url_for("index"))
    if token.expired:
        flash(FLASH_MESSAGE.ACTIVATION_TOKEN_EXPIRED, FLASH_LEVEL.ERROR)
        # TODO: reissue token?
        return redirect(url_for("index"))

    user = UserAccount.query.get(token.user_id)
    if user.activated:
        flash(FLASH_MESSAGE.ACTIVATION_ALREADY_DONE, FLASH_LEVEL.INFO)
        return redirect(url_for("login"))
    else:
        user.activate()
        db.session.commit()
        login_user(user)
        flash(FLASH_MESSAGE.ACTIVATION_COMPLETE, FLASH_LEVEL.SUCCESS)
        return redirect(url_for("index"))


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
