from sixchan.models import Report
from sixchan.utils import Pagination


def get_reports(page: int, per_page: int):
    pagination = Pagination(page, per_page)

    total = Report.query.count()
    if total <= 0:
        return pagination.get_empty_query_model()
    else:
        pagination.total = total
    query = (
        Report.query.order_by(Report.created_at.desc())
        .limit(pagination.limit)
        .offset(pagination.offset)
    )

    items = [row for row in query.all()]
    return pagination.get_query_model(items)
