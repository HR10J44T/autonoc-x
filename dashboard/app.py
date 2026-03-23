from __future__ import annotations
import os
import pandas as pd
import requests
import streamlit as st
import plotly.express as px

API_URL = os.getenv("AUTONOC_API_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="AutoNOC-X",
    page_icon="💣",
    layout="wide",
)

st.markdown(
    '''
    <style>
    .stApp { background: linear-gradient(180deg, #090d12 0%, #0e131b 100%); color: #e8eef9; }
    .metric-card {
        background: rgba(18,26,36,0.88);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 20px;
        padding: 18px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.25);
    }
    .section-title { font-size: 1.1rem; font-weight: 700; margin-bottom: 0.6rem; color: #f4f7fb;}
    .small-muted { color: #98a4b5; font-size: 0.9rem; }
    </style>
    ''',
    unsafe_allow_html=True,
)

st.title("AutoNOC-X Command Center")
st.caption("Self-Healing Linux NOC Automation Dashboard")

top1, top2, top3 = st.columns([3,1,1])
with top2:
    if st.button("Run Scan", use_container_width=True):
        try:
            requests.post(f"{API_URL}/scan", timeout=20)
            st.success("Scan completed")
        except Exception as exc:
            st.error(f"Unable to run scan: {exc}")

with top3:
    st.link_button("API Docs", f"{API_URL}/docs", use_container_width=True)

try:
    data = requests.get(f"{API_URL}/dashboard-data", timeout=10).json()
except Exception as exc:
    st.error(f"Backend unavailable: {exc}")
    st.stop()

metrics_df = pd.DataFrame(data.get("metrics", []))
incidents_df = pd.DataFrame(data.get("incidents", []))
actions_df = pd.DataFrame(data.get("actions", []))

active_incidents = len(incidents_df.index)
critical_incidents = int((incidents_df["severity"] == "critical").sum()) if not incidents_df.empty else 0
auto_heals = len(actions_df.index)
healthy_checks = int((metrics_df["status"] == "healthy").sum()) if not metrics_df.empty else 0

c1, c2, c3, c4 = st.columns(4)
for col, title, value, sub in [
    (c1, "Healthy Checks", healthy_checks, "Current successful checks"),
    (c2, "Active Incidents", active_incidents, "Warning + critical signals"),
    (c3, "Critical Incidents", critical_incidents, "Immediate attention"),
    (c4, "Auto-Heal Actions", auto_heals, "Executed or simulated"),
]:
    with col:
        st.markdown(f'<div class="metric-card"><div class="small-muted">{title}</div><h2>{value}</h2><div class="small-muted">{sub}</div></div>', unsafe_allow_html=True)

left, right = st.columns([1.25, 1])

with left:
    st.markdown('<div class="section-title">Latest Metrics</div>', unsafe_allow_html=True)
    if metrics_df.empty:
        st.info("No metrics yet. Run a scan.")
    else:
        metrics_show = metrics_df[["created_at", "node_name", "metric_type", "status", "value", "unit", "details"]].copy()
        st.dataframe(metrics_show, use_container_width=True, hide_index=True)

        sys_df = metrics_df[metrics_df["metric_type"] == "system"].copy()
        if not sys_df.empty:
            fig = px.bar(
                sys_df,
                x="target",
                y="value",
                color="status",
                title="Local System Utilization",
                text="value",
            )
            fig.update_layout(template="plotly_dark", height=320)
            st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown('<div class="section-title">Incident Feed</div>', unsafe_allow_html=True)
    if incidents_df.empty:
        st.success("No incidents stored yet.")
    else:
        for _, row in incidents_df.head(10).iterrows():
            severity_color = {
                "critical": "#ff3d00",
                "high": "#ff9800",
                "medium": "#ffc107",
                "info": "#00b0ff",
            }.get(str(row["severity"]).lower(), "#9aa5b1")
            st.markdown(
                f'''
                <div class="metric-card" style="border-left: 4px solid {severity_color}; margin-bottom: 12px;">
                    <div class="small-muted">{row["created_at"]}</div>
                    <div style="font-size:1rem; font-weight:700;">{row["title"]}</div>
                    <div class="small-muted">{row["node_name"]} · {row["incident_type"]} · {row["severity"]}</div>
                    <div style="margin-top:8px;">{row["details"]}</div>
                    <div class="small-muted" style="margin-top:8px;">Auto-heal: {row["auto_heal_status"]}</div>
                </div>
                ''',
                unsafe_allow_html=True,
            )

st.markdown('<div class="section-title">Auto-Healing Activity</div>', unsafe_allow_html=True)
if actions_df.empty:
    st.info("No actions yet.")
else:
    st.dataframe(
        actions_df[["created_at", "node_name", "action_type", "command", "execution_mode", "result"]],
        use_container_width=True,
        hide_index=True,
    )
