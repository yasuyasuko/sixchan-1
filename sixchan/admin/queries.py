from sixchan.models import Report
from sixchan.models import ReportReason
from sixchan.models import Res
from sixchan.utils import Pagination


class ReportQueryModel:
    pass


def get_reports(page: int, per_page: int):
    pagination = Pagination(page, per_page)

    total = Report.query.count()
    if total <= 0:
        return pagination.get_empty_query_model()
    else:
        pagination.total = total
    query = (
        Report.query.join(ReportReason)
        .join(Res)
        .with_entities(
            Report.id,
            Report.detail,
            Report.status,
            Report.res_id,
            Report.reported_by,
            Report.created_at,
            ReportReason.text.label("reason_text"),
            Res.body.label("res_body"),
            Res.thread_id,
            Res.number.label("res_number"),
        )
        .order_by(Report.created_at.desc())
        .limit(pagination.limit)
        .offset(pagination.offset)
    )

    items = [row for row in query.all()]
    return pagination.get_query_model(items)
