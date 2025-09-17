from typing import List, Dict, Any
from langchain.schema import Document
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter, 
    MarkdownHeaderTextSplitter
)

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
MIN_CHUNK_SIZE = 50

def filter_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    filtered = {}
    for key, value in metadata.items():
        if isinstance(value, (str, int, float, bool, type(None))):
            filtered[key] = value
        else:
            filtered[key] = str(value)
    return filtered

def get_text_splitter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""],
        keep_separator=True,
        add_start_index=True  
    )

def get_markdown_splitter() -> MarkdownHeaderTextSplitter:
    return MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "Header 1"),
            ("##", "Header 2"), 
            ("###", "Header 3"),
            ("####", "Header 4"),
        ],
        strip_headers=False,
        return_each_line=False  
    )

def chunk_document(content: str, metadata: Dict[str, Any], is_markdown: bool = True) -> List[Document]:
    """
    Chunk document using LangChain's optimized text splitters
    
    Args:
        content: Document content to chunk
        metadata: Base metadata for the document
        is_markdown: Whether to use markdown-aware chunking
        
    Returns:
        List of Document chunks with enhanced metadata
    """
    doc = Document(page_content=content, metadata=metadata)
    
    try:
        if is_markdown and len(content) > CHUNK_SIZE:
            markdown_splitter = get_markdown_splitter()
            md_chunks = markdown_splitter.split_text(content)
            
            text_splitter = get_text_splitter()
            final_chunks = []
            
            for i, md_chunk in enumerate(md_chunks):
                if len(md_chunk.page_content) > CHUNK_SIZE:
                    sub_chunks = text_splitter.split_documents([md_chunk])
                    for chunk in sub_chunks:
                        enhanced_metadata = metadata.copy()
                        enhanced_metadata.update(md_chunk.metadata) 
                        enhanced_metadata.update({
                            "chunk_type": "markdown_hierarchical",
                            "source": metadata.get("source", "unknown")
                        })
                        enhanced_metadata = filter_metadata(enhanced_metadata)
                        chunk.metadata = enhanced_metadata
                    final_chunks.extend(sub_chunks)
                else:
                    enhanced_metadata = metadata.copy()
                    enhanced_metadata.update(md_chunk.metadata)  
                    enhanced_metadata.update({
                        "chunk_type": "markdown",
                        "source": metadata.get("source", "unknown")
                    })
                    enhanced_metadata = filter_metadata(enhanced_metadata)
                    md_chunk.metadata = enhanced_metadata
                    final_chunks.append(md_chunk)
            
            return final_chunks
            
        else:
            text_splitter = get_text_splitter()
            chunks = text_splitter.split_documents([doc])
            
            for chunk in chunks:
                enhanced_metadata = chunk.metadata.copy()
                enhanced_metadata.update({
                    "chunk_type": "text",
                    "source": metadata.get("source", "unknown")
                })
                enhanced_metadata = filter_metadata(enhanced_metadata)
                chunk.metadata = enhanced_metadata
            
            return chunks
            
    except Exception as e:
        print(f"Advanced chunking failed, using fallback: {e}")
        text_splitter = get_text_splitter()
        chunks = text_splitter.split_documents([doc])
        
        for chunk in chunks:
            enhanced_metadata = chunk.metadata.copy()
            enhanced_metadata.update({
                "chunk_type": "fallback",
                "source": metadata.get("source", "unknown")
            })
            enhanced_metadata = filter_metadata(enhanced_metadata)
            chunk.metadata = enhanced_metadata
        
        return chunks

def chunk_documents_batch(documents: List[Document], is_markdown: bool = True) -> List[Document]:
    """
    Efficiently chunk multiple documents using LangChain's batch processing
    
    Args:
        documents: List of documents to chunk
        is_markdown: Whether to use markdown-aware chunking
        
    Returns:
        List of chunked documents
    """
    if not documents:
        return []
    
    try:
        if is_markdown:
            all_chunks = []
            for doc in documents:
                chunks = chunk_document(doc.page_content, doc.metadata, is_markdown=True)
                all_chunks.extend(chunks)
            return all_chunks
        else:
            text_splitter = get_text_splitter()
            all_chunks = text_splitter.split_documents(documents)
            
            for chunk in all_chunks:
                enhanced_metadata = chunk.metadata.copy()
                enhanced_metadata.update({
                    "chunk_type": "text",
                    "source": chunk.metadata.get("source", "unknown")
                })
                chunk.metadata = filter_metadata(enhanced_metadata)
            
            return all_chunks
        
    except Exception as e:
        print(f"Batch chunking failed: {e}")
        return documents

def get_chunking_config() -> Dict[str, Any]:
    return {
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
        "min_chunk_size": MIN_CHUNK_SIZE,
        "splitter_type": "RecursiveCharacterTextSplitter",
        "markdown_aware": True
    }

def analyze_chunk_sizes(documents: List[Document]) -> Dict[str, Any]:
    """
    Analyze chunk size distribution using efficient operations
    
    Args:
        documents: List of documents to analyze
        
    Returns:
        Dictionary with comprehensive chunk statistics
    """
    if not documents:
        return {"error": "No documents provided"}
    
    sizes = [len(doc.page_content) for doc in documents]
    total_size = sum(sizes)
    
    size_distribution = {
        "small": sum(1 for s in sizes if s < 300),
        "medium": sum(1 for s in sizes if 300 <= s < 700), 
        "large": sum(1 for s in sizes if s >= 700)
    }
    
    chunk_types = {}
    for doc in documents:
        chunk_type = doc.metadata.get("chunk_type", "unknown")
        size = len(doc.page_content)
        
        if chunk_type not in chunk_types:
            chunk_types[chunk_type] = []
        chunk_types[chunk_type].append(size)
    
    chunk_type_stats = {
        chunk_type: {
            "count": len(type_sizes),
            "avg_size": sum(type_sizes) // len(type_sizes) if type_sizes else 0,
            "min_size": min(type_sizes) if type_sizes else 0,
            "max_size": max(type_sizes) if type_sizes else 0
        }
        for chunk_type, type_sizes in chunk_types.items()
    }
    
    return {
        "total_chunks": len(documents),
        "avg_chunk_size": total_size // len(documents) if documents else 0,
        "total_size": total_size,
        "size_distribution": size_distribution,
        "chunk_types": chunk_type_stats,
        "config": get_chunking_config()
    }

def optimize_chunk_size(content_sample: str, target_chunks: int = 10) -> Dict[str, int]:
    """
    Dynamically optimize chunk size based on content characteristics
    
    Args:
        content_sample: Sample content to analyze
        target_chunks: Target number of chunks
        
    Returns:
        Optimized chunking parameters
    """
    content_length = len(content_sample)
    
    if content_length == 0:
        return get_chunking_config()
    
    optimal_chunk_size = max(MIN_CHUNK_SIZE, content_length // target_chunks)
    optimal_overlap = min(CHUNK_OVERLAP, optimal_chunk_size // 4)
    
    return {
        "chunk_size": optimal_chunk_size,
        "chunk_overlap": optimal_overlap,
        "min_chunk_size": MIN_CHUNK_SIZE
    }