from src.state import PipelineState
from src.config import MAX_REVISIONS


def should_revise_or_approve(state: PipelineState) -> str:
    """
    Conditional edge after reviewer: revise or approve?
    This is the key conditional edge that creates the Writer <-> Reviewer cycle.
    """

    if state.get("review_approved", False):
        return "human_review_final"

    if state.get("revision_count", 0) >= MAX_REVISIONS:
        # Hit max revisions — force approve and go to human review
        return "human_review_final"

    # Not approved and under revision limit — send back to writer
    return "writer"
