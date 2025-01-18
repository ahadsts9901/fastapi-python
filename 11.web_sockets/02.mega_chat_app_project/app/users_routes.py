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

@router.get("/users", response_model=list[UserResponse])
async def get_all_users(current_user: dict = Depends(jwt_required)):
    try:
        users = User.objects.all()
        return [
            {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'profile_picture': user.profile_picture,
                'created_at': user.created_at.isoformat(),
                'updated_at': user.updated_at.isoformat()
            } for user in users
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "Internal server error", "error": str(e)})
