from typing import Optional
from uuid import UUID

from flask import Flask
from flask import abort
from flask import render_template
from sqlalchemy.orm import joinedload
from werkzeug.routing import BaseConverter

from sixchan.config import FLASH_LEVEL
from sixchan.config import FLASH_MESSAGE
from sixchan.config import get_config
from sixchan.extensions import csrf
from sixchan.extensions import db
from sixchan.extensions import login_manager
from sixchan.extensions import mail
from sixchan.main.utils import normalize_uuid_string
from sixchan.models import AnonymousUser
from sixchan.models import UserAccount


def _debug_mode(app: Flask) -> None:
    import logging
    import re
    import sys
    from datetime import datetime

    import sqlparse

    class PrettySQLFormatter(logging.Formatter):
        """For hooking 'sqlalchemy.engine.Engine' logger.
        SQLAlchemy's logs are hard to read, so we will format logs with sqlparse and
        color. We didn't check the detailed specification of sqlalchemy, so I'm not sure
        how it will behave.
        """

        UPPER_WORD_REGEX = re.compile(r"([A-Z]+)")

        def _color_keyword(self, sql):
            # green highlight
            return self.UPPER_WORD_REGEX.sub("\033[32m\\1\033[0m", sql)

        def format(self, record):
            org: str = record.getMessage().replace("\n", "")
            if org.startswith("["):
                return org
            else:
                formatted = sqlparse.format(org, reindent=True, keyword_case="upper")
                colored = self._color_keyword(formatted)
                dt = str(datetime.fromtimestamp(record.created))[:-7]
                # cyan highlight
                head = f"\033[36m{dt} {record.name} {record.levelname}\033[0m"
                return f"{head}\n{colored}"

    # hook 'sqlalchemy.engine.Engine' logger
    sa_logger = logging.getLogger("sqlalchemy.engine.Engine")
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(PrettySQLFormatter())
    sa_logger.addHandler(handler)

    # limited endpoint on debug
    @app.get("/debug")
    def debug():
        return "this is a page for debug"


def create_app() -> Flask:
    # setup flask app
    app = Flask(__name__)
    app.config.from_object(get_config(app.env))

    class ShortUUIDConverter(BaseConverter):
        def to_python(self, value: str) -> UUID:
            try:
                uuid = normalize_uuid_string(value)
            except ValueError:
                abort(404)
            return uuid

    app.url_map.converters["suuid"] = ShortUUIDConverter

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("error/404.html"), 404

    if app.config["DEBUG"]:
        _debug_mode(app)

    # setup extensions
    csrf.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = FLASH_MESSAGE.LOGIN_REQUIRED
    login_manager.login_message_category = FLASH_LEVEL.ERROR
    login_manager.anonymous_user = AnonymousUser

    @login_manager.user_loader
    def load_user(username: str) -> Optional[UserAccount]:
        return (
            UserAccount.query.filter_by(username=username)
            .options(joinedload(UserAccount.profile))
            .first()
        )

    # setup jinja2
    from sixchan.filters import ago_from_now_format
    from sixchan.filters import datetimeformat
    from sixchan.filters import uuidshort
    from sixchan.utils import paginate

    app.add_template_filter(datetimeformat)
    app.add_template_filter(uuidshort)
    app.add_template_filter(ago_from_now_format)
    app.jinja_env.globals["get_flash_color"] = FLASH_LEVEL.get_flash_color
    app.jinja_env.globals["paginate"] = paginate

    # setup blueprints
    from sixchan.admin.views import admin
    from sixchan.auth.views import auth
    from sixchan.cli.database import database
    from sixchan.cli.dev import dev
    from sixchan.main.views import main
    from sixchan.user.views import user

    app.register_blueprint(admin)
    app.register_blueprint(auth)
    app.register_blueprint(database)
    app.register_blueprint(dev)
    app.register_blueprint(main)
    app.register_blueprint(user)

    return app
