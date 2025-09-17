from typing import List, Dict, Tuple
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

from backend.services.tools import FINGUARD_TOOLS
from backend.services.prompts import AGENTIC_SYSTEM_PROMPT

load_dotenv()

_groq_llm = None

def get_groq_llm():
    global _groq_llm
    if _groq_llm is None:
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        _groq_llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name="llama-3.1-8b-instant",  
            temperature=0.1,
            max_tokens=2048
        )
    return _groq_llm


class FinGuardAgenticAgent:
    
    def __init__(self):
        self.llm = get_groq_llm()
        
        self.agent = self._create_agentic_agent()
    
    def _create_agentic_agent(self):
        return create_react_agent(
            self.llm,
            FINGUARD_TOOLS
        )
    
    def run(self, query: str, user_role: str) -> Tuple[str, List[Dict]]:
        try:
            input_data = {
                "messages": [
                    SystemMessage(content=AGENTIC_SYSTEM_PROMPT),
                    HumanMessage(content=f"User Role: {user_role}\nQuery: {query}")
                ]
            }
            
            result = self.agent.invoke(input_data)
            
            final_message = result["messages"][-1]
            response = final_message.content
            
            sources = []
            for message in result["messages"]:
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    for tool_call in message.tool_calls:
                        tool_name = tool_call.get('name', 'Unknown Tool')
                        sources.append({
                            "text": f"Used tool: {tool_name}",
                            "metadata": {"tool": tool_name, "type": "tool_call"}
                        })
                
                if hasattr(message, 'content') and isinstance(message.content, str):
                    if '[Source:' in message.content:
                        import re
                        source_matches = re.findall(r'\[Source: ([^\]]+)\]', message.content)
                        for source in source_matches:
                            sources.append({
                                "text": f"Document: {source}",
                                "metadata": {"source": source, "type": "document"}
                            })
            
            return response, sources
            
        except Exception as e:
            error_msg = f"I apologize, but I encountered an error while processing your request: {str(e)}"
            return error_msg, []


def create_agentic_finguard_agent() -> FinGuardAgenticAgent:
    return FinGuardAgenticAgent()