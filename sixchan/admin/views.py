from functools import wraps

from flask import Blueprint
from flask import abort
from flask import render_template
from flask import request
from flask_login import current_user

from sixchan.admin import queries
from sixchan.config import REPORT_PER_PAGE

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
