import jwt
from functools import wraps
from .models import User
from config import JWT_KEY
from fastapi import HTTPException, Request, Depends


# JWT authentication middleware
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

# Role-based access control middleware
def role_required(role: str):
    def wrapper(request: Request, token_payload=Depends(jwt_required)):
        user = User.objects(id=token_payload['id']).first()
        if user and user.role != role:
            raise HTTPException(status_code=403, detail="Only admins are allowed")
        return True  # You can allow the request to proceed if the role matches
    return wrapper
