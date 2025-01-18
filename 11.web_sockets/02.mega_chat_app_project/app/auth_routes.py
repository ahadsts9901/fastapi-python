from fastapi import APIRouter, Request, HTTPException, Response, Cookie
from pydantic import BaseModel
import requests
import jwt
from .models import User
from datetime import datetime, timedelta
from config import JWT_KEY, default_profile_picture

router = APIRouter()

class GoogleLoginRequest(BaseModel):
    accessToken: str

@router.post("/google-login")
async def google_login(data: GoogleLoginRequest, response: Response):
    try:
        access_token = data.accessToken
        google_user_resp = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        if google_user_resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch user info from Google")

        google_user = google_user_resp.json()

        if not all([google_user.get("name"), google_user.get("email"), google_user.get("picture")]):
            raise HTTPException(status_code=400, detail="Invalid Google user data")

        user = User.objects(email=google_user["email"]).first()

        if not user:
            user = User(
                username=google_user["name"],
                email=google_user["email"].lower(),
                profile_picture=google_user["picture"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            user.save()

        payload = {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "profile_picture": user.profile_picture,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
            "exp": (datetime.utcnow() + timedelta(days=1)).timestamp()
        }

        token = jwt.encode(payload, JWT_KEY, algorithm="HS256")

        response.set_cookie(
            key="hart",
            value=token,
            httponly=True,
            secure=True,
            samesite="none"
        )

        return {"message": "Google login successful"}

    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "Internal server error", "error": str(e)})

@router.post("/logout")
async def logout(response: Response):
    try:
        response.delete_cookie("hart")
        return {"message": "Logout successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "Internal server error", "error": str(e)})
