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


class FLASH_LEVEL:
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"

    INFO_COLOR = "#3b82f6"
    SUCCESS_COLOR = "#22c55e"
    WARNING_COLOR = "#eab308"
    ERROR_COLOR = "#ef4444"
    UNKNOWN_COLOR = "#6b7280"

    @staticmethod
    def get_flash_color(level: str) -> str:
        colors = {
            FLASH_LEVEL.INFO: FLASH_LEVEL.INFO_COLOR,
            FLASH_LEVEL.SUCCESS: FLASH_LEVEL.SUCCESS_COLOR,
            FLASH_LEVEL.WARNING: FLASH_LEVEL.WARNING_COLOR,
            FLASH_LEVEL.ERROR: FLASH_LEVEL.ERROR_COLOR,
        }
        return colors.get(level, FLASH_LEVEL.UNKNOWN_COLOR)


class Config:
    MAIL_SERVER = "localhost"
    MAIL_PORT = 11025
    MAIL_USERNAME = "sixchan@example.com"
    MAIL_PASSWORD = "password"
    SQLALCHEMY_DATABASE_URI = "postgresql://sixchan:password@localhost:54321/sixchan"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "bazinga"
