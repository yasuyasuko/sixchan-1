from flask import Blueprint, render_template, request

from sixchan.admin import queries
from sixchan.config import REPORT_PER_PAGE

admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.get("/report")
def report():
    page = request.args.get("page", default=1, type=int)
    pagination = queries.get_reports(page, REPORT_PER_PAGE)
    context = {"pagination": pagination}
    return render_template("admin/report.html", **context)
