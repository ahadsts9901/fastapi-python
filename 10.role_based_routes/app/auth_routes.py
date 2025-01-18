from fastapi import APIRouter, Body, HTTPException, Form, File, UploadFile
from fastapi.responses import JSONResponse
from .models import User
import bcrypt
import jwt
from datetime import datetime, timedelta
from config import JWT_KEY
from pydantic import BaseModel

auth_router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

# Login route
@auth_router.post("/login")
async def login(data: LoginRequest = Body(...)):

    username = data.username
    password = data.password
    
    user = User.objects(username=username).first()
    if not user or not bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
        raise HTTPException(status_code=400, detail="Username or password is incorrect")

    payload = {
        "id": str(user.id),
        "username": user.username,
        "role": user.role,
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    token = jwt.encode(payload, JWT_KEY, algorithm="HS256")

    response = JSONResponse(
        status_code=200,
        content={"message": "Login successful"}
    )

    # Set the cookie with token
    response.set_cookie(key="hart", value=token, httponly=True)  # Add secure=True if running over HTTPS

    return response

# Signup route
@auth_router.post("/signup")
async def signup(
    username: str = Form(...),
    password: str = Form(...),
    file: UploadFile = File(...),
):
    if User.objects(username=username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # Simulating saving the profile picture, you would actually store the file
    profile_url = "profile_picture_url"

    new_user = User(
        username=username,
        password=hashed_password,
        role="user",  # Default role
        profile_picture=profile_url,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    new_user.save()

    return JSONResponse(
        status_code=200,
        content={"message": "Signup successful"},
    )

# Logout route
@auth_router.post("/logout")
async def logout():
    response = JSONResponse(content={"message": "Logout successful"})
    response.delete_cookie("hart")
    return response
