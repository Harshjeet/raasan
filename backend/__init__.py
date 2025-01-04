from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Initialize Flask extensions
db = SQLAlchemy()
jwt = JWTManager()




def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # App Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key'  # Change this for security
    app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Secret key for JWT tokens

    # Initialize Extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)  # Enable CORS for Vue.js frontend

    # Import and Register Blueprints
    from .views import main as main_blueprint
    from .auth import auth as auth_blueprint
    from .api import api as api_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(api_blueprint, url_prefix='/api')

    # Create database tables if not already created
    with app.app_context():
        db.create_all()

    return app
