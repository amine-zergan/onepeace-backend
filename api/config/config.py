import os
from datetime import timedelta



BASE_DIR=os.path.dirname(os.path.realpath(__file__))
PATH_DB="sqlite:////Users/aminemejri/Desktop/flask/api/tutoriel.db"

class Config:
    SECRET_KEY=os.getenv('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES=timedelta(hours=23)
    JWT_REFRESH_TOKEN_EXPIRES=timedelta(days=2)
    


class DevConfig(Config):
    DEBUG=True
    SQLALCHEMY_ECHO=True
    SQLALCHEMY_DATABASE_URI='sqlite:///'+os.path.join(BASE_DIR,"tutoriel.sqlite3")
    UPLOAD_FOLDER=os.path.join(BASE_DIR,"/upload")
    MAX_CONTENT_LENGTH=16*1000*100
    MAIL_SERVER=os.getenv("MAIL_SERVER")
    MAIL_PORT=os.getenv("MAIL_PORT")
    MAIL_USERNAME= os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD= os.getenv("MAIL_PASSWORD")
    MAIL_USE_TLS=False
    MAIL_USE_SSL=True

class TestConfig(Config):
    pass

class ProdConfig(Config):
    pass


config_dict={
    "dev":DevConfig,
    "prod":ProdConfig,
    "test":TestConfig
}