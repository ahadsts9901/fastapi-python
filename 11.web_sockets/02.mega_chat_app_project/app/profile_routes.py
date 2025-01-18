from flask import Blueprint, request, jsonify
from .middleware import jwt_required
from .models import User

profile_bp = Blueprint('profile', __name__)

# Get current user profile
@profile_bp.route('/profile', methods=['GET'])
@jwt_required
def get_current_user_profile():
    try:
        user_id = request.current_user['id']
        user = User.objects(id=user_id).first()
        if not user:
            return jsonify({'message': 'user not found'}), 404

        return jsonify({
            'message': 'current user profile fetched',
            'data': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'profile_picture': user.profile_picture,
                'created_at': user.created_at,
                'updated_at': user.updated_at
            }
        }), 200

    except Exception as e:
        return jsonify({"message": "internal server error", "error": str(e)}), 500


# Get dynamic user profile
@profile_bp.route('/profile/<string:user_id>', methods=['GET'])
@jwt_required
def get_dynamic_user_profile(user_id):
    try:
        user = User.objects(id=user_id).first()
        if not user:
            return jsonify({'message': 'user not found'}), 404
    
        return jsonify({
            'message': 'dynamic user profile fetched',
            'data': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'profile_picture': user.profile_picture,
                'created_at': user.created_at,
                'updated_at': user.updated_at
            }
        }), 200

    except Exception as e:
        return jsonify({"message": "internal server error", "error": str(e)}), 500
