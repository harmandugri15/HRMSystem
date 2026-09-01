"""
Training Program Impact, Budget ROI & Outcome Forecaster — Fireart Studio Light Edition (Zero Emojis)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

if "app" in sys.modules and not hasattr(sys.modules["app"], "__path__"):
    del sys.modules["app"]

from app.frontend.theme import FIREART_CSS, apply_fireart_plotly_theme
from app.backend.predictor import predictor
from app.backend.data_loader import get_training_df

st.set_page_config(page_title="Training Impact // PULSE", layout="wide")
st.markdown(FIREART_CSS, unsafe_allow_html=True)

st.markdown("""
<div class="fireart-badge"><span class="fireart-dot"></span> CORPORATE LEARNING INTELLIGENCE</div>
<div class="fireart-hero-title">Training Program Efficacy and <span>Budget ROI</span></div>
<div class="fireart-hero-subtitle">Track course pass rates, measure departmental investment efficiency, and forecast employee course completion prior to enrollment.</div>
""", unsafe_allow_html=True)

df_train = get_training_df()

t1, t2, t3, t4 = st.columns(4)
total_courses = len(df_train)
avg_cost = int(df_train["Training Cost"].mean())
overall_pass_rate = round(df_train["TrainingSuccess"].mean() * 100, 1)
total_spend = int(df_train["Training Cost"].sum())

with t1:
    st.markdown(f"""
    <div class='fireart-card'>
        <div class='pill pill-blue'>Enrollments</div>
        <div class='fireart-metric-val'>{total_courses:,}</div>
        <div class='fireart-metric-label'>Total Trainees</div>
    </div>
    """, unsafe_allow_html=True)

with t2:
    st.markdown(f"""
    <div class='fireart-card'>
        <div class='pill pill-orange'>Unit Cost</div>
        <div class='fireart-metric-val'>${avg_cost:,}</div>
        <div class='fireart-metric-label'>Average Cost / Course</div>
    </div>
    """, unsafe_allow_html=True)

with t3:
    st.markdown(f"""
    <div class='fireart-card'>
        <div class='pill pill-green'>Pass Rate</div>
        <div class='fireart-metric-val' style='color:#059669;'>{overall_pass_rate}%</div>
        <div class='fireart-metric-label'>Completion Efficiency</div>
    </div>
    """, unsafe_allow_html=True)

with t4:
    st.markdown(f"""
    <div class='fireart-card'>
        <div class='pill pill-gray'>L&D Capital</div>
        <div class='fireart-metric-val'>${total_spend:,}</div>
        <div class='fireart-metric-label'>Total Training Spend</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

st.markdown("### 1. Training Program Performance and Outcomes")

c1, c2 = st.columns(2)

with c1:
    prog_stats = (
        df_train.groupby("Training Program Name")
        .agg(
            Success_Rate=("TrainingSuccess", "mean"),
            Count=("Training Outcome", "count"),
            Avg_Cost=("Training Cost", "mean")
        )
        .reset_index()
    )
    prog_stats["Success Rate (%)"] = (prog_stats["Success_Rate"] * 100).round(1)

    fig_prog = px.bar(
        prog_stats.sort_values(by="Success Rate (%)", ascending=False),
        x="Training Program Name",
        y="Success Rate (%)",
        color="Success Rate (%)",
        color_continuous_scale=[[0, "#CBD5E1"], [0.5, "#FF561D"], [1, "#FF470A"]],
        text="Success Rate (%)"
    )
    apply_fireart_plotly_theme(fig_prog, height=360, title="Course Completion Rate (%)")
    st.plotly_chart(fig_prog, use_container_width=True)

with c2:
    fig_out = px.pie(
        df_train,
        names="Training Outcome",
        color_discrete_sequence=["#059669", "#2563EB", "#FF470A", "#71717A"],
        hole=0.5
    )
    apply_fireart_plotly_theme(fig_out, height=360, title="Global Outcome Breakdown")
    st.plotly_chart(fig_out, use_container_width=True)

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

st.markdown("### 2. Pre-Enrollment Completion Forecaster")

with st.container(border=True):
    p_col1, p_col2, p_col3 = st.columns(3)

    with p_col1:
        p_dept = st.selectbox("Department", options=sorted(df_train["DepartmentType"].unique()))
        p_prog = st.selectbox("Course Title", options=sorted(df_train["Training Program Name"].unique()))
        p_type = st.selectbox("Delivery Mode", options=["Internal", "External"])

    with p_col2:
        p_days = st.slider("Duration (Days)", min_value=1, max_value=10, value=3)
        p_cost = st.number_input("Course Cost ($)", min_value=100, max_value=2000, value=550, step=50)
        p_age = st.slider("Trainee Age", min_value=20, max_value=65, value=34)

    with p_col3:
        p_eng = st.slider("Engagement Sentiment (1-5)", min_value=1, max_value=5, value=4)
        p_sat = st.slider("Satisfaction Score (1-5)", min_value=1, max_value=5, value=4)
        p_wlb = st.slider("Work-Life Balance (1-5)", min_value=1, max_value=5, value=3)

if st.button("FORECAST COMPLETION PROBABILITY", type="primary"):
    train_payload = {
        "DepartmentType": p_dept,
        "Training Program Name": p_prog,
        "Training Type": p_type,
        "Training Duration(Days)": p_days,
        "Training Cost": p_cost,
        "Age": p_age,
        "Engagement Score": p_eng,
        "Satisfaction Score": p_sat,
        "Work-Life Balance Score": p_wlb
    }
    
    t_res = predictor.predict_training_outcome(train_payload)
    
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    res_c1, res_c2 = st.columns(2)
    
    with res_c1:
        st.markdown(f"""
        <div class='fireart-card'>
            <div class='pill pill-green'>Completion Forecast</div>
            <div class='fireart-metric-val' style='color:#059669;'>{t_res['success_probability']}%</div>
            <div class='fireart-metric-label'>Status: <strong>{t_res['predicted_outcome']}</strong></div>
        </div>
        """, unsafe_allow_html=True)
        
    with res_c2:
        st.markdown(f"""
        <div class='fireart-card'>
            <div class='pill pill-orange'>Unit Economics</div>
            <div class='fireart-metric-val'>${t_res['cost_per_day']}</div>
            <div class='fireart-metric-label'>Calculated Cost / Day</div>
        </div>
        """, unsafe_allow_html=True)
