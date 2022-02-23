from flask_wtf import FlaskForm
from wtforms import RadioField


class PanishForm(FlaskForm):
    deal = RadioField("対応", choices=[("safe", "セーフ"), ("out", "不適切")], default="out")
