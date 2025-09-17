from typing import List, Dict, Any
import re
from langchain.tools import tool


def check_role_access(user_role: str, namespace: str) -> bool:
    allowed_namespaces = get_allowed_namespaces(user_role)
    return namespace.lower() in allowed_namespaces


def get_allowed_namespaces(user_role: str) -> List[str]:
    from backend.services.prompts import ROLE_PERMISSIONS
    
    role_info = ROLE_PERMISSIONS.get(user_role.lower(), {})
    return role_info.get("namespaces", [])


def create_context_from_docs(docs: List[Any]) -> str:
    if not docs:
        return "No relevant documents found."
    
    context_parts = []
    for i, doc in enumerate(docs, 1):
        content = getattr(doc, 'page_content', str(doc))
        metadata = getattr(doc, 'metadata', {})
        
        source_info = metadata.get('source', f'Document {i}')
        context_parts.append(f"[Source: {source_info}]\n{content}")
    
    return "\n\n".join(context_parts)


def filter_docs_by_access(docs: List[Any], user_role: str) -> List[Any]:
    if user_role.lower() == "c_level":
        return docs 
    
    allowed_namespaces = get_allowed_namespaces(user_role)
    filtered_docs = []
    
    for doc in docs:
        metadata = getattr(doc, 'metadata', {})
        doc_namespace = metadata.get('department', 'general').lower()
        
        if doc_namespace in allowed_namespaces:
            filtered_docs.append(doc)
    
    return filtered_docs


def validate_query(query: str) -> bool:
    if not query or not query.strip():
        return False
    return len(query.strip()) >= 3


def extract_namespace_from_query(query: str) -> str:
    query_lower = query.lower()
    
    namespace_keywords = {
        "finance": ["financial", "budget", "expense", "cost", "revenue", "profit", "accounting", "invoice"],
        "marketing": ["marketing", "campaign", "customer", "sales", "promotion", "advertising", "brand"],
        "hr": ["employee", "payroll", "attendance", "performance", "hiring", "hr", "human resources"],
        "engineering": ["technical", "development", "architecture", "system", "code", "engineering", "software"]
    }
    
    namespace_scores = {}
    for namespace, keywords in namespace_keywords.items():
        score = sum(1 for keyword in keywords if keyword in query_lower)
        if score > 0:
            namespace_scores[namespace] = score
    
    if namespace_scores:
        return max(namespace_scores, key=namespace_scores.get)
    
    return "general"

@tool
def search_financial_data(query: str, user_role: str) -> str:
    """
    Search for financial data including budgets, expenses, revenue, and financial reports.
    Use this tool when users ask about financial information, costs, budgets, or revenue.
    
    Args:
        query: The search query about financial data
        user_role: The user's role for access control
    
    Returns:
        Formatted financial information or access denied message
    """
    from backend.services.chroma import search_documents
    
    if not check_role_access(user_role, "finance"):
        return f"Access denied. Role '{user_role}' cannot access financial data. Contact your administrator."
    
    try:
        docs = search_documents(
            query=f"financial budget expense revenue {query}",
            k=5,
            collection_name="finguard"
        )
        
        filtered_docs = [
            doc for doc in docs 
            if doc.metadata.get('department') == 'finance'
        ]
        
        if not filtered_docs:
            return "No financial data found for your query."
        
        context = create_context_from_docs(filtered_docs)
        return f"Financial Data Found:\n\n{context}"
        
    except Exception as e:
        return f"Error searching financial data: {str(e)}"


@tool
def search_employee_data(query: str, user_role: str) -> str:
    """
    Search for employee information including payroll, attendance, performance, and HR data.
    Use this tool when users ask about employees, HR policies, attendance, or payroll.
    
    Args:
        query: The search query about employee data
        user_role: The user's role for access control
    
    Returns:
        Formatted employee information or access denied message
    """
    from backend.services.chroma import search_documents
    
    if not check_role_access(user_role, "hr"):
        return f"Access denied. Role '{user_role}' cannot access employee data. Contact your administrator."
    
    try:
        docs = search_documents(
            query=f"employee hr payroll attendance {query}",
            k=5,
            collection_name="finguard"
        )
        
        filtered_docs = [
            doc for doc in docs 
            if doc.metadata.get('department') == 'hr'
        ]
        
        if not filtered_docs:
            return "No employee data found for your query."
        
        context = create_context_from_docs(filtered_docs)
        return f"Employee Data Found:\n\n{context}"
        
    except Exception as e:
        return f"Error searching employee data: {str(e)}"


@tool
def search_marketing_data(query: str, user_role: str) -> str:
    """
    Search for marketing information including campaigns, customer data, sales metrics, and marketing reports.
    Use this tool when users ask about marketing campaigns, customers, sales, or promotional activities.
    
    Args:
        query: The search query about marketing data
        user_role: The user's role for access control
    
    Returns:
        Formatted marketing information or access denied message
    """
    from backend.services.chroma import search_documents
    
    if not check_role_access(user_role, "marketing"):
        return f"Access denied. Role '{user_role}' cannot access marketing data. Contact your administrator."
    
    try:
        docs = search_documents(
            query=f"marketing campaign customer sales {query}",
            k=5,
            collection_name="finguard"
        )
        
        filtered_docs = [
            doc for doc in docs 
            if doc.metadata.get('department') == 'marketing'
        ]
        
        if not filtered_docs:
            return "No marketing data found for your query."
        
        context = create_context_from_docs(filtered_docs)
        return f"Marketing Data Found:\n\n{context}"
        
    except Exception as e:
        return f"Error searching marketing data: {str(e)}"


