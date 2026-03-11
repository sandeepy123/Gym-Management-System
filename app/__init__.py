from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login = LoginManager()
login.login_view = 'auth.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login.init_app(app)

    # Register blueprints (we will create these soon)
    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.routes.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp)

    from app.routes.members import bp as members_bp
    app.register_blueprint(members_bp, url_prefix='/members')

    from app.routes.attendance import bp as attendance_bp
    app.register_blueprint(attendance_bp, url_prefix='/attendance')

    from app.routes.actions import bp as actions_bp
    app.register_blueprint(actions_bp, url_prefix='/actions')

    from app.routes.payments import bp as payments_bp
    app.register_blueprint(payments_bp, url_prefix='/payments')

    return app
