from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class UserRole(str, Enum):
    FINANCE = "finance"
    MARKETING = "marketing"
    HR = "hr"
    ENGINEERING = "engineering"
    C_LEVEL = "c_level"
    EMPLOYEE = "employee"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class AuthRequest(BaseModel):
    username: str
    password: str


class User(BaseModel):
    username: str
    role: UserRole
    full_name: Optional[str] = None
    email: Optional[str] = None


class ChatRequest(BaseModel):
    query: str
    namespace: Optional[str] = "general"


class SourceItem(BaseModel):
    id: Optional[str] = None
    text: str
    metadata: Dict[str, Any] = {}
    score: Optional[float] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceItem]
    user_role: str
    namespace: str
    access_granted: bool


class AgentState(BaseModel):
    query: str
    user_role: str
    namespace: str
    retrieved_docs: List[Dict[str, Any]] = []
    context: str = ""
    answer: str = ""
    sources: List[SourceItem] = []
    access_granted: bool = False
    error: Optional[str] = None


class DocumentMetadata(BaseModel):
    source: str
    department: str
    document_type: str
    created_at: Optional[str] = None
    access_level: str = "general"