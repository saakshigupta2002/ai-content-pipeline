import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Model config
MODEL_NAME = "gpt-4o-mini"
MODEL_TEMPERATURE = 0.7
WRITER_TEMPERATURE = 0.8  # slightly more creative for writing

# Token limits per agent
MAX_TOKENS = {
    "researcher": 800,
    "outliner": 600,
    "writer": 2000,
    "reviewer": 500,
}

# Pipeline config
MAX_REVISIONS = 3
MIN_APPROVAL_SCORE = 7.0  # reviewer must score >= 7.0 to approve

# Tavily config
TAVILY_MAX_RESULTS = 5

# Checkpoint DB path — anchored to project root so it works from any CWD
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHECKPOINT_DB_PATH = str(_PROJECT_ROOT / "checkpoints" / "state.db")

# LangSmith project name — also set as env var so LangSmith SDK picks it up
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "ai-content-pipeline")
os.environ.setdefault("LANGSMITH_PROJECT", LANGSMITH_PROJECT)
