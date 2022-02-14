from datetime import timedelta

from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required

from sixchan.config import FLASH_LEVEL as LEVEL
from sixchan.config import FLASH_MESSAGE as MSG
from sixchan.config import THREADS_HISTORY_PER_PAGE
from sixchan.email import send_email
from sixchan.extensions import db
from sixchan.models import ChangeEmailConfiramtionToken
from sixchan.models import UserAccount
from sixchan.user import queries
from sixchan.user.forms import ChangeEmailForm
from sixchan.user.forms import ChangePasswordForm
from sixchan.user.forms import ChangeUsernameForm
from sixchan.user.forms import ProfileForm

user = Blueprint("user", __name__, url_prefix="/me")


@user.route("/account", methods=["GET", "POST"])
@login_required
def account():
    change_username_form = ChangeUsernameForm()
    change_email_form = ChangeEmailForm()
    change_password_form = ChangePasswordForm()

    if change_username_form.validate_on_submit():
        current_user.username = change_username_form.username.data
        db.session.commit()
        flash(MSG.USER_INFO_UPDATE, LEVEL.SUCCESS)
        return redirect(url_for(".account"))

    if not change_username_form.is_submitted():
        change_username_form.username.data = current_user.username

    if change_email_form.validate_on_submit():
        token_string = ChangeEmailConfiramtionToken.generate(
            current_user, timedelta(hours=1), change_email_form.new_email.data
        )
        send_email(
            change_email_form.new_email.data,
            "6channel メールアドレスの変更確認",
            "mail/change_email",
            confirmation_link=url_for(
                "confirm_email", token_string=token_string, _external=True
            ),
        )
        db.session.commit()
        flash(MSG.CHANGE_EMAIL_CONFIRAMTION_LINK_SEND, LEVEL.SUCCESS)
        return redirect(url_for(".account"))

    if change_password_form.validate_on_submit():
        if current_user.verify_password(change_password_form.new_password.data):
            current_user.password = change_password_form.new_password.data
            db.session.commit()
            flash(MSG.CHANGE_PASSWORD_SUCCESS, LEVEL.SUCCESS)
        else:
            flash(MSG.AUTHENTICATION_FAILED, LEVEL.ERROR)
        return redirect(url_for(".account"))

    context = {
        "change_username_form": change_username_form,
        "change_email_form": change_email_form,
        "change_password_form": change_password_form,
    }
    return render_template("user/account.html", **context)


@user.get("/confirm/<token_string>")
def confirm_email(token_string):
    token = ChangeEmailConfiramtionToken.query.get(token_string)
    if not token:
        flash(MSG.CONFIRMATION_TOKEN_INVALID, LEVEL.ERROR)
        return redirect(url_for("main.index"))
    if token.expired:
        flash(MSG.CONFIRMATION_TOKEN_EXPIRED, LEVEL.ERROR)

    account = UserAccount.query.get(token.account_id)
    account.email = token.new_email
    db.session.commit()

    if current_user.is_authencicated:
        flash(MSG.CHANGE_EMAIL_COMPLETE_FOR_LOGIN_USER, LEVEL.SUCCESS)
        return redirect(url_for(".account"))
    else:
        flash(MSG.CHANGE_EMAIL_COMPLETE_FOR_NOTLOGIN_USER, LEVEL.SUCCESS)
        return redirect(url_for("auth.login"))


@user.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.profile.display_name = form.display_name.data
        current_user.profile.introduction = form.introduction.data
        db.session.commit()
        flash(MSG.USER_PROFILE_UPDATE, LEVEL.SUCCESS)
        return redirect(url_for(".profile"))
    if not form.is_submitted():
        form.display_name.data = current_user.profile.display_name
        form.introduction.data = current_user.profile.introduction
    context = {"form": form}
    return render_template("user/profile.html", **context)


@user.get("/history")
@login_required
def history():
    page = request.args.get("page", default=1, type=int)
    pagination = queries.get_threads_pagination(
        current_user, page, THREADS_HISTORY_PER_PAGE
    )
    context = {"pagination": pagination}
    return render_template("user/history.html", **context)
