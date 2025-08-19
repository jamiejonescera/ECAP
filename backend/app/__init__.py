from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import db and bcrypt from models
from app.models import db, bcrypt

# Initialize other extensions
jwt = JWTManager()
mail = Mail()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///instance/ecap.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    
    # File upload config
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), '..', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
    
    # Email config
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    
    # Enable CORS
    CORS(app, origins=['http://localhost:3000'])
    
    # Create folders
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('instance', exist_ok=True)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # Create database tables
    with app.app_context():
        # Import models to register them
        from app.models import User
        
        db.create_all()
        
        # Create default admin user
        admin_user = User.query.filter_by(email='admin@ecap.com').first()
        if not admin_user:
            admin_user = User(
                email='admin@ecap.com',
                name='System Administrator',
                position_in_school='Administrator',
                is_admin=True
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user created: admin@ecap.com / admin123")
    
    return app