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

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Sora:wght@300;400;600;700&display=swap');
* { font-family: 'Sora', sans-serif; }
.main { background: #050810; }
.block-container { padding: 1.2rem 2.5rem 2rem; }
.hero {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 40%, #0f172a 100%);
    border: 1px solid #312e81;
    border-radius: 20px;
    padding: 2.5rem 3rem;
    margin-bottom: 1.2rem;
    position: relative;
    overflow: hidden;
}
.hero-eyebrow {
    display: inline-flex; align-items: center; gap: 6px;
    background: #1e1b4b; color: #a5b4fc;
    font-size: 0.72rem; font-weight: 600;
    padding: 0.3rem 0.9rem; border-radius: 20px;
    border: 1px solid #4338ca55; margin-bottom: 1rem;
    letter-spacing: 0.06em; text-transform: uppercase;
}
.hero-title {
    font-size: 2.4rem; font-weight: 700; color: #f1f5f9;
    margin: 0 0 0.4rem; line-height: 1.15; letter-spacing: -0.8px;
}
.hero-title span { color: #818cf8; }
.hero-sub { font-size: 0.95rem; color: #64748b; margin: 0; line-height: 1.6; }
.hero-divider {
    height: 1px; margin-top: 1.5rem;
    background: linear-gradient(90deg, transparent, #4338ca, #7c3aed, #4338ca, transparent);
}
.statusbar {
    background: #0f172a; border: 1px solid #1e293b;
    border-radius: 12px; padding: 0.7rem 1.4rem;
    display: flex; align-items: center; gap: 1.2rem;
    margin-bottom: 1.4rem; flex-wrap: wrap;
}
.pulse {
    width: 8px; height: 8px; border-radius: 50%;
    background: #22c55e; box-shadow: 0 0 0 3px #22c55e33;
    display: inline-block; margin-right: 5px;
}
.status-text { color: #22c55e; font-size: 0.8rem; font-weight: 600; }
.status-sep { color: #1e293b; font-size: 1rem; }
.status-info { color: #475569; font-size: 0.78rem; }
.kpi-grid {
    display: grid; grid-template-columns: repeat(6, 1fr);
    gap: 10px; margin-bottom: 1.2rem;
}
.kpi {
    background: #0f172a; border: 1px solid #1e293b;
    border-radius: 14px; padding: 1.1rem 1rem; text-align: center;
    cursor: default;
}
.kpi-label {
    font-size: 0.65rem; color: #475569; text-transform: uppercase;
    letter-spacing: 0.1em; font-weight: 600; margin-bottom: 0.5rem;
}
.kpi-val {
    font-size: 2rem; font-weight: 700; line-height: 1;
    font-family: 'JetBrains Mono', monospace;
}
.kpi-sub { font-size: 0.72rem; margin-top: 0.3rem; font-weight: 500; }
.kpi-blue .kpi-val { color: #60a5fa; } .kpi-blue .kpi-sub { color: #3b82f6; }
.kpi-purple .kpi-val { color: #a78bfa; } .kpi-purple .kpi-sub { color: #7c3aed; }
.kpi-cyan .kpi-val { color: #22d3ee; } .kpi-cyan .kpi-sub { color: #06b6d4; }
.kpi-slate .kpi-val { color: #94a3b8; } .kpi-slate .kpi-sub { color: #64748b; }
.kpi-green .kpi-val { color: #4ade80; } .kpi-green .kpi-sub { color: #22c55e; }
.kpi-amber .kpi-val { color: #fbbf24; } .kpi-amber .kpi-sub { color: #f59e0b; }
.pipe-grid {
    display: grid; grid-template-columns: repeat(3, 1fr);
    gap: 12px; margin-bottom: 1.4rem;
}
.pipe-card {
    background: #0f172a; border: 1px solid #1e293b;
    border-radius: 16px; padding: 1.2rem 1.4rem;
}
.pipe-card.fail { border-left: 3px solid #ef4444; }
.pipe-card.pass { border-left: 3px solid #22c55e; }
.pipe-card.warn { border-left: 3px solid #f59e0b; }
.pipe-top {
    display: flex; justify-content: space-between;
    align-items: flex-start; margin-bottom: 0.6rem;
}
.pipe-name {
    font-size: 0.7rem; color: #64748b;
    text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600;
}
.pipe-badge {
    font-size: 0.65rem; font-weight: 700; padding: 0.15rem 0.6rem;
    border-radius: 6px; letter-spacing: 0.05em;
}
.badge-fail { background: #450a0a; color: #fca5a5; border: 1px solid #ef444433; }
.badge-pass { background: #052e16; color: #86efac; border: 1px solid #22c55e33; }
.pipe-issue { font-size: 1rem; font-weight: 700; color: #e2e8f0; margin: 0.3rem 0; }
.pipe-meta { font-size: 0.72rem; color: #475569; margin-top: 0.3rem; line-height: 1.5; }
.pipe-action { font-size: 0.7rem; color: #818cf8; margin-top: 0.5rem; font-style: italic; }
.sec-head {
    font-size: 0.75rem; font-weight: 700; color: #475569;
    text-transform: uppercase; letter-spacing: 0.12em;
    margin: 0 0 0.8rem; display: flex; align-items: center; gap: 8px;
}
.sec-head::after { content: ''; flex: 1; height: 1px; background: #1e293b; }
.footer-bar {
    text-align: center; color: #334155; font-size: 0.72rem;
    padding: 1.5rem 0 0.5rem; border-top: 1px solid #1e293b; margin-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE   = os.path.dirname(__file__)
CSV    = os.path.join(BASE, "..", "backend", "analysis_log.csv")
JSON_S = os.path.join(BASE, "..", "backend", "summary_report.json")
JSON_P = os.path.join(BASE, "..", "backend", "pipeline_report.json")

@st.cache_data(ttl=5)
def load_csv():
    if os.path.exists(CSV):
        try:    return pd.read_csv(CSV, encoding="utf-8")
        except: return pd.read_csv(CSV, encoding="latin-1")
    return pd.DataFrame(columns=[
        "timestamp", "filename", "pipeline", "type", "category",
        "reason", "fix", "confidence", "source", "action_taken"
    ])

@st.cache_data(ttl=5)
def load_summary():
    if os.path.exists(JSON_S):
        with open(JSON_S, encoding="utf-8") as f: return json.load(f)
    return {}

@st.cache_data(ttl=5)
def load_pipeline():
    if os.path.exists(JSON_P):
        with open(JSON_P, encoding="utf-8") as f: return json.load(f)
    return {}

df      = load_csv()
summary = load_summary()
pdata   = load_pipeline()

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-eyebrow">⚡ Hack2Hire 1.0 — Problem 08 — T John Institute of Technology</div>
  <h1 class="hero-title">AI-Powered <span>Jenkins</span> Pipeline Analyzer</h1>
  <p class="hero-sub">
    Self-Healing DevOps Agent &nbsp;·&nbsp; Gemini 1.5 Flash LLM &nbsp;·&nbsp;
    Regex Classifier &nbsp;·&nbsp; Real-time Anomaly Detection
  </p>
  <div class="hero-divider"></div>
</div>
""", unsafe_allow_html=True)

# ── Status Bar ────────────────────────────────────────────────────────────────
now      = datetime.now().strftime("%d %b %Y · %H:%M:%S")
n_pipes  = len(pdata.get("pipelines", []))
n_failed = pdata.get("failed_pipelines", 0)

st.markdown(f"""
<div class="statusbar">
  <span><span class="pulse"></span><span class="status-text">Agent Active</span></span>
  <span class="status-sep">|</span>
  <span class="status-info">Last scan: {now}</span>
  <span class="status-sep">|</span>
  <span class="status-info">
    {n_pipes} pipelines monitored &nbsp;·&nbsp;
    <span style="color:#ef4444;font-weight:600;">{n_failed} failing</span>
  </span>
  <span class="status-sep">|</span>
  <span class="status-info">T John Institute of Technology · CSE Dept</span>
</div>
""", unsafe_allow_html=True)

# ── KPI Cards ─────────────────────────────────────────────────────────────────
if summary:
    mttr  = summary.get("mttr", {})
    src   = summary.get("source_counts", {})
    total = summary.get("total_logs", 0)
    imp   = mttr.get("improvement", 0)
    saved = round(mttr.get("without_ai", 0) - mttr.get("with_ai", 0), 1)

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi kpi-blue">
        <div class="kpi-label">Total Logs</div>
        <div class="kpi-val">{total}</div>
        <div class="kpi-sub">Analyzed</div>
      </div>
      <div class="kpi kpi-purple">
        <div class="kpi-label">Regex</div>
        <div class="kpi-val">{src.get('regex',0)}</div>
        <div class="kpi-sub">Layer 1</div>
      </div>
      <div class="kpi kpi-cyan">
        <div class="kpi-label">LLM</div>
        <div class="kpi-val">{src.get('llm',0)}</div>
        <div class="kpi-sub">Gemini AI</div>
      </div>
      <div class="kpi kpi-slate">
        <div class="kpi-label">MTTR Before</div>
        <div class="kpi-val">{mttr.get('without_ai',0)}</div>
        <div class="kpi-sub">minutes</div>
      </div>
      <div class="kpi kpi-green">
        <div class="kpi-label">MTTR After</div>
        <div class="kpi-val">{mttr.get('with_ai',0)}</div>
        <div class="kpi-sub">↓ {imp:.1f}% faster</div>
      </div>
      <div class="kpi kpi-amber">
        <div class="kpi-label">Time Saved</div>
        <div class="kpi-val">{saved}</div>
        <div class="kpi-sub">min / issue</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── Pipeline Health ───────────────────────────────────────────────────────────
pipelines = pdata.get("pipelines", [])
if pipelines:
    st.markdown('<p class="sec-head">📡 Jenkins Pipeline Health</p>',
                unsafe_allow_html=True)
    cards_html = '<div class="pipe-grid">'
    for p in pipelines:
        result = p.get("result", "N/A")
        cls    = "fail" if result == "FAILURE" else "pass" if result == "SUCCESS" else "warn"
        badge  = "badge-fail" if result == "FAILURE" else "badge-pass"
        icon   = "🔴" if result == "FAILURE" else "🟢"
        name   = p.get("pipeline", "").replace("-", " ").title()
        cards_html += f"""
        <div class="pipe-card {cls}">
          <div class="pipe-top">
            <div class="pipe-name">{name}</div>
            <span class="pipe-badge {badge}">{icon} {result}</span>
          </div>
          <div class="pipe-issue">{p.get('type','Unknown')}</div>
          <div class="pipe-meta">
            Build #{p.get('build','N/A')} &nbsp;·&nbsp;
            {p.get('duration_sec',0)}s &nbsp;·&nbsp;
            ✅ {p.get('tests_pass',0)} &nbsp; ❌ {p.get('tests_fail',0)}
          </div>
          <div class="pipe-action">⚡ {p.get('action','No action')}</div>
        </div>"""
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)

# ── Chart layout shared ───────────────────────────────────────────────────────
CL = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=10, b=10, l=10, r=10),
    height=280,
    font=dict(color="#64748b", size=11),
)

# ── Charts Row 1 ──────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown('<p class="sec-head">📊 Failure Distribution</p>',
                unsafe_allow_html=True)
    if summary and "failure_distribution" in summary:
        fd     = summary["failure_distribution"]
        COLORS = ["#6366f1","#ef4444","#22c55e","#f59e0b","#8b5cf6","#06b6d4","#f97316"]
        fig1   = px.pie(values=list(fd.values()), names=list(fd.keys()),
                        color_discrete_sequence=COLORS, hole=0.6)
        fig1.update_traces(
            textposition="outside", textinfo="percent+label",
            textfont=dict(size=10.5, color="#94a3b8"),
            marker=dict(line=dict(color="#050810", width=2))
        )
        fig1.update_layout(showlegend=False, **CL)
        st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown('<p class="sec-head">⏱ MTTR — AI vs Manual</p>',
                unsafe_allow_html=True)
    if summary and "mttr" in summary:
        mttr_d = summary["mttr"]
        fig2   = go.Figure()
        fig2.add_bar(
            name="Manual",
            x=["MTTR"], y=[mttr_d["without_ai"]],
            marker=dict(color="rgba(239,68,68,0.5)",
                        line=dict(color="#ef4444", width=1)),
            text=[f"{mttr_d['without_ai']} min"],
            textposition="outside",
            textfont=dict(color="#fca5a5"),
            width=0.3
        )
        fig2.add_bar(
            name="AI Agent",
            x=["MTTR"], y=[mttr_d["with_ai"]],
            marker=dict(color="rgba(34,197,94,0.5)",
                        line=dict(color="#22c55e", width=1)),
            text=[f"{mttr_d['with_ai']} min"],
            textposition="outside",
            textfont=dict(color="#86efac"),
            width=0.3
        )
        fig2.update_layout(
            barmode="group",
            yaxis=dict(gridcolor="#1e293b", color="#475569",
                       title=dict(text="minutes")),
            xaxis=dict(color="#475569"),
            legend=dict(orientation="h", y=1.12,
                        font=dict(color="#64748b"),
                        bgcolor="rgba(0,0,0,0)"),
            **CL
        )
        st.plotly_chart(fig2, use_container_width=True)

# ── Charts Row 2 ──────────────────────────────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.markdown('<p class="sec-head">🎯 Confidence Breakdown</p>',
                unsafe_allow_html=True)
    if summary:
        conf = summary.get("confidence_breakdown", {})
        fig3 = go.Figure(go.Bar(
            x=["High", "Medium", "Low"],
            y=[conf.get("High",0), conf.get("Medium",0), conf.get("Low",0)],
            marker=dict(
                color=["rgba(34,197,94,0.5)",
                       "rgba(245,158,11,0.5)",
                       "rgba(239,68,68,0.5)"],
                line=dict(color=["#22c55e","#f59e0b","#ef4444"], width=1)
            ),
            text=[conf.get("High",0), conf.get("Medium",0), conf.get("Low",0)],
            textposition="outside",
            textfont=dict(color="#94a3b8")
        ))
        fig3.update_layout(
            yaxis=dict(gridcolor="#1e293b", color="#475569"),
            xaxis=dict(color="#94a3b8"),
            showlegend=False, **CL
        )
        st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.markdown('<p class="sec-head">🧠 Classification Source</p>',
                unsafe_allow_html=True)
    if summary:
        src2 = summary.get("source_counts", {})
        fig4 = go.Figure(go.Bar(
            x=["Regex (Layer 1)", "Gemini LLM (Layer 2)"],
            y=[src2.get("regex",0), src2.get("llm",0)],
            marker=dict(
                color=["rgba(99,102,241,0.5)",
                       "rgba(167,139,250,0.5)"],
                line=dict(color=["#6366f1","#a78bfa"], width=1)
            ),
            text=[src2.get("regex",0), src2.get("llm",0)],
            textposition="outside",
            textfont=dict(color="#94a3b8")
        ))
        fig4.update_layout(
            yaxis=dict(gridcolor="#1e293b", color="#475569"),
            xaxis=dict(color="#94a3b8"),
            showlegend=False, **CL
        )
        st.plotly_chart(fig4, use_container_width=True)

# ── Full Analysis Log ─────────────────────────────────────────────────────────
st.markdown('<p class="sec-head">📋 Full Analysis Log</p>',
            unsafe_allow_html=True)

if not df.empty:
    def style_conf(val):
        m = {
            "High":   "background:#052e16;color:#4ade80;",
            "Medium": "background:#431407;color:#fbbf24;",
            "Low":    "background:#2d1657;color:#c084fc;"
        }
        return m.get(val, "")

    def style_src(val):
        if val == "llm":
            return "background:#1e1b4b;color:#a78bfa;font-weight:600;"
        return "background:#0c1a2e;color:#60a5fa;"

    dcols = ["timestamp","filename","type","category",
             "reason","fix","confidence","source","action_taken"]
    if "pipeline" in df.columns:
        dcols = ["timestamp","filename","pipeline","type","category",
                 "reason","fix","confidence","source","action_taken"]

    styled = (
        df[dcols].style
        .applymap(style_conf, subset=["confidence"])
        .applymap(style_src,  subset=["source"])
        .set_properties(**{
            "background-color": "#0f172a",
            "color":            "#cbd5e1",
            "border-color":     "#1e293b"
        })
        .set_table_styles([{
            "selector": "th",
            "props": [
                ("background",      "#1e293b"),
                ("color",           "#64748b"),
                ("font-size",       "0.72rem"),
                ("text-transform",  "uppercase"),
                ("letter-spacing",  "0.08em")
            ]
        }])
    )
    st.dataframe(styled, use_container_width=True, height=300)

    c_dl, _ = st.columns([1, 5])
    with c_dl:
        st.download_button(
            "⬇️ Download CSV",
            df.to_csv(index=False),
            "analysis_log.csv",
            "text/csv",
            use_container_width=True
        )
else:
    st.info("📋 No analysis logs found. Run `py backend/cli.py` or `py backend/jenkins_agent.py` to populate this table.")

# ── Self-Healing Actions ──────────────────────────────────────────────────────
st.markdown('<p class="sec-head">⚡ Self-Healing Actions</p>',
            unsafe_allow_html=True)

if not df.empty and "action_taken" in df.columns:
    acols = ["timestamp","filename","type","action_taken"]
    if "pipeline" in df.columns:
        acols = ["timestamp","filename","pipeline","type","action_taken"]

    adf = df[acols].copy()
    adf.columns = [c.replace("_"," ").title() for c in acols]

    st.dataframe(
        adf.style.set_properties(**{
            "background-color": "#0f172a",
            "color":            "#cbd5e1",
            "border-color":     "#1e293b"
        }),
        use_container_width=True,
        height=260
    )
elif df.empty:
    st.info("⚡ No self-healing actions recorded yet.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="footer-bar">
    Built by <strong style="color:#475569;">
    Vinay Babannavar &amp; Preetam Anil Kage</strong>
    &nbsp;·&nbsp; Hack2Hire 1.0 Problem 08
    &nbsp;·&nbsp; T John Institute of Technology
    &nbsp;·&nbsp; {datetime.now().strftime("%d %b %Y")}
</div>
""", unsafe_allow_html=True)

c_ref, _ = st.columns([1, 6])
with c_ref:
    if st.button("🔄 Refresh Now", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Auto refresh every 10 seconds
time.sleep(10)
st.rerun()