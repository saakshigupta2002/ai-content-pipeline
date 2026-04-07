import streamlit as st
from src.graph import compile_graph, get_graph_config

st.set_page_config(
    page_title="AI Content Pipeline",
    page_icon="https://em-content.zobj.net/source/apple/391/memo_1f4dd.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- Custom CSS ---
st.markdown("""
<style>
    /* === Global === */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Hide default Streamlit chrome */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* === Main container === */
    .block-container {
        max-width: 900px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* === Typography === */
    h1 {
        font-weight: 700 !important;
        font-size: 2.2rem !important;
        letter-spacing: -0.03em !important;
        margin-bottom: 0 !important;
    }
    h2 {
        font-weight: 600 !important;
        font-size: 1.4rem !important;
        letter-spacing: -0.02em !important;
    }
    h3 {
        font-weight: 500 !important;
        font-size: 1.1rem !important;
    }
    p, li, span {
        font-size: 0.95rem;
        line-height: 1.7;
    }

    /* === Stage indicator === */
    .stage-bar {
        display: flex;
        gap: 0;
        margin: 1.5rem 0 2rem 0;
        border-radius: 6px;
        overflow: hidden;
        border: 1px solid #222;
    }
    .stage-step {
        flex: 1;
        text-align: center;
        padding: 10px 0;
        font-size: 0.75rem;
        font-weight: 500;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        color: #555;
        background: #0F0F0F;
        border-right: 1px solid #222;
        transition: all 0.3s ease;
    }
    .stage-step:last-child { border-right: none; }
    .stage-step.active {
        background: #FFFFFF;
        color: #000000;
        font-weight: 600;
    }
    .stage-step.done {
        background: #1A1A1A;
        color: #888;
    }

    /* === Cards === */
    .metric-card {
        background: #111;
        border: 1px solid #222;
        border-radius: 8px;
        padding: 1.2rem;
        text-align: center;
    }
    .metric-card .metric-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #666;
        margin-bottom: 6px;
    }
    .metric-card .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #FFF;
    }

    /* === Content container === */
    .content-box {
        background: #0F0F0F;
        border: 1px solid #1E1E1E;
        border-radius: 8px;
        padding: 2rem;
        margin: 1rem 0;
        line-height: 1.8;
        position: relative;
        z-index: 1;
        overflow-wrap: break-word;
        white-space: pre-wrap;
    }

    /* === Source pills === */
    .source-pill {
        display: inline-block;
        background: #1A1A1A;
        border: 1px solid #2A2A2A;
        border-radius: 20px;
        padding: 4px 14px;
        margin: 3px 4px;
        font-size: 0.75rem;
        color: #999;
        text-decoration: none;
        transition: all 0.2s ease;
        position: relative;
        z-index: 1;
    }
    .source-pill:hover {
        background: #222;
        color: #FFF;
        border-color: #444;
    }

    /* === Buttons === */
    .stButton > button {
        border: 1px solid #333 !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.02em !important;
        padding: 0.5rem 1.5rem !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button[kind="primary"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-color: #FFFFFF !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #E0E0E0 !important;
    }
    .stButton > button[kind="secondary"] {
        background-color: transparent !important;
        color: #AAA !important;
        border-color: #333 !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background-color: #1A1A1A !important;
        color: #FFF !important;
    }

    /* === Form submit button === */
    .stFormSubmitButton > button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #FFFFFF !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.02em !important;
        padding: 0.5rem 1.5rem !important;
        transition: all 0.2s ease !important;
    }
    .stFormSubmitButton > button:hover {
        background-color: #E0E0E0 !important;
        color: #000000 !important;
    }

    /* === Form === */
    .stTextInput > div > div > input {
        background: #111 !important;
        border: 1px solid #222 !important;
        border-radius: 6px !important;
        color: #FFF !important;
        font-size: 0.95rem !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #555 !important;
        box-shadow: none !important;
    }
    .stSelectbox > div > div {
        background: #111 !important;
        border: 1px solid #222 !important;
        border-radius: 6px !important;
    }
    .stTextArea > div > div > textarea {
        background: #111 !important;
        border: 1px solid #222 !important;
        border-radius: 6px !important;
        color: #FFF !important;
    }

    /* === Alerts === */
    .stAlert > div {
        border-radius: 6px !important;
        border: 1px solid #222 !important;
    }

    /* === Expander === */
    .streamlit-expanderHeader {
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        color: #888 !important;
    }

    /* === Divider === */
    hr {
        border-color: #1A1A1A !important;
        margin: 1.5rem 0 !important;
    }

    /* === Spinner === */
    .stSpinner > div {
        border-top-color: #FFF !important;
    }

    /* === Caption === */
    .caption-text {
        color: #555;
        font-size: 0.8rem;
        letter-spacing: 0.03em;
    }
</style>
""", unsafe_allow_html=True)


# --- Helpers ---
def render_stage_bar(current_stage):
    stages = ["Input", "Research", "Outline Review", "Writing", "Final Review", "Done"]
    stage_map = {
        "input": 0, "running": 1, "outline_review": 2,
        "writing": 3, "final_review": 4, "manual_edit": 4, "done": 5,
    }
    current_idx = stage_map.get(current_stage, 0)
    steps_html = ""
    for i, name in enumerate(stages):
        if i < current_idx:
            cls = "stage-step done"
        elif i == current_idx:
            cls = "stage-step active"
        else:
            cls = "stage-step"
        steps_html += f'<div class="{cls}">{name}</div>'
    st.markdown(f'<div class="stage-bar">{steps_html}</div>', unsafe_allow_html=True)


def render_metric_cards(metrics):
    cols = st.columns(len(metrics))
    for col, (label, value) in zip(cols, metrics):
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """, unsafe_allow_html=True)


def render_sources(sources):
    if not sources:
        return
    pills = ""
    for url in sources:
        domain = url.split("//")[-1].split("/")[0] if "//" in url else url[:30]
        pills += f'<a href="{url}" target="_blank" class="source-pill">{domain}</a>'
    st.markdown(f"<div style='margin: 1rem 0;'>{pills}</div>", unsafe_allow_html=True)


# --- Session State ---
if "graph" not in st.session_state:
    st.session_state.graph = compile_graph()
if "config" not in st.session_state:
    st.session_state.config = None
if "current_state" not in st.session_state:
    st.session_state.current_state = None
if "stage" not in st.session_state:
    st.session_state.stage = "input"

# --- Header ---
st.markdown("# AI Content Pipeline")
st.markdown('<p class="caption-text">Multi-agent blog post generator &mdash; LangGraph + LangSmith</p>', unsafe_allow_html=True)

# --- Stage Bar ---
render_stage_bar(st.session_state.stage)

# =============================================
# STAGE: INPUT
# =============================================
if st.session_state.stage == "input":
    st.markdown("### Configure your blog post")
    st.markdown('<p class="caption-text">The pipeline will research, outline, write, and review your post automatically.</p>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    with st.form("blog_input"):
        topic = st.text_input("Topic", placeholder="e.g., Introduction to Vector Databases")
        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            target_audience = st.selectbox(
                "Target Audience",
                ["beginner developers", "intermediate developers", "senior engineers", "ML engineers", "non-technical"]
            )
        with col2:
            tone = st.selectbox(
                "Tone",
                ["casual-technical", "formal-technical", "tutorial", "opinionated", "explanatory"]
            )

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Generate", type="primary", use_container_width=True)

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

# =============================================
# STAGE: RUNNING
# =============================================
if st.session_state.stage == "running":
    graph = st.session_state.graph
    config = st.session_state.config

    with st.spinner("Researching topic and generating outline..."):
        for event in graph.stream(
            st.session_state.initial_input,
            config=config,
            stream_mode="values",
        ):
            st.session_state.current_state = event

    st.session_state.stage = "outline_review"
    st.rerun()

# =============================================
# STAGE: OUTLINE REVIEW
# =============================================
if st.session_state.stage == "outline_review":
    state = st.session_state.current_state

    st.markdown("### Review the outline")
    st.markdown('<p class="caption-text">The research is complete. Review the proposed outline below, then approve or edit it.</p>', unsafe_allow_html=True)

    # Sources
    with st.expander("View research findings & sources", expanded=False):
        st.markdown(state.get("research_results", ""))
        render_sources(state.get("sources", []))

    # Outline display + edit in tabs
    tab_view, tab_edit = st.tabs(["Outline", "Edit Outline"])

    with tab_view:
        st.markdown(f'<div class="content-box">{state.get("outline", "")}</div>', unsafe_allow_html=True)

    with tab_edit:
        edited_outline = st.text_area(
            "Modify the outline as needed:",
            value=state.get("outline", ""),
            height=400,
            label_visibility="collapsed",
        )

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("Approve Outline", type="primary", use_container_width=True):
            graph = st.session_state.graph
            config = st.session_state.config
            graph.update_state(config, {"outline_approved": True})
            st.session_state.stage = "writing"
            st.rerun()
    with col2:
        if st.button("Use Edited Version", use_container_width=True):
            graph = st.session_state.graph
            config = st.session_state.config
            graph.update_state(config, {"outline": edited_outline, "outline_approved": True})
            st.session_state.stage = "writing"
            st.rerun()

# =============================================
# STAGE: WRITING
# =============================================
if st.session_state.stage == "writing":
    graph = st.session_state.graph
    config = st.session_state.config

    st.markdown("### Writing in progress")
    st.markdown('<p class="caption-text">The writer agent is drafting your post. The reviewer will score it and request revisions if needed.</p>', unsafe_allow_html=True)

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
                    f'<div class="content-box"><strong style="color:#666;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em;">Draft &middot; Revision {revision}</strong><br><br>{draft_text[:1000]}{"..." if len(draft_text) > 1000 else ""}</div>',
                    unsafe_allow_html=True,
                )
            elif current_agent == "reviewer":
                score = event.get("review_score", 0)
                approved = event.get("review_approved", False)
                if approved:
                    status_container.success(f"Approved with score {score}/10")
                else:
                    revision = event.get("revision_count", 0)
                    status_container.warning(f"Score {score}/10 -- revision {revision} in progress...")
                    draft_container.empty()

    st.session_state.stage = "final_review"
    st.rerun()

# =============================================
# STAGE: FINAL REVIEW
# =============================================
if st.session_state.stage == "final_review":
    state = st.session_state.current_state

    st.markdown("### Final review")
    st.markdown('<p class="caption-text">Your blog post is ready. Review the final draft below.</p>', unsafe_allow_html=True)

    # Metrics
    score = state.get("review_score", 0)
    revisions = state.get("revision_count", 0)
    word_count = len(state.get("draft", "").split())
    status = "Approved" if state.get("review_approved") else "Max revisions"
    render_metric_cards([
        ("Score", f"{score}/10"),
        ("Revisions", str(revisions)),
        ("Words", str(word_count)),
        ("Status", status),
    ])

    st.markdown("<br>", unsafe_allow_html=True)

    # Blog content
    st.markdown(f'<div class="content-box">{state.get("draft", "")}</div>', unsafe_allow_html=True)

    # Sources
    with st.expander("Sources", expanded=False):
        render_sources(state.get("sources", []))

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("Approve & Finalize", type="primary", use_container_width=True):
            graph = st.session_state.graph
            config = st.session_state.config
            for event in graph.stream(None, config=config, stream_mode="values"):
                st.session_state.current_state = event
            st.session_state.stage = "done"
            st.rerun()
    with col2:
        if st.button("Edit Manually", use_container_width=True):
            st.session_state.stage = "manual_edit"
            st.rerun()
    with col3:
        if st.button("View in LangSmith", use_container_width=True):
            st.markdown("[Open LangSmith](https://smith.langchain.com/)")

# =============================================
# STAGE: MANUAL EDIT
# =============================================
if st.session_state.stage == "manual_edit":
    state = st.session_state.current_state

    st.markdown("### Edit draft")
    st.markdown('<p class="caption-text">Make your changes below. The edited version will become the final output.</p>', unsafe_allow_html=True)

    edited_draft = st.text_area(
        "Draft content:",
        value=state.get("draft", ""),
        height=500,
        label_visibility="collapsed",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("Save & Finalize", type="primary", use_container_width=True):
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
        if st.button("Cancel", use_container_width=True):
            st.session_state.stage = "final_review"
            st.rerun()

# =============================================
# STAGE: DONE
# =============================================
if st.session_state.stage == "done":
    state = st.session_state.current_state
    final = state.get("final_output", state.get("draft", ""))

    st.balloons()

    st.markdown("### Your blog post is ready")
    st.markdown('<p class="caption-text">Copy the markdown below or download it as a file.</p>', unsafe_allow_html=True)

    st.markdown(f'<div class="content-box">{final}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Copyable markdown
    with st.expander("View raw markdown", expanded=False):
        st.code(final, language="markdown")

    # Download button
    st.download_button(
        label="Download as Markdown",
        data=final,
        file_name="blog-post.md",
        mime="text/markdown",
        use_container_width=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Start New Post", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
