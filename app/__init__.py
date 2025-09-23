# app/__init__.py
from flask import Flask
from config import Config
from .extensions import db, migrate

# Import Blueprints
from .routes.auth import auth_bp
from .routes.user import user_bp
from .routes.role import role_bp   # ✅ NEW
from .routes.main import main_bp  


def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(role_bp, url_prefix="/role")   # ✅ NEW
    app.register_blueprint(main_bp)
   
    return app

