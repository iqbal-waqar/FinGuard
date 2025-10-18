from fastapi import APIRouter, Depends
from backend.schemas.models import AuthRequest, TokenResponse, User
from backend.utils.auth import get_current_user
from backend.interactors.auth import AuthInteractor

router = APIRouter()

auth_interactor = AuthInteractor()


@router.post("/login", response_model=TokenResponse)
async def login(auth_request: AuthRequest):
    return auth_interactor.login(auth_request.username, auth_request.password)


@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/demo-credentials")
async def get_demo_users():
    return auth_interactor.get_demo_credentials()
