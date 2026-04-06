import streamlit as st
from src.graph import compile_graph, get_graph_config

st.set_page_config(page_title="AI Content Pipeline", page_icon="\ud83d\udcdd", layout="wide")
st.title("\ud83d\udcdd AI Content Pipeline")
st.caption("Multi-agent blog post generator \u2014 LangGraph + LangSmith")

# --- Session State Initialization ---
if "graph" not in st.session_state:
    st.session_state.graph = compile_graph()
if "config" not in st.session_state:
    st.session_state.config = None
if "current_state" not in st.session_state:
    st.session_state.current_state = None
if "stage" not in st.session_state:
    st.session_state.stage = "input"  # input -> running -> outline_review -> writing -> final_review -> done

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
        submitted = st.form_submit_button("\ud83d\ude80 Generate Blog Post")

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
    st.info("\u23f3 Running pipeline: Research \u2192 Outline...")

    graph = st.session_state.graph
    config = st.session_state.config

    # Stream the graph execution — stops at interrupt_before human_review_outline
    with st.spinner("Researching and creating outline..."):
        for event in graph.stream(
            st.session_state.initial_input,
            config=config,
            stream_mode="values",
        ):
            st.session_state.current_state = event

    # After hitting the interrupt_before human_review_outline, we pause
    st.session_state.stage = "outline_review"
    st.rerun()

# --- Outline Review (Human Checkpoint 1) ---
if st.session_state.stage == "outline_review":
    state = st.session_state.current_state

    st.success("\u2705 Research complete!")

    with st.expander("\ud83d\udd0d Research Findings", expanded=False):
        st.markdown(state.get("research_results", ""))
        if state.get("sources"):
            st.markdown("**Sources:**")
            for url in state["sources"]:
                st.markdown(f"- {url}")

    st.subheader("\ud83d\udccb Proposed Outline")
    st.markdown(state.get("outline", ""))

    col1, col2 = st.columns(2)
    with col1:
        if st.button("\u2705 Approve Outline", type="primary"):
            graph = st.session_state.graph
            config = st.session_state.config

            # Update graph state to mark outline as approved before resuming
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
        if st.button("\u270f\ufe0f Use Edited Outline"):
            graph = st.session_state.graph
            config = st.session_state.config

            # Update state with edited outline and mark approved
            graph.update_state(
                config,
                {"outline": edited_outline, "outline_approved": True}
            )
            st.session_state.stage = "writing"
            st.rerun()

# --- Writing + Review Phase (with token-level streaming for writer) ---
if st.session_state.stage == "writing":
    st.info("\u270d\ufe0f Writing blog post...")

    graph = st.session_state.graph
    config = st.session_state.config

    # Resume graph from the outline interrupt.
    # Stream node-level state values and show draft + review status in real-time.
    draft_container = st.empty()
    status_container = st.empty()

    with st.spinner("Writing and reviewing..."):
        for event in graph.stream(
            None,  # None = resume from interrupt
            config=config,
            stream_mode="values",
        ):
            st.session_state.current_state = event

            current_agent = event.get("current_agent", "")

            if current_agent == "writer":
                # Show the full draft as it arrives from this node
                draft_text = event.get("draft", "")
                revision = event.get("revision_count", 0)
                draft_container.markdown(
                    f"**Draft (revision {revision}):**\n\n{draft_text[:800]}{'...' if len(draft_text) > 800 else ''}"
                )
            elif current_agent == "reviewer":
                score = event.get("review_score", 0)
                approved = event.get("review_approved", False)
                if approved:
                    status_container.success(f"\u2705 Reviewer approved! Score: {score}/10")
                else:
                    revision = event.get("revision_count", 0)
                    status_container.warning(
                        f"\ud83d\udd04 Revision {revision} needed. Score: {score}/10 \u2014 sending back to writer..."
                    )
                    # Clear draft container for next revision
                    draft_container.empty()

    st.session_state.stage = "final_review"
    st.rerun()

# --- Final Review (Human Checkpoint 2) ---
if st.session_state.stage == "final_review":
    state = st.session_state.current_state

    st.subheader("\ud83d\udcf0 Final Blog Post")

    # Show review stats
    col1, col2, col3 = st.columns(3)
    col1.metric("Review Score", f"{state.get('review_score', 0)}/10")
    col2.metric("Revisions", state.get("revision_count", 0))
    col3.metric("Status", "\u2705 Approved" if state.get("review_approved") else "\u26a0\ufe0f Max revisions reached")

    # Show the draft
    st.markdown("---")
    st.markdown(state.get("draft", ""))
    st.markdown("---")

    # Show sources
    with st.expander("\ud83d\udcda Sources"):
        for url in state.get("sources", []):
            st.markdown(f"- {url}")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("\u2705 Approve & Finalize", type="primary"):
            graph = st.session_state.graph
            config = st.session_state.config

            # Resume from final interrupt
            for event in graph.stream(None, config=config, stream_mode="values"):
                st.session_state.current_state = event

            st.session_state.stage = "done"
            st.rerun()

    with col2:
        if st.button("\u270f\ufe0f Edit Draft Manually"):
            st.session_state.stage = "manual_edit"
            st.rerun()

    with col3:
        if st.button("\ud83d\udd0d View in LangSmith"):
            st.markdown("[Open in LangSmith](https://smith.langchain.com/)")

# --- Manual Edit (optional path from final_review) ---
if st.session_state.stage == "manual_edit":
    state = st.session_state.current_state

    st.subheader("\u270f\ufe0f Edit Draft")
    edited_draft = st.text_area(
        "Make your changes below:",
        value=state.get("draft", ""),
        height=500,
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("\u2705 Save & Finalize", type="primary"):
            graph = st.session_state.graph
            config = st.session_state.config

            # Update the draft in graph state with user's edits, then resume
            graph.update_state(
                config,
                {"draft": edited_draft, "final_approved": True, "final_output": edited_draft}
            )

            for event in graph.stream(None, config=config, stream_mode="values"):
                st.session_state.current_state = event

            # Ensure final_output reflects the edit even if the node overwrote it
            st.session_state.current_state["final_output"] = edited_draft
            st.session_state.stage = "done"
            st.rerun()

    with col2:
        if st.button("\u274c Cancel"):
            st.session_state.stage = "final_review"
            st.rerun()

# --- Done ---
if st.session_state.stage == "done":
    state = st.session_state.current_state

    st.balloons()
    st.success("\ud83c\udf89 Blog post finalized!")
    st.markdown(state.get("final_output", state.get("draft", "")))

    # Copy button
    st.code(state.get("final_output", state.get("draft", "")), language="markdown")

    if st.button("\ud83d\udd04 Start New Post"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
