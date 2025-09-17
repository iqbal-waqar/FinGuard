from typing import List, Optional
from fastapi import HTTPException, status

from backend.services.chroma import get_vectorstore
from backend.services.graph import create_agentic_finguard_agent
from backend.services.tools import (
    check_role_access, 
    extract_namespace_from_query,
    validate_query,
    get_allowed_namespaces
)
from backend.schemas.models import ChatResponse


class RAGInteractor:

    def __init__(self):
        self.vectorstore = get_vectorstore()
        self.agent = create_agentic_finguard_agent()
    
    def has_access(self, role: str, namespace: str) -> bool:
        return check_role_access(role, namespace)
    
    def get_user_permissions(self, role: str) -> List[str]:
        return get_allowed_namespaces(role)
    
    def ask(
        self, 
        user_role: str, 
        query: str, 
        namespace: Optional[str] = None
    ) -> ChatResponse:
        if not validate_query(query):
            return ChatResponse(
                answer="Please provide a valid query with at least 3 characters.",
                sources=[],
                user_role=user_role,
                namespace="general",
                access_granted=False
            )
        
        if namespace is None:
            namespace = extract_namespace_from_query(query)
        
        access_granted = self.has_access(user_role, namespace)
        
        if not access_granted:
            allowed_namespaces = self.get_user_permissions(user_role)
            return ChatResponse(
                answer=f"Access denied. Your role '{user_role}' doesn't have permission to access '{namespace}' information. You can access: {', '.join(allowed_namespaces)}",
                sources=[],
                user_role=user_role,
                namespace=namespace,
                access_granted=False
            )
        
        try:
            answer, sources = self.agent.run(query, user_role)
            
            return ChatResponse(
                answer=answer,
                sources=sources,
                user_role=user_role,
                namespace=namespace,
                access_granted=True
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing query: {str(e)}"
            )
    
    def health_check(self) -> dict:
        try:
            test_docs = self.vectorstore.similarity_search("test", k=1)
            vectorstore_status = "healthy"
        except Exception as e:
            vectorstore_status = f"error: {str(e)}"
        
        try:
            if hasattr(self.agent, 'run'):
                agent_status = "healthy"
            else:
                agent_status = "error: agent missing run method"
        except Exception as e:
            agent_status = f"error: {str(e)}"
        
        health_status = {
            "vectorstore": vectorstore_status,
            "agent": agent_status,
            "status": "healthy" if vectorstore_status == "healthy" and agent_status == "healthy" else "degraded"
        }
        
        if health_status["status"] != "healthy":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="RAG system is not healthy"
            )
        
        return health_status
