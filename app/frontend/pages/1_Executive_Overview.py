"""
Executive Workforce Analytics — Fireart Studio Light Edition (Zero Emojis)
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
from app.backend.data_loader import get_attrition_df, get_performance_df, get_training_df

st.set_page_config(page_title="Executive Analytics // PULSE", layout="wide")
st.markdown(FIREART_CSS, unsafe_allow_html=True)

# Page Header
st.markdown("""
<div class="fireart-badge"><span class="fireart-dot"></span> EXECUTIVE INTELLIGENCE</div>
<div class="fireart-hero-title">Workforce Dynamics & <span>Talent Distribution</span></div>
<div class="fireart-hero-subtitle">Comprehensive analytical view of retention metrics, compensation variance, organizational performance tiers, and corporate training allocations.</div>
""", unsafe_allow_html=True)

df_att = get_attrition_df()
df_perf = get_performance_df()
df_train = get_training_df()

# Filters
st.sidebar.markdown("### Segment Filter")
dept_options = sorted(df_att["Department"].unique())
selected_dept = st.sidebar.multiselect("Select Departments", options=dept_options, default=dept_options)

filtered_att = df_att[df_att["Department"].isin(selected_dept)]

# Section 1: Turnover & Overtime Impact
st.markdown("### 1. Turnover Metrics & Overtime Impact")

r1_c1, r1_c2 = st.columns(2)

with r1_c1:
    role_att = (
        filtered_att.groupby("JobRole")["Attrition_Numeric"]
        .mean()
        .reset_index()
        .sort_values(by="Attrition_Numeric", ascending=True)
    )
    role_att["Attrition Rate (%)"] = (role_att["Attrition_Numeric"] * 100).round(1)
    
    fig_role = px.bar(
        role_att,
        x="Attrition Rate (%)",
        y="JobRole",
        orientation="h",
        color="Attrition Rate (%)",
        color_continuous_scale=[[0, "#E4E4E7"], [0.5, "#FF561D"], [1, "#FF470A"]],
        text="Attrition Rate (%)"
    )
    apply_fireart_plotly_theme(fig_role, height=380, title="Turnover Rate by Job Role (%)")
    st.plotly_chart(fig_role, use_container_width=True)

with r1_c2:
    ot_summary = (
        filtered_att.groupby(["OverTime", "Attrition"])
        .size()
        .reset_index(name="Count")
    )
    fig_ot = px.bar(
        ot_summary,
        x="OverTime",
        y="Count",
        color="Attrition",
        barmode="group",
        color_discrete_map={"No": "#2563EB", "Yes": "#FF470A"}
    )
    apply_fireart_plotly_theme(fig_ot, height=380, title="Resignation Volume by Overtime Requirement")
    st.plotly_chart(fig_ot, use_container_width=True)

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# Section 2: Compensation Variance & Career Progression
st.markdown("### 2. Compensation Structure & Career Experience")

r2_c1, r2_c2 = st.columns(2)

with r2_c1:
    fig_sal = px.box(
        filtered_att,
        x="Department",
        y="MonthlyIncome",
        color="Attrition",
        color_discrete_map={"No": "#059669", "Yes": "#FF470A"}
    )
    apply_fireart_plotly_theme(fig_sal, height=380, title="Monthly Salary Distribution by Department ($)")
    st.plotly_chart(fig_sal, use_container_width=True)

with r2_c2:
    fig_exp = px.scatter(
        filtered_att,
        x="TotalWorkingYears",
        y="MonthlyIncome",
        color="Attrition",
        size="YearsAtCompany",
        hover_data=["JobRole", "Age"],
        color_discrete_map={"No": "#2563EB", "Yes": "#FF470A"}
    )
    apply_fireart_plotly_theme(fig_exp, height=380, title="Experience vs. Income Correlation (Bubble = Tenure)")
    st.plotly_chart(fig_exp, use_container_width=True)

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# Section 3: Performance Distribution & Training Spend
st.markdown("### 3. Performance Breakdown & Department Training Spend")

r3_c1, r3_c2 = st.columns(2)

with r3_c1:
    tier_counts = df_perf["PerformanceTier"].value_counts().reset_index()
    tier_counts.columns = ["Tier", "Count"]
    fig_tier = px.pie(
        tier_counts,
        names="Tier",
        values="Count",
        color_discrete_sequence=["#059669", "#2563EB", "#FF470A"],
        hole=0.5
    )
    apply_fireart_plotly_theme(fig_tier, height=360, title="Workforce Performance Tier Distribution")
    st.plotly_chart(fig_tier, use_container_width=True)

with r3_c2:
    dept_train = (
        df_train.groupby("DepartmentType")["Training Cost"]
        .sum()
        .reset_index()
        .sort_values(by="Training Cost", ascending=False)
    )
    fig_train = px.bar(
        dept_train,
        x="DepartmentType",
        y="Training Cost",
        color="Training Cost",
        color_continuous_scale=[[0, "#E4E4E7"], [1, "#FF470A"]]
    )
    apply_fireart_plotly_theme(fig_train, height=360, title="Total Training Budget Allocation by Department ($)")
    st.plotly_chart(fig_train, use_container_width=True)
