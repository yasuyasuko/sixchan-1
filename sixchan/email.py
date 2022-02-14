from threading import Thread

from flask import current_app, render_template
from flask_mail import Message

from sixchan.extensions import mail


def send_async_email(app, msg: Message) -> None:
    with app.app_context():
        mail.send(msg)


def send_email(to: str, subject: str, template: str, **kwargs) -> Thread:
    app = current_app._get_current_object()
    msg = Message(subject, sender=app.config["MAIL_USERNAME"], recipients=[to])
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
