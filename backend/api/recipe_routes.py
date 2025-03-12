from fastapi import APIRouter, Depends, HTTPException
from core.scraper import scrape_recipe
from core.security import verify_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
auth_scheme = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    token = credentials.credentials
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid authentication credentials")
    return user

@router.post("/scrape-recipe", dependencies=[Depends(get_current_user)])
def scrape_recipe_endpoint(url: str):
    try:
        recipe_details = scrape_recipe(url)
        if recipe_details:
            return recipe_details
        else:
            return {"message": "No recipe found at the provided URL."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
