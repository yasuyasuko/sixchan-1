from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

login_manager = LoginManager()
mail = Mail()
db = SQLAlchemy()
csrf = CSRFProtect()
