import socket

from pydantic import BaseSettings, Field


class CloudFlareSettings(BaseSettings):
    EMAIL: str = Field(..., env="CLOUDFLARE_EMAIL")
    TOKEN: str = Field(..., env="CLOUDFLARE_TOKEN")
    X_CLIENT_SECRET_TOKEN: str = Field(..., env="CLIENT_SECRET")

    class Config:
        case_sensitive = True
        env_file = '.env.development'
        env_file_encoding = 'utf-8'


class MySQLSettings(BaseSettings):
    PRODUCTION_DB: str = Field(..., env="production_sql_db")
    DEVELOPMENT_DB: str = Field(..., env="dev_sql_db")

    class Config:
        env_file = '.env.development'
        env_file_encoding = 'utf-8'


class Logging(BaseSettings):
    filename: str = Field(default="rental.logs")

    class Config:
        env_file = '.env.development'
        env_file_encoding = 'utf-8'


class ResendSettings(BaseSettings):
    API_KEY: str = Field(..., env="RESEND_API_KEY")
    from_: str = Field(default="norespond@zwavhudivhudi-electrical.work")

    class Config:
        env_file = '.env.development'
        env_file_encoding = 'utf-8'


class EmailSettings(BaseSettings):
    RESEND: ResendSettings = ResendSettings()
    COMPANY_ADMIN_EMAIL: str = Field(default="pfunzo@zwavhudivhudi-electrical.work")
    SYSTEM_ADMIN_EMAIL: str = Field(default="email@zwavhudivhudi-electrical.work")

    class Config:
        env_file = '.env.development'
        env_file_encoding = 'utf-8'


class PayPalSettings(BaseSettings):
    CLIENT_ID: str = Field(..., env="PAYPAL_API_CLIENT_ID")
    SECRET_KEY: str = Field(..., env="PAYPAL_SECRET_KEY")

    class Config:
        env_file = '.env.development'
        env_file_encoding = 'utf-8'

class BrainTreeSettings(BaseSettings):
    MERCHANT_ID: str = Field(..., env='BRAIN_TREE_MERCHANT_ID')
    PUBLIC_KEY: str = Field(..., env='BRAIN_TREE_PUBLIC_KEY')
    PRIVATE_KEY: str = Field(..., env='BRAIN_TREE_PRIVATE_KEY')

    class Config:
        env_file = '.env.development'
        env_file_encoding = 'utf-8'


class Settings(BaseSettings):
    APP_NAME: str = Field(default='Last Base')
    LOGO_URL: str = Field(default="https://zwavhudivhudi-electrical.work/static/images/custom/logo.png")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    CLIENT_SECRET: str = Field(..., env="CLIENT_SECRET")
    MYSQL_SETTINGS: MySQLSettings = MySQLSettings()
    CLOUDFLARE_SETTINGS: CloudFlareSettings = CloudFlareSettings()
    EMAIL_SETTINGS: EmailSettings = EmailSettings()
    DEVELOPMENT_SERVER_NAME: str = Field(default="DESKTOP-T9V7F59")
    LOGGING: Logging = Logging()
    HOST_ADDRESSES: str = Field(..., env='HOST_ADDRESSES')
    PAY_FAST_SECRET_KEY: str = Field(..., env="PAYFAST_SECRET_KEY")
    FLUTTERWAVE_SECRET_ID: str = Field(..., env="FLUTTERWAVE_SECRET_ID")
    FLUTTERWAVE_FLW_SECRET_KEY: str = Field(..., env="FLUTTERWAVE_SECRET_KEY")
    FLUTTERWAVE_HASH: str = Field(..., env="FLUTTERWAVE_HASH")
    PAYPAL_SETTINGS: PayPalSettings = PayPalSettings()
    ADMIN_EMAIL: str = "admin@last-shelter.vip"
    AUTH_CODE: str = "pfunzo@zwavhudivhudi-electrical.work"



    class Config:
        env_file = '.env.development'
        env_file_encoding = 'utf-8'


def config_instance() -> Settings:
    """
    :return:
    """
    return Settings()


def is_development():
    return socket.gethostname() == config_instance().DEVELOPMENT_SERVER_NAME
