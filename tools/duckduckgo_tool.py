from langchain_core.tools import tool
from langchain_community.utilities.duckduckgo_search import DuckDuckGoSearchAPIWrapper
from tavily import TavilyClient
from utils.retry_utils import retry_with_backoff
from dotenv import load_dotenv
import os
import logging

load_dotenv()

# Global flag to track if Tavily was used
_tavily_used = False

def is_tavily_used():
    return _tavily_used

@tool
@retry_with_backoff(max_attempts=3, backoff_in_seconds=1)
def ddg_search(query: str) -> str:
    """Search the web using DuckDuckGo with Tavily as a fallback."""
    global _tavily_used
    try:
        ddg = DuckDuckGoSearchAPIWrapper()
        return ddg.run(query)
    except Exception as e:
        logging.error(f"DuckDuckGo search failed: {str(e)}")
        if "rate limit" in str(e).lower() or "429" in str(e).lower():
            _tavily_used = True
            tavily_api_key = os.getenv("TAVILY_API_KEY")
            if not tavily_api_key:
                raise ValueError("Tavily API key not found in .env file.")
            try:
                tavily = TavilyClient(api_key=tavily_api_key)
                results = tavily.search(query=query, max_results=5)["results"]
                return "\n".join([f"{r['title']}: {r['content']}" for r in results])
            except Exception as tavily_error:
                raise ValueError(f"Tavily search failed: {str(tavily_error)}")
        raise e