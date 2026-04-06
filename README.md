# AI Content Pipeline

A multi-agent technical blog post generator built with **LangGraph** (agent orchestration) and **LangSmith** (tracing, evals, monitoring).

## Architecture

A supervisor orchestrates 4 specialized agents — Research, Outline, Writer, Reviewer — to produce polished technical blog posts. Includes human-in-the-loop checkpoints, a revision loop (max 3 cycles), real-time streaming, SQLite persistence, full eval suite, and a Streamlit frontend.

```
User (Streamlit UI)
       │
       ▼
  ┌──────────┐
  │Supervisor │  ← Pure Python routing (no LLM call)
  └─────┬─────┘
       │
       ▼
┌──────────────┐
│Research Agent │  ← Tavily web search → returns facts + source URLs
└───────┬──────┘
       │
       ▼
┌──────────────┐
│Outline Agent │  ← Generates structured blog outline from research
└───────┬──────┘
       │
       ▼
 [HUMAN CHECKPOINT 1]  ← User reviews/edits outline
       │
       ▼
┌──────────────┐
│Writer Agent  │  ← Drafts the blog post
└───────┬──────┘
       │
       ▼
┌───────────────┐
│Reviewer Agent │  ← Scores draft on 5 criteria, returns JSON verdict
└───────┬───────┘
       │
   ┌───┴─────┐
   │Approve? │
   └───┬─────┘
  YES──┴──NO (+ feedback) → back to Writer (max 3 loops)
   │
   ▼
 [HUMAN CHECKPOINT 2]  ← User accepts or requests changes
   │
   ▼
  END
```

## Cost

Uses `gpt-4o-mini` across all agents. Estimated ~$0.01-0.03 per blog post.

## Tech Stack

| Component | Tool |
|-----------|------|
| Agent orchestration | LangGraph |
| Observability + evals | LangSmith |
| LLM | OpenAI `gpt-4o-mini` |
| Web search | Tavily |
| State persistence | SQLite (LangGraph `SqliteSaver`) |
| Frontend | Streamlit |

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with your OPENAI_API_KEY, TAVILY_API_KEY, LANGSMITH_API_KEY

# Create checkpoints directory
mkdir -p checkpoints
```

## Usage

### Run the Streamlit App

```bash
streamlit run app.py
```

### Run Evals

```bash
# Create the eval dataset in LangSmith
python -m evals.dataset

# Run a single experiment
python -m evals.run_experiments

# Run comparison experiments
python -m evals.run_experiments compare
```

## Project Structure

```
ai-content-pipeline/
├── app.py                        # Streamlit frontend
├── src/
│   ├── config.py                 # Model names, max tokens, env loading
│   ├── state.py                  # PipelineState TypedDict
│   ├── graph.py                  # LangGraph graph definition + compilation
│   ├── agents/
│   │   ├── supervisor.py         # Pure Python routing logic
│   │   ├── researcher.py         # Research agent node
│   │   ├── outliner.py           # Outline agent node
│   │   ├── writer.py             # Writer agent node (with revision)
│   │   └── reviewer.py           # Reviewer agent node (JSON scoring)
│   ├── tools/
│   │   └── search.py             # Tavily search tool
│   └── prompts/
│       ├── researcher.py         # Research agent system prompt
│       ├── outliner.py           # Outline agent system prompt
│       ├── writer.py             # Writer agent system prompt
│       └── reviewer.py           # Reviewer agent system prompt
├── evals/
│   ├── dataset.py                # LangSmith eval dataset (10 test cases)
│   ├── evaluators.py             # 5 evaluators (LLM-as-judge + custom)
│   └── run_experiments.py        # Experiment runner + comparison
└── checkpoints/                  # SQLite DB created at runtime
```

## LangGraph Features

- **State management** — `PipelineState` TypedDict shared across all nodes
- **Conditional edges** — Reviewer → Writer or → Final Review
- **Cycles/loops** — Writer ↔ Reviewer revision loop (max 3)
- **Human-in-the-loop** — Two interrupt checkpoints (outline + final)
- **Checkpointing** — SQLite persistence for pause/resume
- **Streaming** — Real-time output to Streamlit UI
- **Tool calling** — Tavily search in research agent

## LangSmith Features

- **Auto-tracing** — All graph runs traced automatically
- **Custom metadata** — Runs tagged with topic, model, tone
- **Eval datasets** — 10 test topics with expected outputs
- **LLM-as-judge** — Quality + tone scoring
- **Custom evaluators** — Word count, section coverage, revision efficiency
- **Comparison experiments** — Side-by-side prompt/config comparison
