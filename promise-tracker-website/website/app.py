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
    initial_sidebar_state="collapsed",
)

# -----------------------------
# File paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

PROMISES_FILE = BASE_DIR / "data" / "promises.csv"
REVIEWED_EVIDENCE_FILE = BASE_DIR / "data" / "evidence_reviewed.csv"
RAW_EVIDENCE_FILE = BASE_DIR / "data" / "evidence.csv"
SUGGESTIONS_FILE = BASE_DIR / "data" / "promise_status_suggestions.csv"
TIMELINE_FILE = BASE_DIR / "data" / "progress_timeline.csv"
PROMISE_TIMELINE_FILE = BASE_DIR / "data" / "promise_progress_timeline.csv"


def read_csv_if_exists(path):
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


# -----------------------------
# Load data
# -----------------------------
promises = pd.read_csv(PROMISES_FILE)

if REVIEWED_EVIDENCE_FILE.exists():
    EVIDENCE_FILE = REVIEWED_EVIDENCE_FILE
else:
    EVIDENCE_FILE = RAW_EVIDENCE_FILE

evidence = read_csv_if_exists(EVIDENCE_FILE)
suggestions = read_csv_if_exists(SUGGESTIONS_FILE)
timeline = read_csv_if_exists(TIMELINE_FILE)
promise_timeline = read_csv_if_exists(PROMISE_TIMELINE_FILE)

if not timeline.empty and "date" in timeline.columns:
    timeline["date"] = pd.to_datetime(timeline["date"], errors="coerce")

if not promise_timeline.empty and "date" in promise_timeline.columns:
    promise_timeline["date"] = pd.to_datetime(promise_timeline["date"], errors="coerce")


# -----------------------------
# Clean promises dataframe
# -----------------------------
if "promise_text" not in promises.columns and "simplified_promise" in promises.columns:
    promises["promise_text"] = promises["simplified_promise"]

if "promise_text" not in promises.columns:
    promises["promise_text"] = ""

if "topic" not in promises.columns:
    promises["topic"] = "Unknown topic"

if "keywords" not in promises.columns:
    promises["keywords"] = ""

if "status" not in promises.columns:
    promises["status"] = "needs review"

if "progress_score" not in promises.columns:
    promises["progress_score"] = 0

if "evidence_summary" not in promises.columns:
    promises["evidence_summary"] = "No human-reviewed evidence summary available yet."

if "parliamentary_status" not in promises.columns:
    promises["parliamentary_status"] = "N/A"

promises["promise_id"] = promises["promise_id"].astype(str)
promises["status"] = promises["status"].astype(str).str.strip().str.lower()
promises["progress_score"] = pd.to_numeric(
    promises["progress_score"],
    errors="coerce"
).fillna(0)


# -----------------------------
# Helper functions
# -----------------------------
def clean_display_value(value, fallback="Not available"):
    if pd.isna(value):
        return fallback

    text = str(value).strip()

    if text == "" or text.lower() in ["nan", "none", "null"]:
        return fallback

    return text


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


def render_badge(text, css_class):
    return f'<span class="badge {css_class}">{text}</span>'


def safe_int(value, fallback=0):
    try:
        return int(float(value))
    except Exception:
        return fallback


def get_status_emoji(status):
    return status_icon(status)


def get_topic_emoji(topic):
    topic = str(topic).lower()

    if "planning" in topic:
        return "🧭"
    if "rent" in topic:
        return "🏘️"
    if "lease" in topic:
        return "📜"
    if "mortgage" in topic or "buyer" in topic:
        return "🔑"
    if "safety" in topic or "cladding" in topic:
        return "🧯"
    if "homeless" in topic:
        return "🤝"
    if "social" in topic or "affordable" in topic:
        return "🏗️"
    if "green" in topic or "brownfield" in topic:
        return "🌿"

    return "🏠"


