import uuid
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from zoneinfo import ZoneInfo

import humanize
import shortuuid
from markupsafe import Markup

ASIA_TOKYO_ZONEINFO = ZoneInfo("Asia/Tokyo")


def datetimeformat(dt: datetime) -> Markup:
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=timezone.utc)
    dt_jp = dt.astimezone(ASIA_TOKYO_ZONEINFO)
    return dt_jp.strftime("%Y/%m/%d(%a) %H:%M:%S.%f")


def uuidshort(uuid: uuid.UUID) -> str:
    return shortuuid.encode(uuid)


def agoformat(delta: timedelta):
    if delta.days > 0 or delta.seconds > 0:
        humanize.i18n.activate("ja_JP")
        humanized = humanize.naturaldelta(delta)
        humanized = humanized.replace("years", "年")
        humanized = humanized.replace("year", "年")
        return humanized + "前"
    elif delta.microseconds == 0:
        return "0秒前"
    else:
        # "0:00:00.000230" → '0.00023秒前'
        return str(delta)[6:].rstrip("0") + "秒前"


def ago_from_now_format(dt: datetime):
    delta = datetime.utcnow() - dt
    return agoformat(delta)
