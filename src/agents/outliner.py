from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.config import MODEL_NAME, MAX_TOKENS, MODEL_TEMPERATURE
from src.prompts.outliner import OUTLINER_SYSTEM_PROMPT
from src.state import PipelineState


def outline_node(state: PipelineState) -> dict:
    """Outline agent: creates structured blog outline from research."""

    llm = ChatOpenAI(
        model=MODEL_NAME,
        temperature=MODEL_TEMPERATURE,
        max_tokens=MAX_TOKENS["outliner"],
    )

    prompt = OUTLINER_SYSTEM_PROMPT.format(
        target_audience=state["target_audience"],
        tone=state["tone"],
    )

    response = llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=(
            f"Topic: {state['topic']}\n\n"
            f"Research Findings:\n{state['research_results']}"
        ))
    ])

    return {
        "outline": response.content,
        "current_agent": "outliner",
    }
