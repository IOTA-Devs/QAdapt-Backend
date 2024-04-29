from fastapi import APIRouter
from .auth import authController
from .api import userController
from .api import personalTokensController

router = APIRouter()

# Load auth and api routes
router.include_router(authController.router, prefix="/auth", tags=["OAuth2.0"])
router.include_router(userController.router, prefix="/api/users", tags=["Users"])
router.include_router(personalTokensController.router, prefix="/api/personal_tokens", tags=["Personal Access Tokens"])