from fastapi import APIRouter
from .auth import authController
from .api import userController
router = APIRouter()

# Load auth and api routes
router.include_router(authController.router, prefix="/auth", tags=["OAuth2.0"])
router.include_router(userController.router, prefix="/api/users", tags=["Users"])