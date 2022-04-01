from datetime import datetime
from uuid import UUID

from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from sqlalchemy.orm import joinedload

from sixchan.config import FLASH_LEVEL as LEVEL
from sixchan.config import FLASH_MESSAGE as MSG
from sixchan.config import MAX_RESES_PER_THREAD
from sixchan.config import THREADS_PER_PAGE
from sixchan.extensions import db
from sixchan.main import queries
from sixchan.main.forms import AnonymousResForm
from sixchan.main.forms import AnonymousThreadForm
from sixchan.main.forms import FavoriteForm
from sixchan.main.forms import OnymousResForm
from sixchan.main.forms import OnymousThreadForm
from sixchan.main.forms import ReportForm
from sixchan.models import AnonymousUser
from sixchan.models import Board
from sixchan.models import BoardCategory
from sixchan.models import Report
from sixchan.models import ReportReason
from sixchan.models import Thread

main = Blueprint("main", __name__)


@main.get("/")
def index():
    board_categories = BoardCategory.query.options(
        joinedload(BoardCategory.boards)
    ).all()
    return render_template("main/index.html", board_categories=board_categories)


@main.route("/boards/<suuid:board_id>", methods=["GET", "POST"])
def board(board_id: UUID):
    board = Board.query.get_or_404(board_id)
    page = request.args.get("page", default=1, type=int)
    pagination = queries.get_threads_pagination(
        board_id=board_id, page=page, per_page=THREADS_PER_PAGE
    )

    if current_user.is_authenticated:
        form = OnymousThreadForm()
    else:
        form = AnonymousThreadForm()

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
        "pagination": pagination,
        "form": form,
        "anchor": "thread-form" if form.is_submitted() else None,
    }
    return render_template("main/board.html", **context)


@main.route("/threads/<suuid:thread_id>", methods=["GET", "POST"])
def thread(thread_id: UUID):
    thread = Thread.query.get_or_404(thread_id)
    reses = queries.get_reses(thread.id)
    can_post = len(reses) < MAX_RESES_PER_THREAD

    if current_user.is_authenticated:
        res_form = OnymousResForm()
    else:
        res_form = AnonymousResForm()
    favorite_form = FavoriteForm(prefix="favorite")

    if res_form.validate_on_submit():
        if isinstance(current_user, AnonymousUser):
            current_user.name = res_form.anon_name.data
            current_user.email = res_form.anon_email.data
        ip = request.environ.get("HTTP_X_REAL_IP", request.remote_addr)
        today_utc = datetime.utcnow().strftime("%Y%m%d")
        thread.post_res(
            body=res_form.body.data, who_seeds=[ip, today_utc], user=current_user
        )
        db.session.commit()
        return redirect(url_for(".thread", thread_id=thread_id, _anchor="res-form"))

    if favorite_form.validate_on_submit():
        current_user.profile.toggle_favorite(thread)
        db.session.commit()
        return redirect(url_for(".thread", thread_id=thread_id))

    context = {
        "thread": thread,
        "reses": reses,
        "can_post": can_post,
        "res_form": res_form,
        "favorite_form": favorite_form,
        "anchor": "res-form" if res_form.is_submitted() else None,
    }
    return render_template("main/thread.html", **context)


@main.get("/users/<username>")
def user(username):
    user_ = queries.get_user(username)
    context = {"user": user_}
    return render_template("main/user.html", **context)


@main.route("/report/<suuid:res_id>", methods=["GET", "POST"])
def report(res_id: UUID):
    res = queries.get_res(res_id)
    reasons = [(r.name, r.text) for r in ReportReason.query.all()]
    form = ReportForm()
    form.reason.choices = reasons
    if form.validate_on_submit():
        reporter = current_user if current_user.is_authenticated else None
        report = Report(
            reason_name=form.reason.data,
            detail=form.detail.data,
            res_id=res.id,
            reported_by=reporter.id,
        )
        db.session.add(report)
        db.session.commit()
        flash(MSG.REPORT_ACCEPTED, LEVEL.SUCCESS)
        return redirect(request.url)
    context = {"res": res, "form": form}
    return render_template("main/report.html", **context)