def get_suggestion_for_promise(pid):
    if suggestions.empty or "promise_id" not in suggestions.columns:
        return None

    result = suggestions[suggestions["promise_id"].astype(str) == str(pid)]

    if len(result) == 0:
        return None

    return result.iloc[0]


def get_evidence_for_promise(pid):
    if evidence.empty or "promise_id" not in evidence.columns:
        return pd.DataFrame()

    promise_evidence = evidence[evidence["promise_id"].astype(str) == str(pid)].copy()

    if "is_relevant" in promise_evidence.columns:
        promise_evidence = promise_evidence[
            promise_evidence["is_relevant"]
            .astype(str)
            .str.lower()
            .isin(["yes", "maybe"])
        ]

    if "normalized_url" in promise_evidence.columns:
        promise_evidence = promise_evidence.drop_duplicates(
            subset=["promise_id", "normalized_url"],
            keep="first"
        )
    elif "url" in promise_evidence.columns:
        promise_evidence = promise_evidence.drop_duplicates(
            subset=["promise_id", "url"],
            keep="first"
        )

    if "is_relevant" in promise_evidence.columns:
        relevance_order = {"yes": 0, "maybe": 1}
        promise_evidence["relevance_order"] = (
            promise_evidence["is_relevant"]
            .astype(str)
            .str.lower()
            .map(relevance_order)
            .fillna(2)
        )

        sort_cols = ["relevance_order"]

        if "source_type" in promise_evidence.columns:
            sort_cols.append("source_type")

        promise_evidence = promise_evidence.sort_values(by=sort_cols)

    return promise_evidence


def count_unique_evidence_sources(df):
    if df.empty:
        return 0

    if "global_source_key" in df.columns:
        return df["global_source_key"].dropna().nunique()

    if "normalized_url" in df.columns:
        return df["normalized_url"].dropna().nunique()

    if "url" in df.columns:
        return df["url"].dropna().nunique()

    return len(df)


# -----------------------------
# Metadata
# -----------------------------
if not evidence.empty and "collected_at" in evidence.columns:
    last_evidence_update = evidence["collected_at"].dropna().astype(str).max()
else:
    last_evidence_update = "Not available"

total_evidence_items = count_unique_evidence_sources(evidence)
total_auto_suggestions = len(suggestions)

if not suggestions.empty and "suggested_status" in suggestions.columns:
    needs_review_count = len(
        suggestions[
            suggestions["suggested_status"]
            .astype(str)
            .str.lower()
            .eq("needs review")
        ]
    )
else:
    needs_review_count = 0


