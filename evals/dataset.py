"""Creates the LangSmith evaluation dataset."""

from langsmith import Client


def create_eval_dataset():
    client = Client()

    dataset_name = "blog-pipeline-eval"

    # Delete if exists (for clean re-creation)
    try:
        existing = client.read_dataset(dataset_name=dataset_name)
        client.delete_dataset(dataset_id=existing.id)
    except Exception:
        pass

    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description="Test cases for the AI Content Pipeline blog generator"
    )

    test_cases = [
        {
            "inputs": {
                "topic": "Introduction to Vector Databases for Beginners",
                "target_audience": "beginner developers",
                "tone": "casual-technical",
            },
            "outputs": {
                "expected_sections": ["what is a vector database", "embeddings", "use cases", "getting started"],
                "min_word_count": 800,
                "expected_tone": "casual-technical",
            }
        },
        {
            "inputs": {
                "topic": "RAG vs Fine-tuning: When to Use What in 2025",
                "target_audience": "ML engineers",
                "tone": "formal-technical",
            },
            "outputs": {
                "expected_sections": ["rag overview", "fine-tuning overview", "comparison", "decision framework"],
                "min_word_count": 800,
                "expected_tone": "formal-technical",
            }
        },
        {
            "inputs": {
                "topic": "Building Your First LangGraph Agent",
                "target_audience": "intermediate developers",
                "tone": "tutorial",
            },
            "outputs": {
                "expected_sections": ["what is langgraph", "setup", "building the graph", "adding tools"],
                "min_word_count": 800,
                "expected_tone": "tutorial",
            }
        },
        {
            "inputs": {
                "topic": "Why Prompt Engineering Still Matters in the Age of Agents",
                "target_audience": "senior engineers",
                "tone": "opinionated",
            },
            "outputs": {
                "expected_sections": ["prompt engineering basics", "agents", "why prompts matter", "best practices"],
                "min_word_count": 800,
                "expected_tone": "opinionated",
            }
        },
        {
            "inputs": {
                "topic": "Understanding Transformer Attention Mechanisms",
                "target_audience": "ML engineers",
                "tone": "explanatory",
            },
            "outputs": {
                "expected_sections": ["attention", "self-attention", "multi-head", "applications"],
                "min_word_count": 800,
                "expected_tone": "explanatory",
            }
        },
        {
            "inputs": {
                "topic": "Docker for Machine Learning Engineers",
                "target_audience": "ML engineers",
                "tone": "tutorial",
            },
            "outputs": {
                "expected_sections": ["why docker", "dockerfile", "gpu support", "best practices"],
                "min_word_count": 800,
                "expected_tone": "tutorial",
            }
        },
        {
            "inputs": {
                "topic": "GraphRAG Explained: Knowledge Graphs Meet Retrieval",
                "target_audience": "intermediate developers",
                "tone": "casual-technical",
            },
            "outputs": {
                "expected_sections": ["what is graphrag", "knowledge graphs", "implementation", "use cases"],
                "min_word_count": 800,
                "expected_tone": "casual-technical",
            }
        },
        {
            "inputs": {
                "topic": "MCP Servers: The Future of Tool Integration for AI Agents",
                "target_audience": "senior engineers",
                "tone": "formal-technical",
            },
            "outputs": {
                "expected_sections": ["what is mcp", "architecture", "building servers", "ecosystem"],
                "min_word_count": 800,
                "expected_tone": "formal-technical",
            }
        },
        {
            "inputs": {
                "topic": "How to Evaluate LLM Applications Properly",
                "target_audience": "intermediate developers",
                "tone": "explanatory",
            },
            "outputs": {
                "expected_sections": ["why evaluation matters", "types of evals", "llm as judge", "best practices"],
                "min_word_count": 800,
                "expected_tone": "explanatory",
            }
        },
        {
            "inputs": {
                "topic": "Multi-Agent Systems: Patterns and Pitfalls",
                "target_audience": "senior engineers",
                "tone": "opinionated",
            },
            "outputs": {
                "expected_sections": ["why multi-agent", "patterns", "pitfalls", "when not to use"],
                "min_word_count": 800,
                "expected_tone": "opinionated",
            }
        },
    ]

    for case in test_cases:
        client.create_example(
            inputs=case["inputs"],
            outputs=case["outputs"],
            dataset_id=dataset.id,
        )

    print(f"Created dataset '{dataset_name}' with {len(test_cases)} examples.")
    return dataset


if __name__ == "__main__":
    create_eval_dataset()
