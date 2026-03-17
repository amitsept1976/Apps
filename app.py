import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import flask_login
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
login_manager = flask_login.LoginManager()


def _normalize_database_uri(database_uri):
    # Render uses postgres:// but SQLAlchemy expects postgresql://
    if database_uri.startswith("postgres://"):
        return database_uri.replace("postgres://", "postgresql://", 1)
    return database_uri


def _configure_app(app):
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-in-prod")
    app.config["SQLALCHEMY_DATABASE_URI"] = _normalize_database_uri(
        os.environ.get("DATABASE_URL", "sqlite:///appointments.db")
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


def _init_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"


def _register_blueprints(app):
    from routes.auth import auth_bp
    from routes.appointments import appointments_bp
    from routes.main import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(main_bp)


def _configure_login_manager():
    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


def create_app():
    app = Flask(__name__)
    _configure_app(app)
    _init_extensions(app)
    _configure_login_manager()
    _register_blueprints(app)

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=False)
