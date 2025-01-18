from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from .models import User
from .middleware import jwt_required  # Assuming this is already implemented
from fastapi import Request

user_router = APIRouter()

# Get current user profile
@user_router.get("/profile")
async def get_current_user_profile(request: Request, payload: dict = Depends(jwt_required)):
    user_id = payload['id']
    user = User.objects(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return JSONResponse(
        status_code=200,
        content={
            "message": "Profile fetched",
            "data": {
                "id": str(user.id),
                "username": user.username,
                "profile_picture": user.profile_picture,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat(),
            }
        }
    )
