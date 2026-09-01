"""
Performance Evaluation & Promotion Readiness Matrix — Fireart Studio Light Edition (Zero Emojis)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

if "app" in sys.modules and not hasattr(sys.modules["app"], "__path__"):
    del sys.modules["app"]

from app.frontend.theme import FIREART_CSS, apply_fireart_plotly_theme
from app.backend.predictor import predictor
from app.backend.data_loader import get_performance_df

st.set_page_config(page_title="Performance Matrix // PULSE", layout="wide")
st.markdown(FIREART_CSS, unsafe_allow_html=True)

st.markdown("""
<div class="fireart-badge"><span class="fireart-dot"></span> TALENT BENCHMARKING MATRIX</div>
<div class="fireart-hero-title">360° Performance Evaluation and <span>Promotion Readiness</span></div>
<div class="fireart-hero-subtitle">Algorithmic capability scoring across KPI velocity, task execution efficiency, attendance consistency, and peer feedback benchmarks.</div>
""", unsafe_allow_html=True)

df_perf = get_performance_df()

tab1, tab2 = st.tabs(["Talent Promotion Calculator", "Workforce Performance Matrix (5,000 Records)"])

with tab1:
    st.markdown("### Evaluate Individual Contributor Profile")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            st.markdown("#### Department and Scope")
            emp_dept = st.selectbox("Department", options=sorted(df_perf["Department"].unique()), index=0)
            emp_role = st.selectbox("Job Role", options=sorted(df_perf["Job Role"].unique()), index=0)
            kpi_score = st.slider("KPI Benchmark Score (0-100)", min_value=0.0, max_value=100.0, value=88.0, step=0.5)
        
    with col2:
        with st.container(border=True):
            st.markdown("#### Execution and Attendance")
            task_comp = st.slider("Task Completion Velocity (%)", min_value=0.0, max_value=100.0, value=90.0, step=0.5)
            attendance = st.slider("Attendance Consistency (%)", min_value=50.0, max_value=100.0, value=96.0, step=0.5)
            hours_logged = st.number_input("Average Weekly Hours Logged", min_value=20, max_value=70, value=42)

    with col3:
        with st.container(border=True):
            st.markdown("#### Feedback and Leadership")
            peer_rating = st.slider("Peer Review Score (1-5)", min_value=1.0, max_value=5.0, value=4.6, step=0.1)
            mgr_feedback = st.slider("Manager Rating (1-5)", min_value=1.0, max_value=5.0, value=4.5, step=0.1)
            training_hours = st.number_input("Completed Training Hours", min_value=0, max_value=100, value=25)

    perf_payload = {
        "Department": emp_dept,
        "Job Role": emp_role,
        "KPI Score": kpi_score,
        "Task Completion (%)": task_comp,
        "Attendance (%)": attendance,
        "Peer Rating": peer_rating,
        "Work Hours Logged": hours_logged,
        "Manager Feedback": mgr_feedback,
        "Training Hours": training_hours
    }

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    if st.button("CALCULATE PROMOTION READINESS", type="primary"):
        res = predictor.predict_promotion(perf_payload)
        
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        st.markdown("### Diagnostic Assessment & Capability Spectrum")
        
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.markdown(f"""
            <div class='fireart-card'>
                <div class='pill pill-blue'>Productivity Score</div>
                <div class='fireart-metric-val'>{res['productivity_index']}<span style='font-size:1.2rem; color:#71717A;'>/100</span></div>
                <div class='fireart-metric-label'>Tier: <strong style='color:#059669;'>{res['performance_tier']}</strong></div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            badge_class = "pill-green" if res["is_eligible"] else "pill-orange"
            status_text = "READY FOR ADVANCEMENT" if res["is_eligible"] else "UNDER DEVELOPMENT"
            st.markdown(f"""
            <div class='fireart-card'>
                <div class='pill {badge_class}'>Promotion Probability</div>
                <div class='fireart-metric-val' style='color:#059669;'>{res['promotion_probability']}%</div>
                <div class='fireart-metric-label'>Status: <strong>{status_text}</strong></div>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
            <div class='fireart-card'>
                <div class='pill pill-gray'>Leadership Recommendation</div>
                <p style='margin-top:10px; color:#000000; font-size:0.92rem; line-height:1.6; font-weight:500;'>{res['recommendation']}</p>
            </div>
            """, unsafe_allow_html=True)

        categories = ["KPI Target", "Task Completion", "Attendance", "Peer Feedback", "Manager Rating"]
        values = [kpi_score, task_comp, attendance, peer_rating * 20, mgr_feedback * 20]
        
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill="toself",
            fillcolor="rgba(255, 71, 10, 0.15)",
            line=dict(color="#FF470A", width=2),
            name="Performance Profile"
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], gridcolor="#CBD5E1", linecolor="#CBD5E1", tickfont=dict(color="#000000")),
                angularaxis=dict(gridcolor="#CBD5E1", linecolor="#CBD5E1", tickfont=dict(color="#000000"))
            ),
            showlegend=False,
            height=380
        )
        apply_fireart_plotly_theme(fig_radar, height=380, title="360° Capability Polygon")
        st.plotly_chart(fig_radar, use_container_width=True)

with tab2:
    st.markdown("### Filter & Audit Organization Talent Records")
    
    with st.container(border=True):
        f_dept = st.multiselect("Filter Departments", options=sorted(df_perf["Department"].unique()), default=sorted(df_perf["Department"].unique())[:3])
        f_tier = st.multiselect("Filter Performance Tiers", options=list(df_perf["PerformanceTier"].unique()), default=list(df_perf["PerformanceTier"].unique()))
    
    filtered_df = df_perf[
        (df_perf["Department"].isin(f_dept)) &
        (df_perf["PerformanceTier"].isin(f_tier))
    ]
    
    st.markdown(f"Displaying **{len(filtered_df):,}** verified records:")
    st.dataframe(
        filtered_df[[
            "Employee ID", "Name", "Department", "Job Role", "ProductivityIndex",
            "PerformanceTier", "KPI Score", "Task Completion (%)", "Promotion Eligibility"
        ]],
        use_container_width=True,
        height=420
    )
