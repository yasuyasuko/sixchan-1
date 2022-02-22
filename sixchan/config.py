import os
from abc import ABC
from typing import Optional

ANON_NAME_MAX_LENGTH = 50
BOARD_CATEGORY_NAME_MAX_LENGTH = 30
BOARD_NAME_MAX_LENGTH = 30
THREAD_NAME_MAX_LENGTH = 100
BODY_MAX_LENGTH = 1000
MAX_RESES_PER_THREAD = 1000
REPORT_REASON_NAME_MAX_LENGTH = 32
REPORT_REASON_TEXT_MAX_LENGTH = 64

EMAIL_MAX_LENGTH = 255
USERNAME_MAX_LENGTH = 15
USERNAME_REGEX = r"^\w+$"
PASSWORD_REGEX = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
DISPLAY_NAME_MAX_LENGTH = 50

THREADS_HISTORY_PER_PAGE = 5
THREADS_PER_PAGE = 15

ROLE_GENERAL = "general"
ROLE_MODERATOR = "moderator"
ROLE_ADMINISTRATOR = "administrator"

REPORT_STATUS_OPEN = "open"
REPORT_STATUS_CLOSE = "close"

INAPPROPRIATE_RES_BODY = "あぼーん"


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
    ACTIVATION_ALREADY_DONE = "既にアクティベーション済みです"
    ACTIVATION_COMPLETE = "アクティベーションが完了しました"
    ACTIVATION_INCOMPLETE = "アクティベーションが完了していません"
    ACTIVATION_LINK_SEND = "確認メールを送信しました。24時間以内にメールからアクティベーションを完了してください"
    ACTIVATION_TOKEN_EXPIRED = "アクティベーショントークンの有効期限が切れています"
    ACTIVATION_TOKEN_INVALID = "無効なアクティベーショントークンです"
    AUTHENTICATION_FAILED = "認証に失敗しました"
    CHANGE_EMAIL_COMPLETE_FOR_LOGIN_USER = "メールアドレスの変更が完了しました"
    CHANGE_EMAIL_COMPLETE_FOR_NOTLOGIN_USER = "メールアドレスの変更が完了しました。ログインし直してください"
    CHANGE_EMAIL_CONFIRAMTION_LINK_SEND = "確認メールを送信しました。1時間以内にメールから確認完了してください"
    CHANGE_PASSWORD_SUCCESS = "パスワードが変更されました"
    CONFIRMATION_TOKEN_EXPIRED = "確認トークンの有効期限が切れています。もう１度変更からやり直してください"
    CONFIRMATION_TOKEN_INVALID = "無効な確認トークンです"
    EMAIL_ALREADY_EXISTS = "そのメールアドレスはすでに使われいます"
    LOGIN = "ログインしました"
    LOGIN_REQUIRED = "このページにアクセスするためにはログインが必要です"
    LOGOUT = "ログアウトしました"
    USER_DOESNT_EXIST = "ユーザーが存在しません"
    USER_INFO_UPDATE = "ユーザー情報を更新しました"
    USER_PROFILE_UPDATE = "プロフィールを更新しました"
    USERNAME_ALREADY_EXISTS = "そのユーザー名は既に使われています"
    REPORT_ACCEPTED = "ご協力ありがとうございます。報告を受け付けました"


class Config(ABC):
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DATABASE_DIALECT: str
    DATABASE_USERNAME: Optional[str]
    DATABASE_PASSWORD: Optional[str]
    DATABASE_HOST: Optional[str]
    DATABASE_PORT: Optional[int]
    DATABASE_NAME: str

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.DATABASE_DIALECT == "sqlite":
            uri = f"sqlite:///{self.DATABASE_NAME}"
        else:
            uri = (
                f"{self.DATABASE_DIALECT}://"
                f"{self.DATABASE_USERNAME}:{self.DATABASE_PASSWORD}"
                f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}"
                f"/{self.DATABASE_NAME}"
            )
        return uri


class ProductionConfig(Config):
    SECRET_KEY = os.environ.get("SECRET_KEY")
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = os.environ.get("MAIL_PORT")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    DATABASE_DIALECT = os.environ.get("DATABASE_DIALECT", "postgresql")
    DATABASE_USERNAME = os.environ.get("DATABASE_USERNAME")
    DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
    DATABASE_HOST = os.environ.get("DATABASE_HOST")
    DATABASE_PORT = int(os.environ.get("DATABASE_PORT", "5432"))
    DATABASE_NAME = os.environ.get("DATABASE_NAME", "sixchan")


class DevelopmentConfig(Config):
    SECRET_KEY = "bazinga"
    MAIL_SERVER = "localhost"
    MAIL_PORT = 11025
    MAIL_USERNAME = "sixchan@example.com"
    MAIL_PASSWORD = "password"
    DATABASE_DIALECT = "postgresql"
    DATABASE_USERNAME = "sixchan"
    DATABASE_PASSWORD = "password"
    DATABASE_HOST = "localhost"
    DATABASE_PORT = 54321
    DATABASE_NAME = "sixchan"
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = "bazinga"
    MAIL_SERVER = "localhost"
    MAIL_PORT = 11025
    MAIL_USERNAME = "sixchan@example.com"
    MAIL_PASSWORD = "password"
    DATABASE_DIALECT = "sqlite"
    DATABASE_NAME = ":memory:"


def get_config(env: str) -> Config:
    env = env.lower()
    configs = {
        "production": ProductionConfig(),
        "development": DevelopmentConfig(),
        "testing": TestingConfig(),
    }
    return configs.get(env, DevelopmentConfig())
