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
    layout="wide"
)

st.title("🤖 AI-Powered Jenkins Pipeline Analyzer")
st.caption("Self-Healing DevOps Agent — Hack2Hire 1.0")

# ── Load data ────────────────────────────────────────────────────────────────
BASE  = os.path.dirname(__file__)
CSV   = os.path.join(BASE, "..", "backend", "analysis_log.csv")
JSON  = os.path.join(BASE, "..", "backend", "summary_report.json")

@st.cache_data(ttl=5)
def load_csv():
    if os.path.exists(CSV):
        return pd.read_csv(CSV, encoding="latin-1")
    return pd.DataFrame()

@st.cache_data(ttl=5)
def load_summary():
    if os.path.exists(JSON):
        with open(JSON) as f:
            return json.load(f)
    return {}

df      = load_csv()
summary = load_summary()

# ── Top metrics ──────────────────────────────────────────────────────────────
if summary:
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Logs",       summary.get("total_logs", 0))
    c2.metric("Regex Classified", summary.get("source_counts", {}).get("regex", 0))
    c3.metric("LLM Classified",   summary.get("source_counts", {}).get("llm", 0))

    mttr = summary.get("mttr", {})
    c4.metric("MTTR without AI",  f"{mttr.get('without_ai', 0)} min")
    c5.metric("MTTR with AI",     f"{mttr.get('with_ai', 0)} min",
              delta=f"-{mttr.get('improvement', 0):.1f}%",
              delta_color="inverse")

st.divider()

# ── Row 1: Failure distribution + Confidence ─────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Failure Distribution")
    if summary and "failure_distribution" in summary:
        fd = summary["failure_distribution"]
        fig = px.pie(
            values=list(fd.values()),
            names=list(fd.keys()),
            color_discrete_sequence=px.colors.qualitative.Set3,
            hole=0.4
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(showlegend=False, margin=dict(t=0,b=0,l=0,r=0), height=300)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data yet — run analysis first")

with col2:
    st.subheader("MTTR: With vs Without AI")
    if summary and "mttr" in summary:
        mttr = summary["mttr"]
        fig2 = go.Figure()
        fig2.add_bar(name="Without AI", x=["MTTR"], y=[mttr["without_ai"]],
                     marker_color="#ef4444", text=[f"{mttr['without_ai']} min"],
                     textposition="outside")
        fig2.add_bar(name="With AI",    x=["MTTR"], y=[mttr["with_ai"]],
                     marker_color="#22c55e", text=[f"{mttr['with_ai']} min"],
                     textposition="outside")
        fig2.update_layout(
            barmode="group", height=300,
            margin=dict(t=20,b=0,l=0,r=0),
            yaxis_title="Minutes",
            legend=dict(orientation="h", y=1.1)
        )
        st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── Row 2: Full analysis log table ───────────────────────────────────────────
st.subheader("📋 Full Analysis Log")

if not df.empty:
    # Colour-code confidence
    def colour_confidence(val):
        if val == "High":   return "background-color: #dcfce7; color: #14532d"
        if val == "Medium": return "background-color: #fef9c3; color: #713f12"
        return "background-color: #fee2e2; color: #7f1d1d"

    def colour_source(val):
        if val == "llm":   return "background-color: #e0e7ff; color: #3730a3"
        return "background-color: #f1f5f9; color: #334155"

    styled = (
        df.style
        .applymap(colour_confidence, subset=["confidence"])
        .applymap(colour_source,     subset=["source"])
    )
    st.dataframe(styled, use_container_width=True, height=300)

    # Download button
    st.download_button(
        label="⬇️ Download analysis_log.csv",
        data=df.to_csv(index=False),
        file_name="analysis_log.csv",
        mime="text/csv"
    )
else:
    st.info("No analysis data yet — run: py -3.10 cli.py from the backend folder")

st.divider()

# ── Row 3: Self-healing actions taken ────────────────────────────────────────
st.subheader("⚡ Self-Healing Actions Taken")

if not df.empty and "action_taken" in df.columns:
    action_df = df[["timestamp","filename","type","action_taken"]].copy()
    action_df.columns = ["Timestamp", "File", "Issue Type", "Action"]
    st.dataframe(action_df, use_container_width=True, height=250)

st.divider()

# ── Footer ────────────────────────────────────────────────────────────────────
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  |  "
           f"Hack2Hire 1.0 — Problem 08  |  T John Institute of Technology")

if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()