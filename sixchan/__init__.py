from datetime import datetime, timedelta

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
from sixchan.email import mail, send_email
from sixchan.filters import authorformat, datetimeformat, uuidshort, whoformat
from sixchan.forms import AccountForm, LoginForm, ResForm, SignupForm, ThreadForm
from sixchan.models import ActivationToken, Board, BoardCategory, Res, Thread, User, db
from sixchan.utils import get_b64encoded_digest_string_from_words, normalize_uuid_string

app = Flask(__name__)
app.config.from_object(Config)
csrf = CSRFProtect(app)
db.init_app(app)
mail.init_app(app)
login_manager = LoginManager(app)

app.add_template_filter(datetimeformat)
app.add_template_filter(authorformat)
app.add_template_filter(whoformat)
app.add_template_filter(uuidshort)


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


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash("そのユーザー名は既に使われています")
            return render_template("signup.html", form=form)
        if User.query.filter_by(email=form.email.data).first():
            flash("そのメールアドレスはすでに使われいます")
            return render_template("signup.html", form=form)

        user = User(
            username=form.username.data,
            display_name=form.display_name.data,
            email=form.email.data,
            activated=False,
        )
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()

        token_string = ActivationToken.generate(user, timedelta(days=1))
        send_email(
            user.email,
            "6channel ご本人確認",
            "mail/activate",
            activation_link=f"{request.url_root}activate/{token_string}",
        )
        flash("確認メールを送信しました。24時間以内にメールからアクティベーションを完了してください")
        return redirect("/")

    return render_template("signup.html", form=form)


@app.get("/activate/<token_string>")
def activate(token_string):
    token = ActivationToken.query.get(token_string)
    if not token:
        flash("無効なアクティベーショントークンです")
    if token.expired:
        flash("アクティベーショントークンの有効期限が切れています")
        # TODO: reissue token?
        return redirect("/")

    user = User.query.join(ActivationToken, User.id == ActivationToken.user_id).first()
    if user.activated:
        flash("既にアクティベーション済みです")
        return redirect("/login")
    else:
        user.activated = True
        db.session.commit()
        login_user(user)
        flash("アクティベーションが完了しました")
        return redirect("/")


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = AccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.display_name = form.display_name.data
        db.session.commit()
        flash("ユーザー情報を更新しました")
        return redirect(request.url)
    else:
        form.username.data = current_user.username
        form.display_name.data = current_user.display_name

    return render_template("account.html", form=form)
