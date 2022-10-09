from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_admin import Admin

#pour initialisation de class :instance

db=SQLAlchemy()
migrate=Migrate()
admin=Admin()
mail=Mail()
migrate=Migrate()
jwt=JWTManager()
