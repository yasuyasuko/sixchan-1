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


class FLASH_MESSAGE:
    LOGIN = "ログインしました"
    LOGIN_REQUIRED = "このページにアクセスするためにはログインが必要です"
    LOGOUT = "ログアウトしました"
    AUTHENTICATION_FAILED = "認証に失敗しました"
    USERNAME_ALREADY_EXISTS = "そのユーザー名は既に使われています"
    EMAIL_ALREADY_EXISTS = "そのメールアドレスはすでに使われいます"
    ACTIVATION_LINK_SEND = "確認メールを送信しました。24時間以内にメールからアクティベーションを完了してください"
    ACTIVATION_TOKEN_INVALID = "無効なアクティベーショントークンです"
    ACTIVATION_TOKEN_EXPIRED = "アクティベーショントークンの有効期限が切れています"
    ACTIVATION_ALREADY_DONE = "既にアクティベーション済みです"
    ACTIVATION_COMPLETE = "アクティベーションが完了しました"
    USER_INFO_UPDATE = "ユーザー情報を更新しました"


class Config:
    MAIL_SERVER = "localhost"
    MAIL_PORT = 11025
    MAIL_USERNAME = "sixchan@example.com"
    MAIL_PASSWORD = "password"
    SQLALCHEMY_DATABASE_URI = "postgresql://sixchan:password@localhost:54321/sixchan"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "bazinga"
