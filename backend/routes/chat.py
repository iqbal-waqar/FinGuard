from fastapi import APIRouter, Depends
from backend.schemas.models import ChatRequest, ChatResponse, User
from backend.utils.auth import get_current_user
from backend.interactors.rag import RAGInteractor

router = APIRouter()

@router.post("/query", response_model=ChatResponse)
async def chat_query(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    rag_interactor = RAGInteractor()
    return rag_interactor.ask(
        user_role=current_user.role.value,
        query=chat_request.query,
        namespace=chat_request.namespace
    )

@router.get("/health")
async def health_check():
    return {"status": "healthy"}