from fastapi import APIRouter
from .auth import authController as auth
from .api_v1 import test

router = APIRouter()

# Load auth and api routes
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(test.router, prefix="/api/v1", tags=["api_v1"])