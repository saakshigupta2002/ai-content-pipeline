from langchain_community.tools.tavily_search import TavilySearchResults
from src.config import TAVILY_MAX_RESULTS


def get_search_tool():
    """Returns a configured Tavily search tool."""
    return TavilySearchResults(
        max_results=TAVILY_MAX_RESULTS,
        search_depth="basic",       # "basic" is cheaper than "advanced"
        include_answer=True,
        include_raw_content=False,   # saves tokens
    )
