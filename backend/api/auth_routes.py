from fastapi import APIRouter, Depends, HTTPException, status
from core.security import create_token, verify_token

router = APIRouter()

@router.post("/token")
async def get_token(secret_key: str):
    if secret_key != "my_secret_key":
        raise HTTPException(status_code=400, detail="Incorrect secret key")
    data = {"user": "admin"}
    token = create_token(data)
    return {"access_token": token}