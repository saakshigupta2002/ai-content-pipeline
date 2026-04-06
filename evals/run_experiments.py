"""Run LangSmith evaluation experiments and comparisons."""

from langsmith import evaluate
from src.graph import build_graph, get_graph_config, _get_sqlite_saver
from evals.evaluators import (
    quality_evaluator,
    word_count_evaluator,
    section_coverage_evaluator,
    revision_efficiency_evaluator,
    tone_match_evaluator,
)


ALL_EVALUATORS = [
    quality_evaluator,
    word_count_evaluator,
    section_coverage_evaluator,
    revision_efficiency_evaluator,
    tone_match_evaluator,
]


def pipeline_target(inputs: dict) -> dict:
    """Target function for LangSmith evaluate().
    Runs the full pipeline end-to-end for a given input (no HITL — auto-approve)."""

    workflow = build_graph()

    # For evals, compile WITHOUT interrupts (auto-approve everything)
    # Use in-memory SQLite so each eval run is isolated
    checkpointer = _get_sqlite_saver(":memory:")
    graph = workflow.compile(checkpointer=checkpointer)

    initial_state = {
        "topic": inputs["topic"],
        "target_audience": inputs["target_audience"],
        "tone": inputs["tone"],
        "research_results": "",
        "sources": [],
        "outline": "",
        "outline_approved": True,   # auto-approve for evals
        "draft": "",
        "revision_count": 0,
        "review_score": 0.0,
        "review_feedback": "",
        "review_approved": False,
        "final_approved": False,
        "final_output": "",
        "current_agent": "",
        "messages": [],
    }

    config = get_graph_config(
        inputs["topic"], inputs["tone"], inputs["target_audience"]
    )
    config["tags"].append("eval-run")

    result = graph.invoke(initial_state, config=config)

    return {
        "final_output": result.get("final_output", result.get("draft", "")),
        "revision_count": result.get("revision_count", 0),
        "review_score": result.get("review_score", 0.0),
        "draft": result.get("draft", ""),
    }


def run_experiment(experiment_prefix: str = "v1-baseline"):
    """Run a single experiment against the eval dataset."""

    results = evaluate(
        pipeline_target,
        data="blog-pipeline-eval",
        evaluators=ALL_EVALUATORS,
        experiment_prefix=experiment_prefix,
        max_concurrency=2,  # keep costs predictable
    )

    print(f"\nExperiment '{experiment_prefix}' complete!")
    print(f"View results at: https://smith.langchain.com/")
    return results


def run_comparison():
    """Run multiple experiments for side-by-side comparison in LangSmith."""

    print("Running Experiment 1: Baseline (default prompts)...")
    run_experiment("v1-baseline")

    # To run comparisons with different configs, modify prompts or config
    # between calls. For example:
    #
    # print("Running Experiment 2: Lower temperature writer...")
    # import src.config as cfg
    # cfg.WRITER_TEMPERATURE = 0.5
    # run_experiment("v2-low-temp-writer")
    #
    # print("Running Experiment 3: Stricter reviewer threshold...")
    # cfg.MIN_APPROVAL_SCORE = 8.0
    # run_experiment("v3-strict-reviewer")

    print("\nAll experiments complete!")
    print("Compare them side-by-side in LangSmith's Comparison View.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "compare":
        run_comparison()
    else:
        run_experiment()
