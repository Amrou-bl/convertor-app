from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from .database import *
from . import models
from app.routers import auth

models.Base.metadata.create_all(bind=engine)

application = FastAPI(
    version="1.0.0",
    description="This API provides endpoints for user authentication and management. It includes functionality for user registration, login, token verification, and logout. The API supports creating new user accounts, authenticating users to obtain access tokens, validating those tokens to access protected resources, and invalidating tokens upon logout. Each endpoint is designed to handle specific authentication tasks securely and efficiently, ensuring proper user management and access control within the application",
    title="User Authentication API",
    docs_url=None,
    openapi_url="/docs/openapi.json",
    redoc_url="/docs",
)
application.include_router(auth.router)


@application.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")