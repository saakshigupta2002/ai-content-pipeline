from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.config import MODEL_NAME, MAX_TOKENS, MODEL_TEMPERATURE
from src.prompts.researcher import RESEARCHER_SYSTEM_PROMPT
from src.tools.search import get_search_tool
from src.state import PipelineState


def research_node(state: PipelineState) -> dict:
    """Research agent: searches the web and summarizes findings.
    Caches results — if research_results already exists, skip the search."""

    # Cache: don't re-search if we already have results (e.g. on graph retry)
    if state.get("research_results"):
        return {
            "current_agent": "researcher",
        }

    # Step 1: Use Tavily to search
    search_tool = get_search_tool()
    search_results = search_tool.invoke(state["topic"])

    # Extract source URLs
    sources = []
    search_context = ""
    if isinstance(search_results, list):
        for result in search_results:
            if isinstance(result, dict):
                sources.append(result.get("url", ""))
                search_context += f"Source: {result.get('url', '')}\n"
                search_context += f"Content: {result.get('content', '')}\n\n"

    # Step 2: Use LLM to summarize research into structured format
    llm = ChatOpenAI(
        model=MODEL_NAME,
        temperature=MODEL_TEMPERATURE,
        max_tokens=MAX_TOKENS["researcher"],
    )

    prompt = RESEARCHER_SYSTEM_PROMPT.format(
        target_audience=state["target_audience"]
    )

    response = llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=f"Topic: {state['topic']}\n\nRaw search results:\n{search_context}")
    ])

    return {
        "research_results": response.content,
        "sources": [s for s in sources if s],  # filter empty strings
        "current_agent": "researcher",
    }
