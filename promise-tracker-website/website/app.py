from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------
# Page setting
# -----------------------------
st.set_page_config(
    page_title="UK Labour Housing Promise Tracker",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# Load data
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

PROMISES_FILE = BASE_DIR / "data" / "promises.csv"
EVIDENCE_FILE = BASE_DIR / "data" / "evidence.csv"
SUGGESTIONS_FILE = BASE_DIR / "data" / "promise_status_suggestions.csv"
TIMELINE_FILE = BASE_DIR / "data" / "progress_timeline.csv"

promises = pd.read_csv(PROMISES_FILE)

if EVIDENCE_FILE.exists():
    evidence = pd.read_csv(EVIDENCE_FILE)
else:
    evidence = pd.DataFrame()

if SUGGESTIONS_FILE.exists():
    suggestions = pd.read_csv(SUGGESTIONS_FILE)
else:
    suggestions = pd.DataFrame()

if TIMELINE_FILE.exists():
    timeline = pd.read_csv(TIMELINE_FILE)
    timeline["date"] = pd.to_datetime(timeline["date"])
else:
    timeline = pd.DataFrame()
PROMISE_TIMELINE_FILE = BASE_DIR / "data" / "promise_progress_timeline.csv"

if PROMISE_TIMELINE_FILE.exists():
    promise_timeline = pd.read_csv(PROMISE_TIMELINE_FILE)
    promise_timeline["date"] = pd.to_datetime(promise_timeline["date"])
else:
    promise_timeline = pd.DataFrame()
# Clean columns
promises["status"] = promises["status"].astype(str).str.strip().str.lower()
promises["progress_score"] = pd.to_numeric(
    promises["progress_score"],
    errors="coerce"
).fillna(0)

# -----------------------------
# Update metadata
# -----------------------------
if not evidence.empty and "collected_at" in evidence.columns:
    last_evidence_update = evidence["collected_at"].dropna().astype(str).max()
else:
    last_evidence_update = "Not available"

if not suggestions.empty and "last_auto_checked" in suggestions.columns:
    last_status_update = suggestions["last_auto_checked"].dropna().astype(str).max()
else:
    last_status_update = "Not available"

total_evidence_items = len(evidence)
total_auto_suggestions = len(suggestions)

if not suggestions.empty and "suggested_status" in suggestions.columns:
    needs_review_count = len(
        suggestions[
            suggestions["suggested_status"].astype(str).str.lower() == "needs review"
        ]
    )
else:
    needs_review_count = 0

# -----------------------------
# Custom CSS
# -----------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(59,130,246,0.13), transparent 32%),
            radial-gradient(circle at top right, rgba(20,184,166,0.13), transparent 28%),
            linear-gradient(135deg, #f8fafc 0%, #eef2ff 45%, #f8fafc 100%);
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1420px;
    }

    .hero {
        position: relative;
        overflow: hidden;
        background:
            linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #0f766e 100%);
        padding: 36px 40px;
        border-radius: 30px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 24px 60px rgba(15,23,42,0.24);
    }

    .hero:before {
        content: "";
        position: absolute;
        width: 300px;
        height: 300px;
        border-radius: 50%;
        background: rgba(255,255,255,0.10);
        right: -90px;
        top: -100px;
    }

    .hero:after {
        content: "";
        position: absolute;
        width: 170px;
        height: 170px;
        border-radius: 50%;
        background: rgba(255,255,255,0.09);
        right: 190px;
        bottom: -75px;
    }

    .hero-content {
        position: relative;
        z-index: 2;
    }

    .eyebrow {
        display: inline-block;
        background: rgba(255,255,255,0.16);
        border: 1px solid rgba(255,255,255,0.25);
        padding: 7px 13px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 800;
        letter-spacing: 0.04em;
        margin-bottom: 14px;
    }

    .hero-title {
        font-size: 44px;
        line-height: 1.05;
        font-weight: 850;
        margin-bottom: 12px;
    }

    .hero-subtitle {
        max-width: 960px;
        color: #e0f2fe;
        font-size: 17px;
        line-height: 1.65;
    }

    .top-filter-card {
        background: rgba(255,255,255,0.80);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(226,232,240,0.95);
        border-radius: 24px;
        padding: 20px 22px;
        box-shadow: 0 16px 40px rgba(15,23,42,0.08);
        margin-bottom: 22px;
    }

    .metric-card {
        background: rgba(255,255,255,0.88);
        border: 1px solid rgba(226,232,240,0.95);
        border-radius: 22px;
        padding: 22px;
        box-shadow: 0 12px 32px rgba(15,23,42,0.07);
        transition: all 0.22s ease-in-out;
        min-height: 116px;
    }

    .metric-card:hover {
        transform: translateY(-6px) scale(1.015);
        box-shadow: 0 22px 48px rgba(15,23,42,0.14);
        border-color: #93c5fd;
    }

    .metric-label {
        color: #64748b;
        font-size: 14px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .metric-value {
        color: #0f172a;
        font-size: 34px;
        font-weight: 850;
    }

    .metric-note {
        color: #64748b;
        font-size: 13px;
        margin-top: 6px;
    }

    .glass-card {
        background: rgba(255,255,255,0.84);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(226,232,240,0.96);
        border-radius: 26px;
        padding: 26px;
        box-shadow: 0 18px 45px rgba(15,23,42,0.08);
        margin-bottom: 26px;
    }

    .section-title {
        font-size: 25px;
        font-weight: 850;
        color: #0f172a;
        margin-bottom: 4px;
    }

    .section-subtitle {
        font-size: 14px;
        color: #64748b;
        margin-bottom: 18px;
    }

    .promise-card {
        position: relative;
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-radius: 22px;
        padding: 20px 22px;
        margin-bottom: 16px;
        box-shadow: 0 10px 24px rgba(15,23,42,0.06);
        transition: all 0.22s ease-in-out;
    }

    .promise-card:hover {
        transform: translateY(-5px) scale(1.01);
        box-shadow: 0 22px 42px rgba(15,23,42,0.13);
        border-color: #60a5fa;
    }

    .promise-id {
        color: #64748b;
        font-size: 13px;
        font-weight: 850;
        letter-spacing: 0.04em;
        margin-bottom: 8px;
    }

    .promise-text {
        color: #0f172a;
        font-size: 17px;
        font-weight: 760;
        line-height: 1.5;
        margin-bottom: 12px;
    }

    .status-row {
        display: flex;
        gap: 8px;
        align-items: center;
        flex-wrap: wrap;
        margin-bottom: 10px;
    }

    .badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 850;
        transition: transform 0.18s ease-in-out;
    }

    .badge:hover {
        transform: scale(1.08);
    }

    .implemented {
        background: #ccfbf1;
        color: #0f766e;
        border: 1px solid #5eead4;
    }

    .partly-implemented {
        background: #dbeafe;
        color: #1d4ed8;
        border: 1px solid #93c5fd;
    }

    .in-progress {
        background: #fef3c7;
        color: #92400e;
        border: 1px solid #fde68a;
    }

    .not-started {
        background: #e2e8f0;
        color: #475569;
        border: 1px solid #cbd5e1;
    }

    .needs-review {
        background: #ede9fe;
        color: #6d28d9;
        border: 1px solid #c4b5fd;
    }

    .unclear {
        background: #f1f5f9;
        color: #334155;
        border: 1px solid #cbd5e1;
    }

    .topic-pill {
        background: #e0f2fe;
        color: #075985;
        border: 1px solid #bae6fd;
    }

    .small-muted {
        color: #64748b;
        font-size: 13px;
    }

    .evidence-card {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        padding: 18px 20px;
        margin-bottom: 14px;
        transition: all 0.22s ease-in-out;
        box-shadow: 0 8px 20px rgba(15,23,42,0.05);
    }

    .evidence-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 18px 36px rgba(15,23,42,0.12);
        border-color: #38bdf8;
    }

    .evidence-title {
        color: #0f172a;
        font-size: 16px;
        font-weight: 850;
        margin-bottom: 6px;
    }

    div[data-testid="stTextInput"] input {
        border-radius: 14px;
        border: 1px solid #bfdbfe;
        background: white;
    }

    div[data-baseweb="select"] > div {
        border-radius: 14px;
    }

    a {
        color: #2563eb !important;
        font-weight: 750;
        text-decoration: none;
    }

    a:hover {
        text-decoration: underline;
    }

    hr {
        margin: 1.2rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Helper functions
# -----------------------------
def pretty_status(status):
    status = str(status).lower().strip()

    if status == "implemented":
        return "Implemented"
    if status == "partly implemented":
        return "Partly implemented"
    if status == "in progress":
        return "In progress"
    if status == "not started":
        return "Not started"
    if status == "needs review":
        return "Needs review"

    return status.title()


def status_class(status):
    status = str(status).lower().strip()

    if status == "implemented":
        return "implemented"
    if status == "partly implemented":
        return "partly-implemented"
    if status == "in progress":
        return "in-progress"
    if status == "not started":
        return "not-started"
    if status == "needs review":
        return "needs-review"

    return "unclear"


def status_icon(status):
    status = str(status).lower().strip()

    if status == "implemented":
        return "✅"
    if status == "partly implemented":
        return "🟦"
    if status == "in progress":
        return "🔄"
    if status == "not started":
        return "⏳"
    if status == "needs review":
        return "⚠️"

    return "❔"


def render_badge(text, css_class):
    return f'<span class="badge {css_class}">{text}</span>'


# -----------------------------
# Hero section
# -----------------------------
st.markdown(
    """
    <div class="hero">
        <div class="hero-content">
            <div class="eyebrow">🏠 DATA-DRIVEN PROMISE TRACKER</div>
            <div class="hero-title">UK Labour Housing Promise Tracker</div>
            <div class="hero-subtitle">
                Let's track how the UK Labour government is delivering on its
                housing promises. We aim to review all official announcements, 
                government data, and public evidence to show what has been delivered, what is in progress, and what has not started.
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Update status panel
# -----------------------------
u1, u2, u3, u4 = st.columns(4)

with u1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">🕒 Latest update</div>
            <div class="metric-value" style="font-size: 22px;">{last_evidence_update}</div>
            <div class="metric-note">From collected evidence file</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with u2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">📚 Sources Reviewed</div>
            <div class="metric-value">{total_evidence_items}</div>
            <div class="metric-note">Collected from multiple sources</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with u3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">🤖 Auto suggestions</div>
            <div class="metric-value">{total_auto_suggestions}</div>
            <div class="metric-note">Generated by update_status.py</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with u4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">⚠️ Needs checking!</div>
            <div class="metric-value">{needs_review_count}</div>
            <div class="metric-note">Require human checking</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.write("")

# -----------------------------
# Top filters
# -----------------------------
st.markdown('<div class="top-filter-card">', unsafe_allow_html=True)

filter_col1, filter_col2, filter_col3 = st.columns([1.4, 1, 1])

with filter_col1:
    search_text = st.text_input(
        "Search promises",
        placeholder="Search by keyword, e.g. renters, brownfield, mortgage...",
        label_visibility="visible"
    )

with filter_col2:
    topic_options = ["All topics"] + sorted(promises["topic"].dropna().unique().tolist())
    selected_topic = st.selectbox("Topic", topic_options)

with filter_col3:
    status_options = ["All statuses"] + sorted(promises["status"].dropna().unique().tolist())
    selected_status = st.selectbox(
        "Status",
        status_options,
        format_func=pretty_status
    )

st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Apply filters
# -----------------------------
filtered = promises.copy()

if search_text.strip():
    mask = (
        filtered["promise_text"].str.contains(search_text, case=False, na=False)
        | filtered["topic"].str.contains(search_text, case=False, na=False)
        | filtered["keywords"].str.contains(search_text, case=False, na=False)
    )
    filtered = filtered[mask]

if selected_topic != "All topics":
    filtered = filtered[filtered["topic"] == selected_topic]

if selected_status != "All statuses":
    filtered = filtered[filtered["status"] == selected_status]

# -----------------------------
# Summary metrics
# -----------------------------
total_promises = len(filtered)
implemented_count = len(filtered[filtered["status"] == "implemented"])
not_started_count = len(filtered[filtered["status"] == "not started"])
in_progress_count = len(filtered[filtered["status"] == "in progress"])
average_progress = filtered["progress_score"].mean() if total_promises > 0 else 0

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">📌 Total promises</div>
            <div class="metric-value">{total_promises}</div>
            <div class="metric-note">Filtered promise count</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with m2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">✅ Delivered</div>
            <div class="metric-value">{implemented_count}</div>
            <div class="metric-note">Human-reviewed classification</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with m3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">⏳ Not started</div>
            <div class="metric-value">{not_started_count}</div>
            <div class="metric-note">No confirmed implementation evidence</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with m4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">📈 Average progress</div>
            <div class="metric-value">{average_progress:.1f}%</div>
            <div class="metric-note">Based on our latest review</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.write("")

# -----------------------------
# Charts
# -----------------------------
chart_col1, chart_col2 = st.columns([0.9, 1.1])

color_map = {
    "implemented": "#0f766e",
    "partly implemented": "#14b8a6",
    "in progress": "#f59e0b",
    "not started": "#64748b",
    "needs review": "#8b5cf6",
    "unclear": "#94a3b8"
}

with chart_col1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Status Distribution</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">How the promises are currently classified.</div>',
        unsafe_allow_html=True
    )

    status_counts = filtered["status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]
    status_counts["label"] = status_counts["status"].apply(pretty_status)

    if len(status_counts) > 0:
        fig_status = px.pie(
            status_counts,
            values="count",
            names="label",
            hole=0.58,
            color="status",
            color_discrete_map=color_map
        )

        fig_status.update_traces(
            textposition="outside",
            textinfo="label+percent",
            pull=[0.04] * len(status_counts),
            marker=dict(line=dict(color="#ffffff", width=3))
        )

        fig_status.update_layout(
            height=410,
            margin=dict(t=10, b=10, l=10, r=10),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.1,
                xanchor="center",
                x=0.5
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(size=13, color="#0f172a")
        )

        fig_status.add_annotation(
            text=f"{total_promises}<br>Promises",
            x=0.5,
            y=0.5,
            font_size=22,
            showarrow=False,
            font=dict(color="#0f172a")
        )

        st.plotly_chart(fig_status, width="stretch")
    else:
        st.info("No promises match your filters.")

    st.markdown('</div>', unsafe_allow_html=True)

with chart_col2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Progress Timeline</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Select a promise to see how progress has changed over time</div>',
        unsafe_allow_html=True
    )

    if not promise_timeline.empty:
        timeline_options = ["All promises"] + sorted(
            promise_timeline["promise_id"].dropna().unique().tolist()
        )

        selected_timeline_promise = st.selectbox(
            "Timeline view",
            timeline_options,
            key="timeline_promise_selector"
        )

        if selected_timeline_promise == "All promises":
            timeline_view = (
                promise_timeline
                .groupby(["date", "stage", "stage_order"], as_index=False)
                .agg(
                    progress_score=("progress_score", "mean"),
                    promise_count=("promise_id", "nunique")
                )
                .sort_values("stage_order")
            )

            title_for_hover = "All promises average"

            fig_timeline = go.Figure()

            fig_timeline.add_trace(
                go.Scatter(
                    x=timeline_view["date"],
                    y=timeline_view["progress_score"],
                    mode="lines+markers",
                    line=dict(width=4, color="#2563eb"),
                    marker=dict(
                        size=12,
                        color="#0f766e",
                        line=dict(width=2, color="white")
                    ),
                    fill="tozeroy",
                    fillcolor="rgba(37, 99, 235, 0.12)",
                    customdata=timeline_view[["stage", "promise_count"]],
                    hovertemplate=(
                        "<b>" + title_for_hover + "</b><br>"
                        "Stage: %{customdata[0]}<br>"
                        "Date: %{x|%Y-%m-%d}<br>"
                        "Average assessment score: %{y:.1f}%<br>"
                        "Promises included: %{customdata[1]}"
                        "<extra></extra>"
                    )
                )
            )

            st.caption(
                "This chart shows an average assessment score across all promises, not a direct completion percentage."
            )

        else:
            timeline_view = (
                promise_timeline[
                    promise_timeline["promise_id"] == selected_timeline_promise
                ]
                .sort_values("stage_order")
            )

            selected_text = timeline_view["promise_text"].iloc[0]
            selected_status = timeline_view["current_status"].iloc[0]

            fig_timeline = go.Figure()

            fig_timeline.add_trace(
                go.Scatter(
                    x=timeline_view["date"],
                    y=timeline_view["progress_score"],
                    mode="lines+markers",
                    line=dict(width=4, color="#0f766e"),
                    marker=dict(
                        size=12,
                        color="#2563eb",
                        line=dict(width=2, color="white")
                    ),
                    fill="tozeroy",
                    fillcolor="rgba(15, 118, 110, 0.14)",
                    customdata=timeline_view[["stage", "note"]],
                    hovertemplate=(
                        "<b>" + selected_timeline_promise + "</b><br>"
                        "Stage: %{customdata[0]}<br>"
                        "Date: %{x|%Y-%m-%d}<br>"
                        "Assessment score: %{y:.1f}%<br><br>"
                        "%{customdata[1]}"
                        "<extra></extra>"
                    )
                )
            )

            st.caption(f"{selected_timeline_promise}: {selected_text}")
            st.caption(f"Current reviewed status: {pretty_status(selected_status)}")

        fig_timeline.update_layout(
            height=410,
            margin=dict(t=10, b=20, l=10, r=20),
            xaxis=dict(title="Tracking stage", showgrid=False),
            yaxis=dict(
                title="Evidence-based assessment score",
                range=[0, 100],
                ticksuffix="%"
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(255,255,255,0)",
            font=dict(size=13, color="#0f172a"),
            hoverlabel=dict(
                bgcolor="white",
                font_size=13,
                font_color="#0f172a"
            )
        )

        fig_timeline.update_yaxes(
            showgrid=True,
            gridcolor="rgba(148,163,184,0.24)"
        )

        st.plotly_chart(fig_timeline, width="stretch")

        with st.expander("View timeline data"):
            st.dataframe(
                timeline_view[
                    [
                        "promise_id",
                        "date",
                        "stage",
                        "progress_score",
                        "current_status",
                        "note"
                    ]
                ] if selected_timeline_promise != "All promises" else timeline_view,
                hide_index=True,
                width="stretch"
            )

    else:
        st.info("No per-promise timeline file found yet. Run scripts/create_promise_timeline.py first.")

    st.markdown('</div>', unsafe_allow_html=True)
# -----------------------------
# Promise Detail and Evidence
# -----------------------------
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Promise Details and Evidence</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">Select one promise to inspect the collected evidence and automatic status suggestion.</div>',
    unsafe_allow_html=True
)

if len(filtered) > 0:
    detail_options = filtered["promise_id"].tolist()
else:
    detail_options = promises["promise_id"].tolist()

selected_promise_id = st.radio(
    "Select promise",
    detail_options,
    horizontal=True,
    key="detail_promise_selector"
)

selected = promises[promises["promise_id"] == selected_promise_id].iloc[0]

st.markdown(f"### {selected_promise_id}: {selected['promise_text']}")

st.markdown(
    render_badge(
        f"{status_icon(selected['status'])} {pretty_status(selected['status'])}",
        status_class(selected["status"])
    )
    + " "
    + render_badge(
        f"🏷️ {selected['topic']}",
        "topic-pill"
    ),
    unsafe_allow_html=True
)

st.write("")
st.progress(int(selected["progress_score"]))

if not suggestions.empty and "promise_id" in suggestions.columns:
    selected_suggestion = suggestions[
        suggestions["promise_id"] == selected_promise_id
    ]
else:
    selected_suggestion = pd.DataFrame()

if len(selected_suggestion) > 0:
    selected_suggestion = selected_suggestion.iloc[0]
    auto_status = selected_suggestion.get("suggested_status", "N/A")
    auto_score = selected_suggestion.get("suggested_progress_score", "N/A")
    auto_evidence_count = selected_suggestion.get("evidence_count", 0)
    auto_summary = selected_suggestion.get(
        "auto_summary",
        "No automatic summary available."
    )
else:
    auto_status = "N/A"
    auto_score = "N/A"
    auto_evidence_count = 0
    auto_summary = "No automatic status suggestion has been generated yet."

d1, d2, d3, d4 = st.columns(4)

d1.metric("Current status", pretty_status(selected["status"]))
d2.metric("Current progress", f"{selected['progress_score']}%")
d3.metric("Auto-suggested status", pretty_status(auto_status))
d4.metric("Evidence count", int(auto_evidence_count))

st.write("**Human-reviewed evidence summary:**")
st.write(selected["evidence_summary"])

st.write("**Auto-generated status summary:**")
st.info(auto_summary)

st.markdown("#### Collected evidence")

if not evidence.empty and "promise_id" in evidence.columns:
    promise_evidence = evidence[evidence["promise_id"] == selected_promise_id]

    if len(promise_evidence) == 0:
        st.info("No evidence has been collected for this promise yet.")
    else:
        for _, ev in promise_evidence.iterrows():
            title = ev.get("title", "Untitled evidence")
            url = ev.get("url", "")
            source_type = ev.get("source_type", "Unknown source")
            date_published = ev.get("date_published", "")
            evidence_text = ev.get("evidence_text", "")
            suggested_status = ev.get("suggested_status", "needs review")

            st.markdown(
                f"""
                <div class="evidence-card">
                    <div class="evidence-title">📄 {title}</div>
                    <div class="small-muted">
                        Source: <b>{source_type}</b> ·
                        Date: <b>{date_published}</b> ·
                        Suggested status: <b>{suggested_status}</b>
                    </div>
                    <br>
                    <div>{evidence_text}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if isinstance(url, str) and url.startswith("http"):
                st.markdown(f"[Open official source]({url})")
else:
    st.info("No evidence file found yet.")

st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Methodology
# -----------------------------
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Methodology</div>', unsafe_allow_html=True)

st.write(
    "This tracker uses a semi-automatic method. The promise dataset is manually structured, "
    "while the evidence collection script searches official sources such as GOV.UK, "
    "UK Parliament, ONS, and Legislation.gov.uk. Collected evidence is stored in a CSV file "
    "and displayed on this dashboard. The update pipeline then generates automatic status "
    "suggestions based on the collected evidence. Final status classification should still "
    "be reviewed by humans to avoid inaccurate political judgement."
)

st.markdown('</div>', unsafe_allow_html=True)