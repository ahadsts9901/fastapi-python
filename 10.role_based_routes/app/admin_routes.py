from fastapi import APIRouter, Depends, HTTPException, Request
from .middleware import jwt_required, role_required
from .models import User
from fastapi.responses import JSONResponse

# Initialize the router
admin_router = APIRouter()

# Admin route to fetch all users
@admin_router.get("/users")
async def get_all_users(request: Request, _=Depends(role_required('admin'))):
    # `jwt_required` is automatically called when `role_required` is used due to Depends
    try:
        users = User.objects.all()
        return JSONResponse(
            content={
                'message': 'All users fetched',
                'data': [user.to_dict() for user in users]
            }, 
            status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
