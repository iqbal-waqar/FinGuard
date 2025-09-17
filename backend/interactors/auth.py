from datetime import timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status

from backend.schemas.models import User, TokenResponse
from backend.utils.auth import (
    authenticate_user, 
    create_access_token, 
    get_demo_credentials,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

class AuthInteractor:
    
    def login(self, username: str, password: str) -> TokenResponse:
        user = authenticate_user(username, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"], "role": user["role"].value},
            expires_delta=access_token_expires
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    def get_demo_credentials(self) -> Dict[str, Any]:
        return {
            "message": "Demo credentials for testing the FinGuard RAG Chatbot",
            "credentials": get_demo_credentials()
        }