from datetime import datetime

from flask import Blueprint, abort, redirect, render_template, request, url_for
from flask_login import current_user

from sixchan.main import queries
from sixchan.main.forms import (
    AnonymousResForm,
    AnonymousThreadForm,
    OnymousResForm,
    OnymousThreadForm,
)
from sixchan.models import AnonymousUser, Board, BoardCategory, Thread, db
from sixchan.utils import normalize_uuid_string

main = Blueprint("main", __name__)


@main.get("/")
def index():
    board_categories = BoardCategory.query.all()
    return render_template("index.html", board_categories=board_categories)


@main.route("/boards/<board_id>", methods=["GET", "POST"])
def board(board_id: str):
    try:
        board_uuid = normalize_uuid_string(board_id)
    except ValueError:
        abort(404)

    board = Board.query.get_or_404(board_uuid)

    form = (
        OnymousThreadForm() if current_user.is_authenticated else AnonymousThreadForm()
    )
    if form.validate_on_submit():
        if isinstance(current_user, AnonymousUser):
            current_user.name = form.anon_name.data
            current_user.email = form.anon_email.data
        new_thread = board.post_thread(form.thread_name.data)
        ip = request.environ.get("HTTP_X_REAL_IP", request.remote_addr)
        today_utc = datetime.utcnow().strftime("%Y%m%d")
        new_thread.post_res(
            body=form.body.data, who_seeds=[ip, today_utc], user=current_user
        )
        db.session.commit()
        return redirect(url_for(".board", board_id=board_id, _anchor="thread-form"))

    context = {
        "board": board,
        "form": form,
        "anchor": "thread-form" if form.is_submitted() else None,
    }
    return render_template("main/board.html", **context)


@main.route("/threads/<thread_id>", methods=["GET", "POST"])
def thread(thread_id: str):
    try:
        thread_uuid = normalize_uuid_string(thread_id)
    except ValueError:
        abort(404)

    thread = Thread.query.get_or_404(thread_uuid)

    form = OnymousResForm() if current_user.is_authenticated else AnonymousResForm()
    if form.validate_on_submit():
        if isinstance(current_user, AnonymousUser):
            current_user.name = form.anon_name.data
            current_user.email = form.anon_email.data
        ip = request.environ.get("HTTP_X_REAL_IP", request.remote_addr)
        today_utc = datetime.utcnow().strftime("%Y%m%d")
        thread.post_res(
            body=form.body.data, who_seeds=[ip, today_utc], user=current_user
        )
        db.session.commit()
        return redirect(url_for(".thread", thread_id=thread_id, _anchor="res-form"))

    context = {
        "thread": thread,
        "form": form,
        "anchor": "res-form" if form.is_submitted() else None,
    }
    return render_template("main/thread.html", **context)


@main.get("/users/<username>")
def user(username):
    user_ = queries.get_user(username)
    context = {"user": user_}
    return render_template("main/user.html", **context)
