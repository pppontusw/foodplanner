import logging
from logging.handlers import RotatingFileHandler
import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_cors import CORS
from config import Config

bootstrap = Bootstrap()
db = SQLAlchemy()
login = LoginManager()
login.login_view = "auth.login"
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    CORS(app, supports_credentials=True)

    from app.errors import bp as errors_bp

    app.register_blueprint(errors_bp)
    from app.api import bp as api_bp

    app.register_blueprint(api_bp, url_prefix="/api")
    from app import models

    if not app.debug and not app.testing:

        with app.app_context():
            app.config["ADMINS"] = [
                i.email
                for i in models.User.query.filter(models.User.is_admin).all()
            ]

        if not os.path.exists("logs"):
            os.mkdir("logs")
        file_handler = RotatingFileHandler(
            "logs/app.log", maxBytes=10240, backupCount=10
        )
        formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info("App starting")

    return app
