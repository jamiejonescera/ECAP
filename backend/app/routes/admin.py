from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User
from datetime import datetime
import secrets
import string

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to require admin privileges"""
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def generate_password(length=12):
    """Generate a random password"""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_all_users():
    """Get all users (admin only)"""
    try:
        users = User.query.all()
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'Get users error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/users', methods=['POST'])
@jwt_required()
@admin_required
def create_user():
    """Create a new user (admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'name', 'position_in_school']
        for field in required_fields:
            if not data or not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 409
        
        # Generate password if not provided
        password = data.get('password') or generate_password()
        
        # Create new user
        user = User(
            email=data['email'],
            name=data['name'],
            position_in_school=data['position_in_school'],
            is_admin=data.get('is_admin', False)
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        response_data = user.to_dict()
        response_data['generated_password'] = password  # Include in response for admin
        
        return jsonify({
            'message': 'User created successfully',
            'user': response_data
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Create user error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_user(user_id):
    """Get specific user (admin only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        current_app.logger.error(f'Get user error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_user(user_id):
    """Update user (admin only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'name' in data:
            user.name = data['name']
        if 'position_in_school' in data:
            user.position_in_school = data['position_in_school']
        if 'is_admin' in data:
            user.is_admin = data['is_admin']
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        # Update password if provided
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Update user error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(user_id):
    """Delete user (admin only)"""
    try:
        # Prevent admin from deleting themselves
        current_user_id = get_jwt_identity()
        if current_user_id == user_id:
            return jsonify({'error': 'Cannot delete your own account'}), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Delete user error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@jwt_required()
@admin_required
def reset_user_password(user_id):
    """Reset user password (admin only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Generate new password
        new_password = generate_password()
        user.set_password(new_password)
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Password reset successfully',
            'new_password': new_password
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Reset password error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500