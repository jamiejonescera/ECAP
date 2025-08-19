from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models import User
from datetime import datetime

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user by email
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'Login error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration endpoint (for testing - normally admin creates users)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'name', 'position_in_school']
        for field in required_fields:
            if not data or not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create new user
        user = User(
            email=data['email'],
            name=data['name'],
            position_in_school=data['position_in_school'],
            is_admin=False  # Only admin can create other admins
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Registration error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        current_app.logger.error(f'Get current user error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        if not data or not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Verify current password
        if not user.check_password(data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Set new password
        user.set_password(data['new_password'])
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Change password error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500
    

@auth_bp.route('/test', methods=['GET'])
def test():
    """Simple test endpoint"""
    return jsonify({
        'message': 'Backend is working perfectly!', 
        'status': 'success',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@auth_bp.route('/health', methods=['GET'])
def health_check():
    """Comprehensive health check endpoint"""
    try:
        from app.models import db, User
        from sqlalchemy import text
        
        # Test database connection (fixed SQLAlchemy syntax)
        db.session.execute(text('SELECT 1'))
        
        # Test user table access
        user_count = User.query.count()
        
        # Test admin user exists
        admin_exists = User.query.filter_by(is_admin=True).first() is not None
        
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'database': {
                'connection': 'ok',
                'user_count': user_count,
                'admin_exists': admin_exists
            },
            'services': {
                'authentication': 'ok',
                'user_management': 'ok'
            }
        }
        
        return jsonify(health_status), 200
        
    except Exception as e:
        error_status = {
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e),
            'database': {
                'connection': 'failed'
            }
        }
        return jsonify(error_status), 500