from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
limiter = Limiter(get_remote_address)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    Bootstrap5(app)

    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    limiter.init_app(app)

    # Register blueprints
    from app.main.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from app.api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    with app.app_context():
        db.create_all()

    # Custom 429 rate limit error handler
    @app.errorhandler(429)
    def ratelimit_error(e):
        return jsonify({'message': 'Rate limit exceeded! Please try again later.'}), 429

    return app

@login_manager.user_loader
def load_user(user_id):
    from app.main.models import User
    return User.query.get(int(user_id))