# -----------------------------
# CSS
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

    .badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 850;
        margin-right: 6px;
        margin-bottom: 6px;
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

    .promise-header {
        background: linear-gradient(135deg, rgba(37,99,235,0.10), rgba(20,184,166,0.12));
        border: 1px solid rgba(147,197,253,0.9);
        border-radius: 22px;
        padding: 22px 24px;
        margin-bottom: 18px;
        box-shadow: 0 12px 30px rgba(15,23,42,0.08);
    }

    .promise-header-small {
        font-size: 14px;
        font-weight: 800;
        color: #2563eb;
        margin-bottom: 8px;
    }

    .promise-header-title {
        font-size: 25px;
        font-weight: 850;
        color: #0f172a;
        line-height: 1.35;
        margin-bottom: 14px;
    }

    div[data-testid="stExpander"] {
        background: rgba(255,255,255,0.74);
        border-radius: 18px;
        border: 1px solid rgba(226,232,240,0.90);
        margin-bottom: 12px;
        transition: all 0.20s ease-in-out;
    }

    div[data-testid="stExpander"]:hover {
        border-color: #60a5fa;
        box-shadow: 0 14px 28px rgba(15,23,42,0.10);
        transform: translateY(-2px);
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
    </style>
    """,
    unsafe_allow_html=True
)


# -----------------------------
# Hero
# -----------------------------
st.markdown(
    """
    <div class="hero">
        <div class="hero-content">
            <div class="eyebrow">🏠 DATA-DRIVEN PROMISE TRACKER</div>
            <div class="hero-title">UK Labour Housing Promise Tracker</div>
            <div class="hero-subtitle">
                An interactive semi-automatic dashboard that tracks Labour's 2024 housing promises through structured data,
                official evidence collection, automatic status suggestions, and human-reviewed interpretation.
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# -----------------------------
# Top metrics
# -----------------------------
u1, u2, u3, u4 = st.columns(4)

with u1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">🕒 Last evidence update</div>
            <div class="metric-value" style="font-size: 22px;">{last_evidence_update}</div>
            <div class="metric-note">From reviewed evidence file</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with u2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">📚 Unique evidence sources</div>
            <div class="metric-value">{total_evidence_items}</div>
            <div class="metric-note">Deduplicated where possible</div>
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
            <div class="metric-note">Supporting signal only</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with u4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">⚠️ Need review</div>
            <div class="metric-value">{needs_review_count}</div>
            <div class="metric-note">Require human checking</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.write("")


# -----------------------------
# Filters
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
    topic_options = ["All topics"] + sorted(promises["topic"].dropna().astype(str).unique().tolist())
    selected_topic = st.selectbox("Topic", topic_options)

with filter_col3:
    status_options = ["All statuses"] + sorted(promises["status"].dropna().astype(str).unique().tolist())
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
        filtered["promise_text"].astype(str).str.contains(search_text, case=False, na=False)
        | filtered["topic"].astype(str).str.contains(search_text, case=False, na=False)
        | filtered["keywords"].astype(str).str.contains(search_text, case=False, na=False)
        | filtered["promise_id"].astype(str).str.contains(search_text, case=False, na=False)
    )
    filtered = filtered[mask]

if selected_topic != "All topics":
    filtered = filtered[filtered["topic"].astype(str) == selected_topic]

if selected_status != "All statuses":
    filtered = filtered[filtered["status"].astype(str) == selected_status]


# -----------------------------
# Summary metrics
# -----------------------------
total_promises = len(filtered)
implemented_count = len(filtered[filtered["status"] == "implemented"])
not_started_count = len(filtered[filtered["status"] == "not started"])
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
            <div class="metric-label">✅ Implemented</div>
            <div class="metric-value">{implemented_count}</div>
            <div class="metric-note">Human-reviewed status</div>
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
            <div class="metric-label">📈 Average reviewed progress</div>
            <div class="metric-value">{average_progress:.1f}%</div>
            <div class="metric-note">Based on promises.csv</div>
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
        '<div class="section-subtitle">Human-reviewed promise status.</div>',
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
    st.markdown('<div class="section-title">Reviewed Progress Timeline</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Timeline scores follow the human-reviewed progress_score in promises.csv.</div>',
        unsafe_allow_html=True
    )

    if not promise_timeline.empty and "promise_id" in promise_timeline.columns:
        timeline_options = ["All promises"] + sorted(
            promise_timeline["promise_id"].dropna().astype(str).unique().tolist()
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
                        "<b>All promises average</b><br>"
                        "Stage: %{customdata[0]}<br>"
                        "Date: %{x|%Y-%m-%d}<br>"
                        "Average reviewed score: %{y:.1f}%<br>"
                        "Promises included: %{customdata[1]}"
                        "<extra></extra>"
                    )
                )
            )

            st.caption(
                "This chart shows the average reviewed assessment score. It is not a direct real-world completion percentage."
            )

        else:
            timeline_view = (
                promise_timeline[
                    promise_timeline["promise_id"].astype(str) == selected_timeline_promise
                ]
                .sort_values("stage_order")
            )

            selected_text = clean_display_value(
                timeline_view["promise_text"].iloc[0],
                "No promise text available."
            )
            selected_status = clean_display_value(
                timeline_view["current_status"].iloc[0],
                "needs review"
            )

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
                        "Reviewed assessment score: %{y:.1f}%<br><br>"
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
                title="Reviewed assessment score",
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
            st.dataframe(timeline_view, hide_index=True, width="stretch")

    else:
        st.info("No promise-level timeline file found yet. Run scripts/create_promise_timeline.py first.")

    st.markdown('</div>', unsafe_allow_html=True)


