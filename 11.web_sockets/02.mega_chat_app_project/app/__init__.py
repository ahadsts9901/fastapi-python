from fastapi import FastAPI
from mongoengine import connect
from fastapi.middleware.cors import CORSMiddleware
from .auth_routes import router as auth_router
from .users_routes import router as users_router
from .profile_routes import router as profile_router
from .chat_routes import router as chat_router
from config import MONGO_URI

def create_app():
    app = FastAPI()

    # Enable CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],  # Update this to specify allowed origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Connect to MongoDB
    if not MONGO_URI:
        raise ValueError("mongo_uri environment variable not set")
    connect("fastapi_chat_app", host=MONGO_URI)

    # Register routers
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(users_router, prefix="/api/v1")
    app.include_router(profile_router, prefix="/api/v1")
    app.include_router(chat_router, prefix="/api/v1")

    # Initialize Socket.IO
    # socketio_app.mount_asgi_app(app)

    return app
