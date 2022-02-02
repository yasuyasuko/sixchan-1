ANON_NAME_MAX_LENGTH = 50
DISPLAY_NAME_MAX_LENGTH = 50
USERNAME_MAX_LENGTH = 15
USERNAME_REGEX = r"^\w+$"
EMAIL_MAX_LENGTH = 255
PASSWORD_REGEX = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"

BOARD_NAME_MAX_LENGTH = 30
BOARD_CATEGORY_NAME_MAX_LENGTH = 30
THREAD_NAME_MAX_LENGTH = 100
BODY_MAX_LENGTH = 1000


class Config:
    MAIL_SERVER = "localhost"
    MAIL_PORT = 11025
    MAIL_USERNAME = "sixchan@example.com"
    MAIL_PASSWORD = "password"
    SQLALCHEMY_DATABASE_URI = "postgresql://sixchan:password@localhost:54321/sixchan"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "bazinga"
