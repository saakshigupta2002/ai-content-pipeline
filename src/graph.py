from langgraph.graph import StateGraph, START, END

from src.state import PipelineState
from src.agents.researcher import research_node
from src.agents.outliner import outline_node
from src.agents.writer import writer_node
from src.agents.reviewer import reviewer_node
from src.agents.supervisor import should_revise_or_approve
from src.config import CHECKPOINT_DB_PATH


def _get_sqlite_saver(conn_string: str):
    """Import and return a SqliteSaver, handling package location differences.
    Also ensures the parent directory exists for file-based paths."""
    import os
    if conn_string != ":memory:":
        os.makedirs(os.path.dirname(conn_string), exist_ok=True)
    try:
        from langgraph.checkpoint.sqlite import SqliteSaver
    except ImportError:
        from langgraph_checkpoint_sqlite import SqliteSaver
    return SqliteSaver.from_conn_string(conn_string)


def human_review_outline_node(state: PipelineState) -> dict:
    """Placeholder node for human outline review checkpoint.
    The actual interrupt happens via interrupt_before on this node.
    When resumed, outline_approved will be set by the Streamlit app."""
    return {
        "outline_approved": True,
        "current_agent": "human_review_outline",
    }


def human_review_final_node(state: PipelineState) -> dict:
    """Placeholder node for final human review checkpoint.
    The actual interrupt happens via interrupt_before on this node.
    When resumed, final output is confirmed."""
    return {
        "final_approved": True,
        "final_output": state.get("draft", ""),
        "current_agent": "human_review_final",
    }


def build_graph():
    """Builds and compiles the full pipeline graph."""

    workflow = StateGraph(PipelineState)

    # --- Add all nodes ---
    workflow.add_node("researcher", research_node)
    workflow.add_node("outliner", outline_node)
    workflow.add_node("human_review_outline", human_review_outline_node)
    workflow.add_node("writer", writer_node)
    workflow.add_node("reviewer", reviewer_node)
    workflow.add_node("human_review_final", human_review_final_node)

    # --- Define edges ---

    # START -> researcher -> outliner -> human_review_outline -> writer
    workflow.add_edge(START, "researcher")
    workflow.add_edge("researcher", "outliner")
    workflow.add_edge("outliner", "human_review_outline")
    workflow.add_edge("human_review_outline", "writer")

    # writer -> reviewer (always review after writing)
    workflow.add_edge("writer", "reviewer")

    # reviewer -> conditional: either back to writer (revise) or to final review (approve)
    workflow.add_conditional_edges(
        "reviewer",
        should_revise_or_approve,
        {
            "writer": "writer",                       # revision loop
            "human_review_final": "human_review_final"  # approved
        }
    )

    # human_review_final -> END
    workflow.add_edge("human_review_final", END)

    return workflow


def compile_graph(workflow=None):
    """Compiles the graph with SQLite checkpointing and HITL interrupts."""

    if workflow is None:
        workflow = build_graph()

    # SQLite checkpointer for persistence
    checkpointer = _get_sqlite_saver(CHECKPOINT_DB_PATH)

    # Compile with interrupt points for human-in-the-loop
    graph = workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["human_review_outline", "human_review_final"],
    )

    return graph


def get_graph_config(topic: str, tone: str, target_audience: str):
    """Returns the config dict for a graph run, including LangSmith metadata."""
    import uuid

    thread_id = str(uuid.uuid4())

    return {
        "configurable": {
            "thread_id": thread_id,
        },
        "tags": ["blog-pipeline", "v1"],
        "metadata": {
            "topic": topic,
            "tone": tone,
            "target_audience": target_audience,
            "model": "gpt-4o-mini",
        },
    }
