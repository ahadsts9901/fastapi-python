from flask import Blueprint, request, jsonify
from .middleware import jwt_required
from .models import User

users_bp = Blueprint('users', __name__)

# Get all users for chat
@users_bp.route('/users', methods=['GET'])
@jwt_required
def get_all_users():
    try:
        users = User.objects.all()
        return jsonify({
            'message': 'all users fetched',
            'data': [user.to_dict() for user in users]
        }), 200
    
    except Exception as e:
        return jsonify({"message": "internal server error", "error": str(e)}), 500
