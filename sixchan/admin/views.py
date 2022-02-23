from functools import wraps
from uuid import UUID

from flask import Blueprint
from flask import abort
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user

from sixchan.admin import queries
from sixchan.admin.forms import PanishForm
from sixchan.config import FLASH_LEVEL as LEVEL
from sixchan.config import FLASH_MESSAGE as MSG
from sixchan.config import REPORT_PER_PAGE
from sixchan.extensions import db
from sixchan.models import Report
from sixchan.models import ReportStatus
from sixchan.models import Res

admin = Blueprint("admin", __name__, url_prefix="/admin")


def moderetor_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_moderator:
            abort(403)
        return f(*args, **kwargs)

    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)

    return wrapper


@admin.get("/report")
@moderetor_required
def report():
    page = request.args.get("page", default=1, type=int)
    pagination = queries.get_reports(page, REPORT_PER_PAGE)
    context = {"pagination": pagination}
    return render_template("admin/report.html", **context)


@admin.route("/panish/<suuid:res_id>", methods=["GET", "POST"])
@moderetor_required
def panish(res_id: UUID):
    page = request.args.get("page", default=1, type=int)
    res = Res.query.get_or_404(res_id)
    pagination = queries.get_reports(page, REPORT_PER_PAGE)
    form = PanishForm()
    if form.validate_on_submit():
        reports = Report.query.filter_by(res_id=res.id).all()
        if form.deal.data == "safe":
            pass
        else:
            res.panish()
        for report in reports:
            report.close()
        db.session.commit()
        return redirect(
            url_for("main.thread", thread_id=res.thread_id, _anchor=f"{res.number}")
        )

    context = {"res": res, "pagination": pagination, "form": form}
    return render_template("admin/panish.html", **context)
