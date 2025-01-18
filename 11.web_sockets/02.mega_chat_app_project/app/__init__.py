from flask import Flask
from mongoengine import connect
from .auth_routes import auth_bp
from .users_routes import users_bp
from .profile_routes import profile_bp
from .chat_routes import chat_bp
from config import MONGO_URI
from flask_cors import CORS
from extensions import socketio

def create_app():
    app = Flask(__name__)
    CORS(app,supports_credentials=True)

    if not MONGO_URI:
        raise ValueError("mongo_uri environment variable not set")
    connect("flask_chat_app", host=MONGO_URI)

    app.register_blueprint(auth_bp, url_prefix='/api/v1')
    app.register_blueprint(users_bp, url_prefix='/api/v1')
    app.register_blueprint(profile_bp, url_prefix='/api/v1')
    app.register_blueprint(chat_bp, url_prefix='/api/v1')
    socketio.init_app(app)

    return app
