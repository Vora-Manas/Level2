from langchain_core.tools import tool
from tavily import TavilyClient
from utils.retry_utils import retry_with_backoff
from dotenv import load_dotenv
import os
import logging

load_dotenv()

# Global flag to indicate Tavily is always used
_tavily_used = True

def is_tavily_used():
    return _tavily_used

@tool
@retry_with_backoff(max_attempts=3, backoff_in_seconds=1)
def tavily_search(query: str) -> str:
    """Search the web using Tavily API."""
    tavily_api_key = os.getenv("tavily_api_key")
    if not tavily_api_key:
        raise ValueError("Tavily API key not found in .env file.")
    
    try:
        tavily = TavilyClient(api_key=tavily_api_key)
        results = tavily.search(query=query, max_results=5)["results"]
        return "\n".join([f"{r['title']}: {r['content']}" for r in results])
    except Exception as e:
        logging.error(f"Tavily search failed: {str(e)}")
        raise ValueError(f"Failed to perform search with Tavily: {str(e)}")