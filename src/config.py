import os

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = os.environ['SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = os.environ['SQL_DATABASE_URI']
    WHOOSH_BASE = 'search_db'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ['SERVER_EMAIL']
    MAIL_PASSWORD = os.environ['SERVER_EMAIL_PW']
    