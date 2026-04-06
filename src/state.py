from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages


class PipelineState(TypedDict):
    """Shared state across all agents in the pipeline."""

    # --- User Inputs ---
    topic: str                     # blog topic from user
    target_audience: str           # e.g. "beginner developers", "ML engineers"
    tone: str                      # e.g. "casual-technical", "formal", "tutorial"

    # --- Research Phase ---
    research_results: str          # summarized findings from Tavily search
    sources: list[str]             # list of source URLs

    # --- Outline Phase ---
    outline: str                   # structured blog outline
    outline_approved: bool         # set to True when user approves at checkpoint 1

    # --- Writing Phase ---
    draft: str                     # current version of the blog draft
    revision_count: int            # how many times the writer has revised (max 3)

    # --- Review Phase ---
    review_score: float            # overall score 0-10 from reviewer
    review_feedback: str           # specific feedback if rejected
    review_approved: bool          # True = reviewer approved, False = needs revision

    # --- Final Output ---
    final_approved: bool           # set to True when user approves at checkpoint 2
    final_output: str              # the approved final blog post

    # --- Pipeline Control ---
    current_agent: str             # tracks which agent is currently active
    messages: Annotated[list, add_messages]  # full message history for tracing
