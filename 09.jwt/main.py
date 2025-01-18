import os
from fastapi import FastAPI, HTTPException, Depends, Request, Form, File, UploadFile, Response
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from datetime import datetime, timedelta
import bcrypt
import jwt
from mongoengine import connect, Document, StringField, DateTimeField
from dotenv import load_dotenv
from functions import upload_profile_picture, jwt_required

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# JWT secret key
JWT_KEY = os.getenv("JWT_KEY")

# Connect to MongoDB
mongo_url = os.getenv("MONGO_URI")
if not mongo_url:
    raise ValueError("MONGO_URI environment variable not set")
connect("jwt_fastapi_python", host=mongo_url)

# MongoDB User schema
class User(Document):
    username = StringField(required=True, unique=True)
    password = StringField(required=True)
    profile_picture = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": str(self.id),
            "username": self.username,
            "profile_picture": self.profile_picture,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

# api model
class LoginRequest(BaseModel):
    username: str
    password: str


# Helper function to decode JWT
def decode_jwt(token: str):
    try:
        payload = jwt.decode(token, JWT_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# OAuth2PasswordBearer for FastAPI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Login route
@app.post("/api/v1/login")
async def login(data: LoginRequest):
    user = User.objects(username=data.username).first()
    if not user or not bcrypt.checkpw(data.password.encode("utf-8"), user.password.encode("utf-8")):
        raise HTTPException(status_code=400, detail="Username or password is incorrect")

    payload = {
        "id": str(user.id),
        "username": user.username,
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
@app.post("/api/v1/signup")
async def signup(
    username: str = Form(...),
    password: str = Form(...),
    file: UploadFile = File(...),
):
    if User.objects(username=username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    profile_url = upload_profile_picture(file.file)

    new_user = User(
        username=username,
        password=hashed_password,
        profile_picture=profile_url["url"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    new_user.save()

    return JSONResponse(
        status_code=200,
        content={"message": "Signup successful"},
    )

# Logout route
@app.post("/api/v1/logout")
async def logout():
    response = JSONResponse(content={"message": "Logout successful"})
    response.delete_cookie("hart")
    return response

# Get current user profile route
@app.get("/api/v1/profile")
async def get_current_user_profile(payload: dict = Depends(jwt_required)):
    user = User.objects(id=payload["id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")

    return JSONResponse(
        status_code=200,
        content={"message": "current user profile fetched", "data": user.to_dict()},
    )

# Protected route
@app.get("/api/v1/protected")
async def protected(payload: dict = Depends(jwt_required)):
    return JSONResponse(content={"message": "Protected route accessed"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
