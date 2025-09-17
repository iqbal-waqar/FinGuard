import os
import csv
from typing import List, Dict, Any
from pathlib import Path
from langchain.schema import Document
from .chunking import chunk_document, chunk_documents_batch, analyze_chunk_sizes, optimize_chunk_size

def load_markdown_files(directory: str, department: str) -> List[Document]:
    data_path = Path(directory)
    
    if not data_path.exists():
        print(f"Warning: Directory {directory} does not exist")
        return []
    
    raw_documents = []
    for file_path in data_path.glob("*.md"):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
                base_metadata = {
                    "source": file_path.name,
                    "department": department,
                    "document_type": "markdown"
                }
                
                raw_documents.append(Document(page_content=content, metadata=base_metadata))
                
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    if not raw_documents:
        return []
    
    chunked_documents = chunk_documents_batch(raw_documents, is_markdown=True)
    return chunked_documents


def load_csv_files(directory: str, department: str) -> List[Document]:
    documents = []
    data_path = Path(directory)
    
    if not data_path.exists():
        print(f"Warning: Directory {directory} does not exist")
        return documents
    
    for file_path in data_path.glob("*.csv"):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                rows = list(csv_reader)
                
                summary_content = f"# {department.title()} Data Summary\n\n"
                summary_content += f"Total records: {len(rows)}\n\n"
                
                if rows:
                    columns = list(rows[0].keys())
                    summary_content += f"Columns: {', '.join(columns)}\n\n"
                    
                    summary_content += "## Sample Data Preview:\n\n"
                    for i, row in enumerate(rows[:3]): 
                        summary_content += f"**Record {i+1}:**\n"
                        for key, value in row.items():
                            summary_content += f"- {key}: {value}\n"
                        summary_content += "\n"
                
                summary_metadata = {
                    "source": f"{file_path.name}_summary",
                    "department": department,
                    "document_type": "csv_summary"
                }
                
                summary_chunks = chunk_document(summary_content, summary_metadata, is_markdown=True)
                documents.extend(summary_chunks)
                
                csv_chunks = []
                if rows:
                    raw_csv_docs = []
                    optimal_config = optimize_chunk_size("\n".join([str(row) for row in rows[:5]]))
                    chunk_size = max(5, optimal_config["chunk_size"] // 200)
                    
                    for i in range(0, len(rows), chunk_size):
                        chunk_rows = rows[i:i+chunk_size]
                        
                        if department == "hr":
                            chunk_content = f"# Employee Records (Batch {i//chunk_size + 1})\n\n"
                            for row in chunk_rows:
                                chunk_content += f"**Employee ID**: {row.get('employee_id', 'N/A')}\n"
                                chunk_content += f"**Name**: {row.get('full_name', 'N/A')}\n"
                                chunk_content += f"**Role**: {row.get('role', 'N/A')}\n"
                                chunk_content += f"**Department**: {row.get('department', 'N/A')}\n"
                                chunk_content += f"**Location**: {row.get('location', 'N/A')}\n"
                                chunk_content += f"**Salary**: PKR {row.get('salary', 'N/A')}\n"
                                chunk_content += f"**Performance Rating**: {row.get('performance_rating', 'N/A')}/5\n"
                                chunk_content += f"**Attendance**: {row.get('attendance_pct', 'N/A')}%\n\n"
                            doc_type = "employee_records"
                        else:
                            chunk_content = f"# {department.title()} Data Records (Batch {i//chunk_size + 1})\n\n"
                            for j, row in enumerate(chunk_rows):
                                chunk_content += f"**Record {i+j+1}:**\n"
                                for key, value in row.items():
                                    chunk_content += f"- {key}: {value}\n"
                                chunk_content += "\n"
                            doc_type = "csv_records"
                        
                        chunk_metadata = {
                            "source": f"{file_path.name}_batch_{i//chunk_size + 1}",
                            "department": department,
                            "document_type": doc_type
                        }
                        
                        raw_csv_docs.append(Document(page_content=chunk_content, metadata=chunk_metadata))
                    
                    csv_chunks = chunk_documents_batch(raw_csv_docs, is_markdown=True)
                    documents.extend(csv_chunks)
                
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    return documents


def load_all_documents() -> List[Document]:
    base_data_path = "/home/rohail/Desktop/FinGuard/data"
    all_documents = []
    
    departments = {
        "finance": ["md"],
        "marketing": ["md"],
        "hr": ["csv", "md"],
        "engineering": ["md"],
        "general": ["md"]
    }
    
    for department, file_types in departments.items():
        department_path = os.path.join(base_data_path, department)
        
        if "md" in file_types:
            md_docs = load_markdown_files(department_path, department)
            all_documents.extend(md_docs)
        
        if "csv" in file_types:
            csv_docs = load_csv_files(department_path, department)
            all_documents.extend(csv_docs)
    
    return all_documents

def get_chunking_stats() -> Dict[str, Any]:
    documents = load_all_documents()
    
    base_stats = analyze_chunk_sizes(documents)
    
    departments = {}
    for doc in documents:
        dept = doc.metadata.get("department", "unknown")
        chunk_size = len(doc.page_content)
        
        if dept not in departments:
            departments[dept] = {"count": 0, "avg_size": 0, "total_size": 0}
        departments[dept]["count"] += 1
        departments[dept]["total_size"] += chunk_size
    
    for dept_stats in departments.values():
        if dept_stats["count"] > 0:
            dept_stats["avg_size"] = dept_stats["total_size"] // dept_stats["count"]
    
    base_stats["departments"] = departments
    base_stats["total_documents"] = base_stats["total_chunks"] 
    
    return base_stats