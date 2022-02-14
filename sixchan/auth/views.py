from datetime import timedelta

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_user, logout_user

from sixchan.config import FLASH_LEVEL, FLASH_MESSAGE
from sixchan.email import send_email
from sixchan.forms import LoginForm, SignupForm
from sixchan.models import ActivationToken, UserAccount, db

auth = Blueprint("auth", __name__, url_prefix="me")


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = UserAccount.query.filter_by(username=form.username.data).first_or_404()
        if not user.activated:
            flash(FLASH_MESSAGE.ACTIVATION_INCOMPLETE, FLASH_LEVEL.ERROR)
            return redirect(url_for("index"))
        if user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash(FLASH_MESSAGE.LOGIN, FLASH_LEVEL.SUCCESS)
            return redirect(url_for("index"))
        else:
            flash(FLASH_MESSAGE.AUTHENTICATION_FAILED, FLASH_LEVEL.ERROR)
    return render_template("user/login.html", form=form)


@auth.get("/logout")
def logout():
    logout_user()
    flash(FLASH_MESSAGE.LOGOUT, FLASH_LEVEL.SUCCESS)
    return redirect(url_for("index"))


@auth.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        if UserAccount.query.filter_by(username=form.username.data).first():
            flash(FLASH_MESSAGE.USERNAME_ALREADY_EXISTS, FLASH_LEVEL.ERROR)
            return render_template("user/signup.html", form=form)
        if UserAccount.query.filter_by(email=form.email.data).first():
            flash(FLASH_MESSAGE.EMAIL_ALREADY_EXISTS, FLASH_LEVEL.ERROR)
            return render_template("user/signup.html", form=form)

        new_user = UserAccount.signup(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            display_name=form.display_name.data,
        )
        token_string = ActivationToken.generate(new_user, timedelta(days=1))
        db.session.commit()
        send_email(
            new_user.email,
            "6channel ご本人確認",
            "mail/activate",
            activation_link=url_for(
                "activate", token_string=token_string, _external=True
            ),
        )
        flash(FLASH_MESSAGE.ACTIVATION_LINK_SEND, FLASH_LEVEL.SUCCESS)
        return redirect(url_for("index"))

    return render_template("user/signup.html", form=form)


@auth.get("/activate/<token_string>")
def activate(token_string: str):
    token = ActivationToken.query.get(token_string)
    if not token:
        flash(FLASH_MESSAGE.ACTIVATION_TOKEN_INVALID, FLASH_LEVEL.ERROR)
        return redirect(url_for("index"))
    if token.expired:
        flash(FLASH_MESSAGE.ACTIVATION_TOKEN_EXPIRED, FLASH_LEVEL.ERROR)
        # TODO: reissue token?
        return redirect(url_for("index"))

    user = UserAccount.query.get(token.user_id)
    if user.activated:
        flash(FLASH_MESSAGE.ACTIVATION_ALREADY_DONE, FLASH_LEVEL.INFO)
        return redirect(url_for(".login"))
    else:
        user.activate()
        db.session.commit()
        login_user(user)
        flash(FLASH_MESSAGE.ACTIVATION_COMPLETE, FLASH_LEVEL.SUCCESS)
        return redirect(url_for("index"))