# -----------------------------
# Promise Explorer
# -----------------------------
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Promise Explorer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">Click a promise card to view its reviewed status, automatic evidence signal, and linked evidence.</div>',
    unsafe_allow_html=True
)

st.caption(
    "The reviewed status is the main project judgement. Automatic suggestions are shown only as supporting signals and still require human interpretation."
)

if len(filtered) == 0:
    st.info("No promises match your filters.")
else:
    for _, row in filtered.iterrows():
        pid = str(row["promise_id"])
        promise_text = clean_display_value(row.get("promise_text", ""), "No promise text available.")
        status = clean_display_value(row.get("status", ""), "needs review")
        topic = clean_display_value(row.get("topic", ""), "Unknown topic")
        progress_score = safe_int(row.get("progress_score", 0), 0)

        promise_evidence = get_evidence_for_promise(pid)

        if "is_relevant" in promise_evidence.columns:
            yes_count = len(
                promise_evidence[
                    promise_evidence["is_relevant"]
                    .astype(str)
                    .str.lower()
                    .eq("yes")
                ]
            )

            maybe_count = len(
                promise_evidence[
                    promise_evidence["is_relevant"]
                    .astype(str)
                    .str.lower()
                    .eq("maybe")
                ]
            )
        else:
            yes_count = 0
            maybe_count = len(promise_evidence)

        suggestion = get_suggestion_for_promise(pid)

        if suggestion is not None:
            auto_status = clean_display_value(
                suggestion.get("suggested_status", ""),
                "N/A"
            )
            auto_score = clean_display_value(
                suggestion.get("suggested_progress_score", ""),
                "N/A"
            )
            auto_count = clean_display_value(
                suggestion.get("evidence_count", ""),
                "0"
            )
            auto_summary = clean_display_value(
                suggestion.get("auto_summary", ""),
                "No automatic summary available."
            )
        else:
            auto_status = "N/A"
            auto_score = "N/A"
            auto_count = "0"
            auto_summary = "No automatic status suggestion available."

        short_promise = promise_text[:105] + ("..." if len(promise_text) > 105 else "")

        expander_title = (
            f"{get_status_emoji(status)} {pid} · {short_promise} "
            f"| {pretty_status(status)} | Evidence: {len(promise_evidence)}"
        )

        with st.expander(expander_title, expanded=False):
            st.markdown(
                f"""
                <div class="promise-header">
                    <div class="promise-header-small">
                        {get_topic_emoji(topic)} {pid} · {topic}
                    </div>
                    <div class="promise-header-title">
                        {promise_text}
                    </div>
                    <div>
                        {render_badge(get_status_emoji(status) + " Reviewed status: " + pretty_status(status), status_class(status))}
                        {render_badge("🏷️ " + topic, "topic-pill")}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            status_col, auto_col = st.columns([1.15, 1])

            with status_col:
                st.markdown("#### Human-reviewed assessment")
                st.metric("Reviewed progress score", f"{progress_score}%")
                st.progress(progress_score)

                st.write("**Human-reviewed evidence summary:**")
                st.write(
                    clean_display_value(
                        row.get("evidence_summary", ""),
                        "No human-reviewed evidence summary available yet."
                    )
                )

            with auto_col:
                st.markdown("#### Automatic evidence signal")
                st.caption(
                    "This is a system-generated signal based on collected evidence. "
                    "It is not the final project judgement."
                )

                signal_col1, signal_col2 = st.columns(2)

                with signal_col1:
                    st.metric("Suggested status", pretty_status(auto_status))

                with signal_col2:
                    st.metric("Evidence signal", f"{auto_score}%")

                st.metric("Evidence items used", auto_count)

                if pretty_status(auto_status) != pretty_status(status) and auto_status != "N/A":
                    st.warning(
                        f"The automatic signal says **{pretty_status(auto_status)}**, "
                        f"but the reviewed project status is **{pretty_status(status)}**. "
                        "This difference shows why human review is necessary."
                    )

            st.write("**Auto-generated status summary:**")
            st.info(auto_summary)

            st.markdown("#### Linked reviewed evidence")
            st.caption(
                f"Reviewed relevant: {yes_count} · Needs checking / background: {maybe_count}"
            )

            if len(promise_evidence) == 0:
                st.info("No reviewed relevant evidence has been linked to this promise yet.")
            else:
                if "source_type" in promise_evidence.columns:
                    source_options = ["All sources"] + sorted(
                        promise_evidence["source_type"]
                        .dropna()
                        .astype(str)
                        .unique()
                        .tolist()
                    )
                else:
                    source_options = ["All sources"]

                selected_source = st.selectbox(
                    "Filter evidence source",
                    source_options,
                    key=f"source_filter_inside_{pid}"
                )

                if selected_source != "All sources" and "source_type" in promise_evidence.columns:
                    display_evidence = promise_evidence[
                        promise_evidence["source_type"].astype(str) == selected_source
                    ]
                else:
                    display_evidence = promise_evidence

                for evidence_number, (_, ev) in enumerate(display_evidence.iterrows(), start=1):
                    title = clean_display_value(ev.get("title", ""), "Untitled evidence")
                    url = clean_display_value(ev.get("url", ""), "")
                    source_type = clean_display_value(ev.get("source_type", ""), "Unknown source")
                    date_published = clean_display_value(ev.get("date_published", ""), "Not available")
                    evidence_text = clean_display_value(
                        ev.get("evidence_text", ""),
                        "No short description was available. Open the official source for more details."
                    )
                    suggested_status = clean_display_value(
                        ev.get("suggested_status", ""),
                        "needs review"
                    )
                    is_relevant = clean_display_value(ev.get("is_relevant", ""), "maybe")
                    review_note = clean_display_value(
                        ev.get("review_note", ""),
                        "Needs human review."
                    )

                    relevance_label = str(is_relevant).lower().strip()

                    if relevance_label == "yes":
                        relevance_text = "✅ Reviewed relevant"
                    elif relevance_label == "maybe":
                        relevance_text = "⚠️ Needs checking / background"
                    else:
                        relevance_text = "❔ Unclear"

                    with st.container(border=True):
                        st.markdown(f"**{evidence_number}. {title}**")
                        st.caption(
                            f"Source: {source_type} · Date: {date_published} · "
                            f"{relevance_text} · Automatic assessment: {pretty_status(suggested_status)}"
                        )

                        st.write(evidence_text)

                        if review_note:
                            st.caption(f"Review note: {review_note}")

                        if isinstance(url, str) and url.startswith("http"):
                            st.markdown(f"[Open official source]({url})")

st.markdown('</div>', unsafe_allow_html=True)


# -----------------------------
# Methodology
# -----------------------------
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Methodology</div>', unsafe_allow_html=True)

st.write(
    "This tracker uses a semi-automatic method. The promise dataset is manually structured, "
    "while the evidence collection script searches official sources such as GOV.UK, UK Parliament, "
    "ONS, and Legislation.gov.uk. Collected evidence is then manually reviewed to remove irrelevant results "
    "and to mark evidence as relevant, background, or requiring further checking. The update pipeline generates "
    "automatic status suggestions based on the reviewed evidence. Final status classification should still be "
    "reviewed by humans to avoid inaccurate political judgement."
)

st.markdown('</div>', unsafe_allow_html=True)