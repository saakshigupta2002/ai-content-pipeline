"""Custom evaluators for LangSmith experiments."""

from langsmith.schemas import Example, Run
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import json


# --- LLM-as-Judge Evaluator ---

def quality_evaluator(run: Run, example: Example) -> dict:
    """Uses gpt-4o-mini as a judge to score blog quality."""

    draft = run.outputs.get("final_output", run.outputs.get("draft", ""))

    if not draft:
        return {"key": "quality", "score": 0.0, "comment": "No output produced"}

    judge_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_tokens=500)

    judge_prompt = f"""Rate this technical blog post on a scale of 0.0 to 1.0 for overall quality.
Consider: clarity, technical accuracy, engagement, structure, and usefulness.

Topic: {example.inputs.get('topic', '')}
Target audience: {example.inputs.get('target_audience', '')}
Expected tone: {example.inputs.get('tone', '')}

Blog post:
{draft[:3000]}

Respond with ONLY a JSON object:
{{"score": <0.0-1.0>, "reasoning": "<brief explanation>"}}
"""

    response = judge_llm.invoke([HumanMessage(content=judge_prompt)])

    try:
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0]
        result = json.loads(content)
        return {
            "key": "quality",
            "score": float(result.get("score", 0.5)),
            "comment": result.get("reasoning", ""),
        }
    except Exception:
        return {"key": "quality", "score": 0.5, "comment": "Judge parsing failed"}


# --- Word Count Evaluator ---

def word_count_evaluator(run: Run, example: Example) -> dict:
    """Checks if the blog meets minimum word count."""

    draft = run.outputs.get("final_output", run.outputs.get("draft", ""))
    if not draft:
        return {"key": "word_count", "score": 0.0}

    word_count = len(draft.split())
    min_count = example.outputs.get("min_word_count", 800) if example.outputs else 800

    score = min(1.0, word_count / min_count)
    return {
        "key": "word_count",
        "score": score,
        "comment": f"{word_count} words (target: {min_count}+)",
    }


# --- Section Coverage Evaluator ---

def section_coverage_evaluator(run: Run, example: Example) -> dict:
    """Checks if the blog covers expected sections from the test case."""

    draft = run.outputs.get("final_output", run.outputs.get("draft", ""))
    if not draft:
        return {"key": "section_coverage", "score": 0.0}

    expected_sections = example.outputs.get("expected_sections", []) if example.outputs else []
    if not expected_sections:
        return {"key": "section_coverage", "score": 1.0, "comment": "No expected sections defined"}

    draft_lower = draft.lower()
    found = sum(1 for section in expected_sections if section.lower() in draft_lower)

    score = found / len(expected_sections)
    return {
        "key": "section_coverage",
        "score": score,
        "comment": f"Found {found}/{len(expected_sections)} expected sections",
    }


# --- Revision Efficiency Evaluator ---

def revision_efficiency_evaluator(run: Run, example: Example) -> dict:
    """Scores how efficiently the pipeline produced an approved draft.
    Fewer revisions = higher score."""

    revision_count = run.outputs.get("revision_count", 0)
    # 0 revisions = 1.0, 1 = 0.75, 2 = 0.5, 3 = 0.25
    score = max(0.0, 1.0 - (revision_count * 0.25))
    return {
        "key": "revision_efficiency",
        "score": score,
        "comment": f"{revision_count} revisions needed",
    }


# --- Tone Match Evaluator ---

def tone_match_evaluator(run: Run, example: Example) -> dict:
    """Uses LLM to check if the blog matches the requested tone."""

    draft = run.outputs.get("final_output", run.outputs.get("draft", ""))
    expected_tone = example.inputs.get("tone", "")

    if not draft or not expected_tone:
        return {"key": "tone_match", "score": 0.5}

    judge_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_tokens=200)

    prompt = f"""Does this blog post match the requested tone of "{expected_tone}"?
Score from 0.0 (completely wrong tone) to 1.0 (perfect tone match).

First 1500 chars of the blog:
{draft[:1500]}

Respond with ONLY: {{"score": <0.0-1.0>, "reasoning": "<brief>"}}
"""

    response = judge_llm.invoke([HumanMessage(content=prompt)])

    try:
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0]
        result = json.loads(content)
        return {
            "key": "tone_match",
            "score": float(result.get("score", 0.5)),
            "comment": result.get("reasoning", ""),
        }
    except Exception:
        return {"key": "tone_match", "score": 0.5, "comment": "Tone judge parsing failed"}
