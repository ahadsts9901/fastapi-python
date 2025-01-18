from fastapi import APIRouter, Depends, HTTPException
from .middleware import jwt_required
from .models import User
from pydantic import BaseModel

router = APIRouter()

class UserProfileResponse(BaseModel):
    id: str
    username: str
    email: str
    profile_picture: str
    created_at: str
    updated_at: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    profile_picture: str
    created_at: str
    updated_at: str

@router.get("/profile", response_model=UserProfileResponse)
async def get_current_user_profile(current_user: dict = Depends(jwt_required)):
    try:
        user_id = current_user['id']
        user = User.objects(id=user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'profile_picture': user.profile_picture,
            'created_at': user.created_at.isoformat(),
            'updated_at': user.updated_at.isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "Internal server error", "error": str(e)})

@router.get("/profile/{user_id}", response_model=UserProfileResponse)
async def get_dynamic_user_profile(user_id: str, current_user: dict = Depends(jwt_required)):
    try:
        user = User.objects(id=user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'profile_picture': user.profile_picture,
            'created_at': user.created_at.isoformat(),
            'updated_at': user.updated_at.isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "Internal server error", "error": str(e)})