@tool
def search_engineering_data(query: str, user_role: str) -> str:
    """
    Search for engineering and technical information including system architecture, development processes, and technical documentation.
    Use this tool when users ask about technical systems, development, or engineering processes.
    
    Args:
        query: The search query about engineering data
        user_role: The user's role for access control
    
    Returns:
        Formatted engineering information or access denied message
    """
    from backend.services.chroma import search_documents
    
    if not check_role_access(user_role, "engineering"):
        return f"Access denied. Role '{user_role}' cannot access engineering data. Contact your administrator."
    
    try:
        docs = search_documents(
            query=f"engineering technical development system {query}",
            k=5,
            collection_name="finguard"
        )
        
        filtered_docs = [
            doc for doc in docs 
            if doc.metadata.get('department') == 'engineering'
        ]
        
        if not filtered_docs:
            return "No engineering data found for your query."
        
        context = create_context_from_docs(filtered_docs)
        return f"Engineering Data Found:\n\n{context}"
        
    except Exception as e:
        return f"Error searching engineering data: {str(e)}"


@tool
def search_general_policies(query: str, user_role: str) -> str:
    """
    Search for general company policies, procedures, and public information.
    Use this tool when users ask about company policies, procedures, or general information.
    
    Args:
        query: The search query about general policies
        user_role: The user's role for access control
    
    Returns:
        Formatted general policy information
    """
    from backend.services.chroma import search_documents
    
    try:
        docs = search_documents(
            query=f"policy procedure general {query}",
            k=5,
            collection_name="finguard"
        )
        
        filtered_docs = [
            doc for doc in docs 
            if doc.metadata.get('department') == 'general'
        ]
        
        if not filtered_docs:
            return "No general policy information found for your query."
        
        context = create_context_from_docs(filtered_docs)
        return f"General Policy Information:\n\n{context}"
        
    except Exception as e:
        return f"Error searching general policies: {str(e)}"


@tool
def calculate_financial_metrics(data: str, calculation_type: str) -> str:
    """
    Perform financial calculations like percentages, growth rates, or basic arithmetic on financial data.
    Use this tool when users need calculations performed on financial numbers.
    
    Args:
        data: The financial data or numbers to calculate
        calculation_type: Type of calculation (percentage, growth_rate, sum, average)
    
    Returns:
        Calculated result with explanation
    """
    try:
        numbers = re.findall(r'-?\d+(?:\.\d+)?', data)
        numbers = [float(n) for n in numbers]
        
        if not numbers:
            return "No numerical data found to calculate."
        
        if calculation_type.lower() == "sum":
            result = sum(numbers)
            return f"Sum of values: {result:,.2f}"
        
        elif calculation_type.lower() == "average":
            result = sum(numbers) / len(numbers)
            return f"Average of values: {result:,.2f}"
        
        elif calculation_type.lower() == "percentage" and len(numbers) >= 2:
            percentage = (numbers[0] / numbers[1]) * 100
            return f"Percentage: {percentage:.2f}%"
        
        elif calculation_type.lower() == "growth_rate" and len(numbers) >= 2:
            growth = ((numbers[1] - numbers[0]) / numbers[0]) * 100
            return f"Growth rate: {growth:.2f}%"
        
        else:
            return f"Available numbers: {numbers}. Please specify a valid calculation type."
            
    except Exception as e:
        return f"Error performing calculation: {str(e)}"


@tool
def get_user_permissions(user_role: str) -> str:
    """
    Get information about what data and areas a user role can access.
    Use this tool when users ask about their permissions or access levels.
    
    Args:
        user_role: The user's role
    
    Returns:
        Information about user permissions and accessible areas
    """
    from backend.services.prompts import ROLE_PERMISSIONS
    
    role_info = ROLE_PERMISSIONS.get(user_role.lower(), {})
    if not role_info:
        return f"Unknown role: {user_role}"
    
    areas = ", ".join(role_info["areas"])
    namespaces = ", ".join(role_info["namespaces"])
    
    return f"Role: {user_role.title()}\nAccessible Areas: {areas}\nAccessible Departments: {namespaces}"


@tool
def smart_search(query: str, user_role: str) -> str:
    """
    Intelligent search that automatically determines the best data source based on the query content.
    Use this tool when the query doesn't clearly fit into a specific category.
    
    Args:
        query: The search query
        user_role: The user's role for access control
    
    Returns:
        Relevant information from the most appropriate data source
    """
    from backend.services.chroma import search_documents
    
    try:
        namespace = extract_namespace_from_query(query)
        
        docs = search_documents(
            query=query,
            k=8,
            collection_name="finguard"
        )
        
        filtered_docs = filter_docs_by_access(docs, user_role)
        
        if not filtered_docs:
            return f"No accessible information found for your query. Your role '{user_role}' may not have access to the requested data."
        
        dept_results = {}
        for doc in filtered_docs:
            dept = doc.metadata.get('department', 'general')
            if dept not in dept_results:
                dept_results[dept] = []
            dept_results[dept].append(doc)
        
        formatted_results = []
        for dept, dept_docs in dept_results.items():
            context = create_context_from_docs(dept_docs[:2]) 
            formatted_results.append(f"=== {dept.title()} Department ===\n{context}")
        
        return "\n\n".join(formatted_results)
        
    except Exception as e:
        return f"Error performing smart search: {str(e)}"


FINGUARD_TOOLS = [
    search_financial_data,
    search_employee_data,
    search_marketing_data,
    search_engineering_data,
    search_general_policies,
    calculate_financial_metrics,
    get_user_permissions,
    smart_search
]