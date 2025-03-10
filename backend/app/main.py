from fastapi import FastAPI
from api.auth_routes import router as auth_router
from api.protected_routes import router as protected_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(protected_router)