import time
import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="AI DevOps Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }
.main { background: #0a0e1a; }
.block-container { padding: 1.5rem 2rem; }
.hero-banner {
    background: linear-gradient(135deg, #1a1f3a 0%, #0d1117 50%, #1a2744 100%);
    border: 1px solid #2a3a5c;
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
}
.hero-title { font-size: 2rem; font-weight: 700; color: #ffffff; margin: 0; letter-spacing: -0.5px; }
.hero-subtitle { font-size: 0.95rem; color: #6b7db3; margin: 0.3rem 0 0 0; }
.hero-badge {
    display: inline-block; background: #1e3a5f; color: #60a5fa;
    font-size: 0.75rem; font-weight: 600; padding: 0.25rem 0.75rem;
    border-radius: 20px; border: 1px solid #2563eb44; margin-bottom: 0.75rem;
}
.glow-line {
    height: 2px;
    background: linear-gradient(90deg, #2563eb, #7c3aed, #2563eb);
    border-radius: 2px; margin: 1rem 0 0 0;
}
.metric-card {
    background: #111827; border: 1px solid #1f2937;
    border-radius: 12px; padding: 1.2rem 1.4rem; text-align: center;
}
.metric-card:hover { border-color: #2563eb; }
.metric-value { font-size: 2rem; font-weight: 700; color: #ffffff; line-height: 1; margin: 0.3rem 0; }
.metric-label { font-size: 0.75rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 500; }
.metric-delta-good { font-size: 0.8rem; color: #10b981; font-weight: 600; margin-top: 0.2rem; }
.metric-delta-info { font-size: 0.8rem; color: #60a5fa; font-weight: 600; margin-top: 0.2rem; }
.section-title {
    font-size: 1.1rem; font-weight: 600; color: #e5e7eb;
    margin: 0 0 1rem 0; display: flex; align-items: center; gap: 0.5rem;
}
.pipeline-card {
    background: #111827; border: 1px solid #1f2937;
    border-radius: 12px; padding: 1rem 1.2rem; text-align: center;
}
.pipeline-name { font-size: 0.7rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.4rem; }
.pipeline-status { font-size: 1.1rem; font-weight: 700; margin: 0.3rem 0; }
.pipeline-type { font-size: 0.8rem; color: #60a5fa; margin-top: 0.2rem; }
.pipeline-meta { font-size: 0.72rem; color: #4b5563; margin-top: 0.3rem; }
.status-bar {
    background: #111827; border: 1px solid #1f2937;
    border-radius: 10px; padding: 0.8rem 1.2rem;
    display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;
}
.status-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: #10b981; box-shadow: 0 0 6px #10b981;
    display: inline-block; margin-right: 6px;
}
.footer {
    text-align: center; color: #374151; font-size: 0.75rem;
    padding: 1.5rem 0 0.5rem; border-top: 1px solid #1f2937; margin-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
BASE          = os.path.dirname(__file__)
CSV           = os.path.join(BASE, "..", "backend", "analysis_log.csv")
JSON          = os.path.join(BASE, "..", "backend", "summary_report.json")
PIPELINE_JSON = os.path.join(BASE, "..", "backend", "pipeline_report.json")

@st.cache_data(ttl=5)
def load_csv():
    if os.path.exists(CSV):
        try:
            return pd.read_csv(CSV, encoding="utf-8")
        except Exception:
            return pd.read_csv(CSV, encoding="latin-1")
    return pd.DataFrame()

@st.cache_data(ttl=5)
def load_summary():
    if os.path.exists(JSON):
        with open(JSON, encoding="utf-8") as f:
            return json.load(f)
    return {}

@st.cache_data(ttl=5)
def load_pipeline():
    if os.path.exists(PIPELINE_JSON):
        with open(PIPELINE_JSON, encoding="utf-8") as f:
            return json.load(f)
    return {}

df            = load_csv()
summary       = load_summary()
pipeline_data = load_pipeline()

# ── Hero Banner ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <div class="hero-badge">🏆 Hack2Hire 1.0 — Problem 08</div>
    <h1 class="hero-title">🤖 AI-Powered Jenkins Pipeline Analyzer</h1>
    <p class="hero-subtitle">
        Self-Healing DevOps Agent &nbsp;•&nbsp;
        Gemini LLM + Regex Classifier &nbsp;•&nbsp;
        Real-time Anomaly Detection
    </p>
    <div class="glow-line"></div>
</div>
""", unsafe_allow_html=True)

# ── Status Bar ────────────────────────────────────────────────────────────────
now = datetime.now().strftime("%d %b %Y • %H:%M:%S")
total_pipelines = len(pipeline_data.get("pipelines", []))
failed_pipelines = pipeline_data.get("failed_pipelines", 0)

st.markdown(f"""
<div class="status-bar">
    <span>
        <span class="status-dot"></span>
        <span style="color:#10b981;font-size:0.8rem;font-weight:600;">Agent Active</span>
    </span>
    <span style="color:#6b7280;font-size:0.8rem;">Last scan: {now}</span>
    <span style="color:#6b7280;font-size:0.8rem;">•</span>
    <span style="color:#6b7280;font-size:0.8rem;">
        Pipelines: {total_pipelines} monitored • {failed_pipelines} failing
    </span>
    <span style="color:#6b7280;font-size:0.8rem;">•</span>
    <span style="color:#6b7280;font-size:0.8rem;">T John Institute of Technology | CSE Dept</span>
</div>
""", unsafe_allow_html=True)

# ── Metric Cards ──────────────────────────────────────────────────────────────
if summary:
    mttr  = summary.get("mttr", {})
    src   = summary.get("source_counts", {})
    total = summary.get("total_logs", 0)
    imp   = mttr.get("improvement", 0)
    saved = round(mttr.get("without_ai", 0) - mttr.get("with_ai", 0), 1)

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Total Logs</div>
            <div class="metric-value">{total}</div>
            <div class="metric-delta-info">Analyzed</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Regex Classified</div>
            <div class="metric-value">{src.get('regex',0)}</div>
            <div class="metric-delta-info">Layer 1</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">LLM Classified</div>
            <div class="metric-value">{src.get('llm',0)}</div>
            <div class="metric-delta-info">Gemini AI</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">MTTR Without AI</div>
            <div class="metric-value">{mttr.get('without_ai',0)}</div>
            <div class="metric-label">minutes</div>
        </div>""", unsafe_allow_html=True)
    with c5:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">MTTR With AI</div>
            <div class="metric-value" style="color:#10b981;">{mttr.get('with_ai',0)}</div>
            <div class="metric-delta-good">↓ {imp:.1f}% faster</div>
        </div>""", unsafe_allow_html=True)
    with c6:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Time Saved</div>
            <div class="metric-value" style="color:#fbbf24;">{saved}</div>
            <div class="metric-delta-good">min per issue</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Jenkins Pipeline Health ───────────────────────────────────────────────────
pipelines = pipeline_data.get("pipelines", [])
if pipelines:
    st.markdown('<p class="section-title">📡 Jenkins Pipeline Health</p>',
                unsafe_allow_html=True)
    cols = st.columns(len(pipelines))
    for i, p in enumerate(pipelines):
        result     = p.get("result", "N/A")
        issue_type = p.get("type", "Unknown")
        color      = "#ef4444" if result == "FAILURE" else "#10b981" if result == "SUCCESS" else "#f59e0b"
        icon       = "🔴" if result == "FAILURE" else "🟢" if result == "SUCCESS" else "🟡"
        name       = p.get("pipeline", "").replace("-", " ").upper()
        with cols[i]:
            st.markdown(f"""
            <div class="pipeline-card">
                <div class="pipeline-name">{name}</div>
                <div class="pipeline-status" style="color:{color};">{icon} {result}</div>
                <div class="pipeline-type">{issue_type}</div>
                <div class="pipeline-meta">
                    Build #{p.get('build','N/A')} •
                    {p.get('duration_sec',0)}s •
                    ✅{p.get('tests_pass',0)} ❌{p.get('tests_fail',0)}
                </div>
                <div class="pipeline-meta" style="color:#6b7280;margin-top:4px;">
                    {p.get('action','No action')}
                </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

# ── Charts Row ────────────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<p class="section-title">📊 Failure Distribution</p>',
                unsafe_allow_html=True)
    if summary and "failure_distribution" in summary:
        fd     = summary["failure_distribution"]
        COLORS = ["#3b82f6","#ef4444","#10b981","#f59e0b","#8b5cf6","#06b6d4","#f97316"]
        fig = px.pie(
            values=list(fd.values()),
            names=list(fd.keys()),
            color_discrete_sequence=COLORS,
            hole=0.55
        )
        fig.update_traces(
            textposition="outside",
            textinfo="percent+label",
            textfont=dict(size=11, color="#e5e7eb"),
            marker=dict(line=dict(color="#0a0e1a", width=2))
        )
        fig.update_layout(
            showlegend=False,
            margin=dict(t=10, b=10, l=10, r=10),
            height=300,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown('<p class="section-title">⏱️ MTTR: AI vs Manual Resolution</p>',
                unsafe_allow_html=True)
    if summary and "mttr" in summary:
        mttr = summary["mttr"]
        fig2 = go.Figure()
        fig2.add_bar(
            name="Without AI",
            x=["Resolution Time"],
            y=[mttr["without_ai"]],
            marker_color="#ef4444",
            marker_line_color="#991b1b",
            marker_line_width=1.5,
            text=[f"{mttr['without_ai']} min"],
            textposition="outside",
            textfont=dict(color="#e5e7eb", size=12),
            width=0.25
        )
        fig2.add_bar(
            name="With AI Agent",
            x=["Resolution Time"],
            y=[mttr["with_ai"]],
            marker_color="#10b981",
            marker_line_color="#065f46",
            marker_line_width=1.5,
            text=[f"{mttr['with_ai']} min"],
            textposition="outside",
            textfont=dict(color="#e5e7eb", size=12),
            width=0.25
        )
        fig2.update_layout(
            barmode="group",
            height=300,
            margin=dict(t=20, b=0, l=0, r=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(
                gridcolor="#1f2937",
                color="#6b7280",
                title=dict(text="Minutes", font=dict(color="#6b7280"))
            ),
            xaxis=dict(color="#6b7280"),
            legend=dict(
                orientation="h", y=1.15,
                font=dict(color="#9ca3af"),
                bgcolor="rgba(0,0,0,0)"
            ),
            font=dict(color="#9ca3af")
        )
        st.plotly_chart(fig2, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Confidence + Source breakdown ─────────────────────────────────────────────
if summary:
    col3, col4 = st.columns(2)
    conf = summary.get("confidence_breakdown", {})
    src  = summary.get("source_counts", {})

    with col3:
        st.markdown('<p class="section-title">🎯 Confidence Breakdown</p>',
                    unsafe_allow_html=True)
        fig3 = go.Figure(go.Bar(
            x=["High", "Medium", "Low"],
            y=[conf.get("High",0), conf.get("Medium",0), conf.get("Low",0)],
            marker_color=["#10b981", "#f59e0b", "#ef4444"],
            text=[conf.get("High",0), conf.get("Medium",0), conf.get("Low",0)],
            textposition="outside",
            textfont=dict(color="#e5e7eb")
        ))
        fig3.update_layout(
            height=220, margin=dict(t=20,b=0,l=0,r=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(gridcolor="#1f2937", color="#6b7280"),
            xaxis=dict(color="#9ca3af"),
            showlegend=False
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown('<p class="section-title">🧠 Classification Source</p>',
                    unsafe_allow_html=True)
        fig4 = go.Figure(go.Bar(
            x=["Regex (Layer 1)", "Gemini LLM (Layer 2)"],
            y=[src.get("regex",0), src.get("llm",0)],
            marker_color=["#3b82f6", "#8b5cf6"],
            text=[src.get("regex",0), src.get("llm",0)],
            textposition="outside",
            textfont=dict(color="#e5e7eb")
        ))
        fig4.update_layout(
            height=220, margin=dict(t=20,b=0,l=0,r=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(gridcolor="#1f2937", color="#6b7280"),
            xaxis=dict(color="#9ca3af"),
            showlegend=False
        )
        st.plotly_chart(fig4, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Full Analysis Log ─────────────────────────────────────────────────────────
st.markdown('<p class="section-title">📋 Full Analysis Log</p>',
            unsafe_allow_html=True)

if not df.empty:
    def color_confidence(val):
        if val == "High":   return "background-color:#052e16;color:#34d399;font-weight:600;"
        if val == "Medium": return "background-color:#431407;color:#fb923c;font-weight:600;"
        return "background-color:#3b0764;color:#e879f9;font-weight:600;"

    def color_source(val):
        if val == "llm": return "background-color:#1e1b4b;color:#a78bfa;font-weight:600;"
        return "background-color:#0c1a2e;color:#60a5fa;font-weight:600;"

    # Show pipeline column if present
    display_cols = ["timestamp","filename","type","category",
                    "reason","fix","confidence","source","action_taken"]
    if "pipeline" in df.columns:
        display_cols = ["timestamp","filename","pipeline","type","category",
                        "reason","fix","confidence","source","action_taken"]

    styled = (
        df[display_cols].style
        .applymap(color_confidence, subset=["confidence"])
        .applymap(color_source,     subset=["source"])
        .set_properties(**{
            "background-color": "#111827",
            "color": "#d1d5db",
            "border-color": "#1f2937"
        })
    )
    st.dataframe(styled, use_container_width=True, height=320)

    col_dl, col_empty = st.columns([1, 4])
    with col_dl:
        st.download_button(
            label="⬇️ Download CSV",
            data=df.to_csv(index=False),
            file_name="analysis_log.csv",
            mime="text/csv",
            use_container_width=True
        )

st.markdown("<br>", unsafe_allow_html=True)

# ── Self-Healing Actions ──────────────────────────────────────────────────────
st.markdown('<p class="section-title">⚡ Self-Healing Actions Taken</p>',
            unsafe_allow_html=True)

if not df.empty and "action_taken" in df.columns:
    action_cols = ["timestamp", "filename", "type", "action_taken"]
    if "pipeline" in df.columns:
        action_cols = ["timestamp", "filename", "pipeline", "type", "action_taken"]

    action_df = df[action_cols].copy()
    action_df.columns = [c.replace("_", " ").title() for c in action_cols]

    st.dataframe(
        action_df.style.set_properties(**{
            "background-color": "#111827",
            "color": "#d1d5db",
            "border-color": "#1f2937"
        }),
        use_container_width=True,
        height=280
    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="footer">
    🤖 AI-Powered Jenkins Pipeline Analyzer &nbsp;•&nbsp;
    Hack2Hire 1.0 — Problem 08 &nbsp;•&nbsp;
    T John Institute of Technology &nbsp;•&nbsp;
    Built by Vinay Babannavar &amp; Preetam Anil Kage &nbsp;•&nbsp;
    {datetime.now().strftime("%d %b %Y")}
</div>
""", unsafe_allow_html=True)

col_r, _ = st.columns([1, 5])
with col_r:
    if st.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Auto refresh every 10 seconds
time.sleep(10)
st.rerun()