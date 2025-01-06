from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from .models import User, UserRole,db

# Initialize Flask extensions

jwt = JWTManager()
migrate = Migrate()
def create_admin():
    with db.session.begin():
        existing_admin = User.query.filter_by(role = UserRole.ADMIN).first()
        if not existing_admin:
            admin = User(
                email = "admin@email.com",
                name = "AdminName",
                password = "password",
                role = UserRole.ADMIN
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin created")
        else:
            print("Admin already exists")

def create_app():
    app = Flask(__name__)

    # App Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'djski32jfdskjfsa0kf'  
    app.config['JWT_SECRET_KEY'] = 'KDS73JD9WKU0EKSNFO0DMS'  

    # Initialize Extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app)  # Enable CORS for Vue.js frontend

    # Import and Register Blueprints
    from .views import main as main_blueprint
    from .auth import auth as auth_blueprint
    from .api import api as api_blueprint
    from .admin import admin as admin_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(api_blueprint, url_prefix='/api')
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    # Create database tables if not already created
    with app.app_context():
        db.create_all()
        create_admin()
    return app
