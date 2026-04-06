import streamlit as st
from src.graph import compile_graph, get_graph_config

st.set_page_config(page_title="AI Content Pipeline", page_icon="pencil", layout="wide")
st.title("AI Content Pipeline")
st.caption("Multi-agent blog post generator -- LangGraph + LangSmith")

# --- Session State Initialization ---
if "graph" not in st.session_state:
    st.session_state.graph = compile_graph()
if "config" not in st.session_state:
    st.session_state.config = None
if "current_state" not in st.session_state:
    st.session_state.current_state = None
if "stage" not in st.session_state:
    st.session_state.stage = "input"

# --- Input Form ---
if st.session_state.stage == "input":
    with st.form("blog_input"):
        topic = st.text_input("Blog Topic", placeholder="e.g., Introduction to Vector Databases")
        target_audience = st.selectbox(
            "Target Audience",
            ["beginner developers", "intermediate developers", "senior engineers", "ML engineers", "non-technical"]
        )
        tone = st.selectbox(
            "Tone",
            ["casual-technical", "formal-technical", "tutorial", "opinionated", "explanatory"]
        )
        submitted = st.form_submit_button("Generate Blog Post")

    if submitted and topic:
        st.session_state.config = get_graph_config(topic, tone, target_audience)
        st.session_state.initial_input = {
            "topic": topic,
            "target_audience": target_audience,
            "tone": tone,
            "research_results": "",
            "sources": [],
            "outline": "",
            "outline_approved": False,
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
        st.session_state.stage = "running"
        st.rerun()

# --- Pipeline Execution (Research + Outline) ---
if st.session_state.stage == "running":
    st.info("Running pipeline: Research -> Outline...")

    graph = st.session_state.graph
    config = st.session_state.config

    with st.spinner("Researching and creating outline..."):
        for event in graph.stream(
            st.session_state.initial_input,
            config=config,
            stream_mode="values",
        ):
            st.session_state.current_state = event

    st.session_state.stage = "outline_review"
    st.rerun()

# --- Outline Review (Human Checkpoint 1) ---
if st.session_state.stage == "outline_review":
    state = st.session_state.current_state

    st.success("Research complete!")

    with st.expander("Research Findings", expanded=False):
        st.markdown(state.get("research_results", ""))
        if state.get("sources"):
            st.markdown("**Sources:**")
            for url in state["sources"]:
                st.markdown(f"- {url}")

    st.subheader("Proposed Outline")
    st.markdown(state.get("outline", ""))

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Approve Outline", type="primary"):
            graph = st.session_state.graph
            config = st.session_state.config

            graph.update_state(
                config,
                {"outline_approved": True}
            )

            st.session_state.stage = "writing"
            st.rerun()

    with col2:
        edited_outline = st.text_area(
            "Or edit the outline:",
            value=state.get("outline", ""),
            height=300
        )
        if st.button("Use Edited Outline"):
            graph = st.session_state.graph
            config = st.session_state.config

            graph.update_state(
                config,
                {"outline": edited_outline, "outline_approved": True}
            )
            st.session_state.stage = "writing"
            st.rerun()

# --- Writing + Review Phase ---
if st.session_state.stage == "writing":
    st.info("Writing blog post...")

    graph = st.session_state.graph
    config = st.session_state.config

    draft_container = st.empty()
    status_container = st.empty()

    with st.spinner("Writing and reviewing..."):
        for event in graph.stream(
            None,
            config=config,
            stream_mode="values",
        ):
            st.session_state.current_state = event

            current_agent = event.get("current_agent", "")

            if current_agent == "writer":
                draft_text = event.get("draft", "")
                revision = event.get("revision_count", 0)
                draft_container.markdown(
                    f"**Draft (revision {revision}):**\n\n{draft_text[:800]}{'...' if len(draft_text) > 800 else ''}"
                )
            elif current_agent == "reviewer":
                score = event.get("review_score", 0)
                approved = event.get("review_approved", False)
                if approved:
                    status_container.success(f"Reviewer approved! Score: {score}/10")
                else:
                    revision = event.get("revision_count", 0)
                    status_container.warning(
                        f"Revision {revision} needed. Score: {score}/10 -- sending back to writer..."
                    )
                    draft_container.empty()

    st.session_state.stage = "final_review"
    st.rerun()

# --- Final Review (Human Checkpoint 2) ---
if st.session_state.stage == "final_review":
    state = st.session_state.current_state

    st.subheader("Final Blog Post")

    col1, col2, col3 = st.columns(3)
    col1.metric("Review Score", f"{state.get('review_score', 0)}/10")
    col2.metric("Revisions", state.get("revision_count", 0))
    col3.metric("Status", "Approved" if state.get("review_approved") else "Max revisions reached")

    st.markdown("---")
    st.markdown(state.get("draft", ""))
    st.markdown("---")

    with st.expander("Sources"):
        for url in state.get("sources", []):
            st.markdown(f"- {url}")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Approve & Finalize", type="primary"):
            graph = st.session_state.graph
            config = st.session_state.config

            for event in graph.stream(None, config=config, stream_mode="values"):
                st.session_state.current_state = event

            st.session_state.stage = "done"
            st.rerun()

    with col2:
        if st.button("Edit Draft Manually"):
            st.session_state.stage = "manual_edit"
            st.rerun()

    with col3:
        if st.button("View in LangSmith"):
            st.markdown("[Open in LangSmith](https://smith.langchain.com/)")

# --- Manual Edit (optional path from final_review) ---
if st.session_state.stage == "manual_edit":
    state = st.session_state.current_state

    st.subheader("Edit Draft")
    edited_draft = st.text_area(
        "Make your changes below:",
        value=state.get("draft", ""),
        height=500,
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save & Finalize", type="primary"):
            graph = st.session_state.graph
            config = st.session_state.config

            graph.update_state(
                config,
                {"draft": edited_draft, "final_approved": True, "final_output": edited_draft}
            )

            for event in graph.stream(None, config=config, stream_mode="values"):
                st.session_state.current_state = event

            st.session_state.current_state["final_output"] = edited_draft
            st.session_state.stage = "done"
            st.rerun()

    with col2:
        if st.button("Cancel"):
            st.session_state.stage = "final_review"
            st.rerun()

# --- Done ---
if st.session_state.stage == "done":
    state = st.session_state.current_state

    st.balloons()
    st.success("Blog post finalized!")
    st.markdown(state.get("final_output", state.get("draft", "")))

    st.code(state.get("final_output", state.get("draft", "")), language="markdown")

    if st.button("Start New Post"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
