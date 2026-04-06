import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.config import MODEL_NAME, MAX_TOKENS, MIN_APPROVAL_SCORE
from src.prompts.reviewer import REVIEWER_SYSTEM_PROMPT
from src.state import PipelineState


def reviewer_node(state: PipelineState) -> dict:
    """Reviewer agent: evaluates draft and returns structured JSON verdict."""

    llm = ChatOpenAI(
        model=MODEL_NAME,
        temperature=0.3,  # lower temp for consistent scoring
        max_tokens=MAX_TOKENS["reviewer"],
    )

    prompt = REVIEWER_SYSTEM_PROMPT.format(
        tone=state["tone"],
        target_audience=state["target_audience"],
        outline=state["outline"],
        research_results=state["research_results"],
        draft=state["draft"],
    )

    response = llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content="Review the draft above and return your JSON verdict."),
    ])

    # Parse the JSON response
    try:
        # Clean potential markdown code fences
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1]  # remove first line
            content = content.rsplit("```", 1)[0]  # remove last fence
        review = json.loads(content)
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        review = {
            "scores": {"clarity": 5, "accuracy": 5, "completeness": 5, "tone": 5, "engagement": 5},
            "overall_score": 5.0,
            "approved": False,
            "feedback": f"Review parsing failed. Raw response: {response.content[:200]}"
        }

    # Enforce MIN_APPROVAL_SCORE — override LLM's approved field
    overall_score = review.get("overall_score", 5.0)
    approved = overall_score >= MIN_APPROVAL_SCORE

    return {
        "review_score": overall_score,
        "review_feedback": review.get("feedback", ""),
        "review_approved": approved,
        "current_agent": "reviewer",
    }
