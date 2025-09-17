from typing import Any, List, Optional
import os
from dotenv import load_dotenv
from langchain.schema import Document
from .embedding import get_embeddings, reset_embeddings

load_dotenv()

CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "./chroma_db")

try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma

_vectorstore = None


def get_vectorstore(collection_name: str = "finguard") -> Chroma:
    global _vectorstore
    if _vectorstore is None:
        embeddings = get_embeddings()
        
        _vectorstore = Chroma(
            persist_directory=CHROMA_DB_DIR,
            collection_name=collection_name,
            embedding_function=embeddings,
        )
    return _vectorstore


def add_documents_to_vectorstore(
    documents: List[Document], 
    collection_name: str = "finguard"
) -> None:
    vectorstore = get_vectorstore(collection_name)
    vectorstore.add_documents(documents)

def search_documents(
    query: str, 
    k: int = 4, 
    collection_name: str = "finguard",
    filter_dict: Optional[dict] = None
) -> List[Document]:
    vectorstore = get_vectorstore(collection_name)
    
    if filter_dict:
        docs = vectorstore.similarity_search(
            query, 
            k=k, 
            filter=filter_dict
        )
    else:
        docs = vectorstore.similarity_search(query, k=k)
    
    return docs


def clear_vectorstore(collection_name: str = "finguard") -> None:
    try:
        import shutil
        if os.path.exists(CHROMA_DB_DIR):
            shutil.rmtree(CHROMA_DB_DIR)
        
        global _vectorstore
        _vectorstore = None
        
        reset_embeddings()
        
    except Exception as e:
        print(f"Error clearing vectorstore: {e}")
        raise

def initialize_data_from_files(force_reload: bool = False):
    try:
        if force_reload:
            clear_vectorstore()
        
        vectorstore = get_vectorstore()
        
        try:
            existing_docs = vectorstore.similarity_search("test", k=1)
            if existing_docs and not force_reload:
                return
        except:
            pass
        
        from backend.services.data_loader import load_all_documents, get_chunking_stats
        
        documents = load_all_documents()
        
        if not documents:
            return
        
        add_documents_to_vectorstore(documents, "finguard")
        
    except Exception as e:
        raise


if __name__ == "__main__":
    import sys
    
    force_reload = "--force" in sys.argv or "-f" in sys.argv
    initialize_data_from_files(force_reload=force_reload)