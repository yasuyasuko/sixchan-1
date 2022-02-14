from typing import Optional

from flask import Flask, flash, redirect, render_template, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
)
from flask_wtf.csrf import CSRFProtect

from sixchan.config import FLASH_LEVEL, FLASH_MESSAGE, Config
from sixchan.email import mail
from sixchan.filters import authorformat, datetimeformat, uuidshort, whoformat
from sixchan.forms import AccountForm
from sixchan.models import (
    AnonymousUser,
    UserAccount,
    db,
)
from sixchan.cli.database import database
from sixchan.cli.dev import dev

app = Flask(__name__)
app.config.from_object(Config)
csrf = CSRFProtect(app)
db.init_app(app)
mail.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = FLASH_MESSAGE.LOGIN_REQUIRED
login_manager.login_message_category = FLASH_LEVEL.ERROR
login_manager.anonymous_user = AnonymousUser
app.add_template_filter(datetimeformat)
app.add_template_filter(authorformat)
app.add_template_filter(whoformat)
app.add_template_filter(uuidshort)
app.jinja_env.globals["get_flash_color"] = FLASH_LEVEL.get_flash_color
app.register_blueprint(database)
app.register_blueprint(dev)


@login_manager.user_loader
def load_user(username: str) -> Optional[UserAccount]:
    return UserAccount.query.filter_by(username=username).first()


if app.config["DEBUG"]:

    @app.get("/debug")
    def debug():
        return "this is a page for debug"


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = AccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.display_name = form.display_name.data
        db.session.commit()
        flash(FLASH_MESSAGE.USER_INFO_UPDATE, FLASH_LEVEL.SUCCESS)
        return redirect(url_for("account"))

    if not form.is_submitted():
        form.username.data = current_user.username
        form.display_name.data = current_user.display_name

    return render_template("account.html", form=form)
