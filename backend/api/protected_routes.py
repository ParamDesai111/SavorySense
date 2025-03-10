from fastapi import APIRouter, Depends, HTTPException, status
from core.security import create_token, verify_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
auth_scheme = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    token = credentials.credentials
    user = verify_token(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

@router.get("/protected")
async def protected_route(user: dict = Depends(get_current_user)):
    return {"message": "This is protected data", "user": user}

