from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.config import MODEL_NAME, MAX_TOKENS, WRITER_TEMPERATURE
from src.prompts.writer import WRITER_SYSTEM_PROMPT, WRITER_REVISION_PROMPT
from src.state import PipelineState


def writer_node(state: PipelineState) -> dict:
    """Writer agent: drafts or revises the blog post."""

    llm = ChatOpenAI(
        model=MODEL_NAME,
        temperature=WRITER_TEMPERATURE,
        max_tokens=MAX_TOKENS["writer"],
    )

    revision_count = state.get("revision_count", 0)

    if revision_count == 0:
        # First draft
        prompt = WRITER_SYSTEM_PROMPT.format(
            tone=state["tone"],
            target_audience=state["target_audience"],
            outline=state["outline"],
            research_results=state["research_results"],
        )
        human_msg = "Write the complete blog post following the outline and research above."
    else:
        # Revision
        prompt = WRITER_REVISION_PROMPT.format(
            revision_count=revision_count,
            review_feedback=state.get("review_feedback", ""),
            draft=state.get("draft", ""),
            outline=state["outline"],
            research_results=state["research_results"],
        )
        human_msg = f"Revise the draft addressing the feedback. This is revision #{revision_count}."

    response = llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=human_msg),
    ])

    return {
        "draft": response.content,
        "revision_count": revision_count + 1,
        "current_agent": "writer",
        "review_approved": False,  # reset review status for new draft
    }
