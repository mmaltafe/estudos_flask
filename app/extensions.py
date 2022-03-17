from dynaconf import FlaskDynaconf
from flask_admin import Admin
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

db = SQLAlchemy()
mail = Mail()


def init_app(app):
    FlaskDynaconf(app)
    JWTManager(app)
    Admin(app)
    CORS(app)
    db.init_app(app)
    mail.init_app(app)
    Migrate(app, db)

    from app.models import User, Product, Category

    @app.shell_context_processor
    def context_processor():

        return dict(app=app, db=db, User=User, Product=Product, Category=Category)
