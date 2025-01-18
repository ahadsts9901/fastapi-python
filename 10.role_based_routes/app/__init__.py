from fastapi import FastAPI
from mongoengine import connect
from .auth_routes import auth_router
from .user_routes import user_router
from .admin_routes import admin_router
from config import MONGO_URI

def create_app():
    app = FastAPI()

    if not MONGO_URI:
        raise ValueError("mongo_uri environment variable not set")

    # Connect to MongoDB
    connect("roles_fastapi_schema", host=MONGO_URI)

    # Include routers for different routes
    app.include_router(auth_router, prefix="/api/v1/auth")
    app.include_router(user_router, prefix="/api/v1/user")
    app.include_router(admin_router, prefix="/api/v1/admin")

    return app
