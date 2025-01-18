import os
import cloudinary
import cloudinary.uploader
import jwt
from fastapi import HTTPException, Request, Depends
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
from typing import Callable
from functools import wraps

# Load environment variables
load_dotenv()

# JWT key
JWT_KEY = os.getenv("JWT_KEY")

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

# OAuth2PasswordBearer for FastAPI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Function to upload a profile picture
def upload_profile_picture(file):
    if not file:
        raise HTTPException(status_code=400, detail="File is required")

    try:
        result = cloudinary.uploader.upload(file)
        return {
            "message": "File uploaded successfully",
            "url": result["secure_url"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong: {str(e)}")


# Middleware to require JWT
def jwt_required(request: Request):
    token = request.cookies.get("hart")  # Get token from cookies
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        payload = jwt.decode(token, JWT_KEY, algorithms=["HS256"])
        return payload  # Return decoded token for further processing
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")