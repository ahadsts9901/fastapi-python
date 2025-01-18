import requests
import bcrypt
import jwt
from flask import Blueprint, request, jsonify, make_response
from .models import User
from datetime import datetime, timedelta
from config import JWT_KEY,default_profile_picture

auth_bp = Blueprint('auth', __name__)

# Google login route
@auth_bp.route('/google-login', methods=['POST'])
def google_login():
    try:
        data = request.json
        if not data or 'accessToken' not in data:
            return jsonify({'message': 'access token is required'}), 400

        access_token = data['accessToken']
        google_user = requests.get("https://www.googleapis.com/oauth2/v3/userinfo", headers={"Authorization": f"Bearer {access_token}"})

        if google_user.status_code != 200:
            return jsonify({"message": "Failed to fetch user info from Google"}), 500
        else:
            google_user = google_user.json()

        if not all([google_user["name"], google_user["email"], google_user["picture"]]):
            return jsonify({"message": "invalid google user data"}), 400
        
        user = User.objects(email=google_user["email"]).first()

        if not user:
            new_user = User(
                username=google_user["name"],
                email=google_user["email"].lower(),
                profile_picture=google_user["picture"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            new_user.save()

            payload = {
                'id': str(new_user.id),
                'username': new_user.username,
                'email': new_user.email,
                'profile_picture': new_user.profile_picture,
                'created_at': new_user.created_at.isoformat(), 
                'updated_at': new_user.updated_at.isoformat(), 
                'exp': (datetime.utcnow() + timedelta(days=1)).timestamp()
            }

            token = jwt.encode(payload, JWT_KEY, algorithm="HS256")
            response = make_response(jsonify({'message': 'google login successful'}))
            response.set_cookie('hart', token, httponly=True, secure=True,samesite="None")

            return response

        else:
            payload = {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'profile_picture': user.profile_picture,
                'created_at': user.created_at.isoformat(),
                'updated_at': user.updated_at.isoformat(),
                'exp': (datetime.utcnow() + timedelta(days=1)).timestamp()
            }

            token = jwt.encode(payload, JWT_KEY, algorithm="HS256")
            response = make_response(jsonify({'message': 'google login successful'}))
            response.set_cookie('hart', token, httponly=True, secure=True,samesite="None")

            return response

    except Exception as e:
        print(e)
        return jsonify({'message': 'internal server error', "error": str(e)}), 500

# Logout route
@auth_bp.route("/logout", methods=["POST"])
def logout():
    try:
        response = make_response(jsonify({"message": "logout successful"}))
        response.delete_cookie("hart")
        return response
    except Exception as e:
        return jsonify({"message": "internal server error", "error": str(e)}), 500
