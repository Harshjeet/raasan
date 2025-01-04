from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize the database
db = SQLAlchemy()

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # App Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Change to your database URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key'  # Change this for security

    # Initialize Extensions
    db.init_app(app)

    # Import and Register Blueprints (Modular structure)
    # from .views import main as main_blueprint
    # from .auth import auth as auth_blueprint
    # from .api import api as api_blueprint

    # app.register_blueprint(main_blueprint)
    # app.register_blueprint(auth_blueprint, url_prefix='/auth')
    # app.register_blueprint(api_blueprint, url_prefix='/api')

    return app
