import uuid
from datetime import datetime, timezone

import pytz
import shortuuid
from markupsafe import Markup, escape


def authorformat(author, email):
    if not author:
        author = "null"
    else:
        author = escape(author)

    if email:
        html = f'<a href="mailto:{email}" class="text-blue-500">{author}</a>'
    else:
        html = f'<span class="text-green-500">{author}</span>'

    return Markup(html)


def datetimeformat(dt: datetime):
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=timezone.utc)
    dt_jp = dt.astimezone(pytz.timezone("Asia/Tokyo"))
    msec = int(dt_jp.microsecond / 1000)
    html = f'{dt_jp.strftime("%Y/%m/%d(%a) %H:%M:%S")}<span class="text-xs text-gray-300">.{msec:03}</span>'
    return Markup(html)


def whoformat(who):
    return Markup(f"<span title={who}>{who[:10]}</span>")


def uuidshort(uuid: uuid.UUID) -> str:
    return shortuuid.encode(uuid)
