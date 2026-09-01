"""
Employee Attrition Risk Diagnostics & Policy Simulator — Fireart Studio Light Edition (Zero Emojis)
"""

import streamlit as st
import pandas as pd
import numpy as np
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
from app.backend.data_loader import get_attrition_df

st.set_page_config(page_title="Retention Diagnostics // PULSE", layout="wide")
st.markdown(FIREART_CSS, unsafe_allow_html=True)

st.markdown("""
<div class="fireart-badge"><span class="fireart-dot"></span> RETENTION INTELLIGENCE ENGINE</div>
<div class="fireart-hero-title">AI Attrition Diagnostics & <span>Policy Simulator</span></div>
<div class="fireart-hero-subtitle">Evaluate individual churn probabilities, uncover underlying root causes, and simulate retention policy interventions in real time.</div>
""", unsafe_allow_html=True)

df_att = get_attrition_df()

# Preset Selector
st.sidebar.markdown("### Profile Archetypes")
preset = st.sidebar.selectbox(
    "Load Benchmark Profile",
    options=["Custom Profile", "High Risk: Overworked Sales Rep", "Moderate Risk: Stagnant Technician", "Low Risk: Principal Scientist", "Executive: Senior Director"]
)

# Preset values
if "High Risk" in preset:
    d_age, d_dept, d_role, d_income, d_ot, d_dist, d_tenure, d_promo, d_sat = 27, "Sales", "Sales Representative", 2600, "Yes", 24, 2, 2, 1
elif "Moderate Risk" in preset:
    d_age, d_dept, d_role, d_income, d_ot, d_dist, d_tenure, d_promo, d_sat = 33, "Research & Development", "Laboratory Technician", 4100, "No", 14, 5, 4, 2
elif "Principal" in preset:
    d_age, d_dept, d_role, d_income, d_ot, d_dist, d_tenure, d_promo, d_sat = 42, "Research & Development", "Research Scientist", 9800, "No", 4, 8, 1, 4
elif "Executive" in preset:
    d_age, d_dept, d_role, d_income, d_ot, d_dist, d_tenure, d_promo, d_sat = 50, "Sales", "Manager", 16500, "No", 3, 15, 1, 4
else:
    d_age, d_dept, d_role, d_income, d_ot, d_dist, d_tenure, d_promo, d_sat = 31, "Sales", "Sales Executive", 5400, "No", 8, 4, 1, 3

# Main Input Grid
st.markdown("### Staff Attributes & Behavioral Signals")

c1, c2, c3 = st.columns(3)

with c1:
    with st.container(border=True):
        st.markdown("#### Demographics & Role")
        age = st.number_input("Age", min_value=18, max_value=70, value=d_age)
        dept_opts = ["Sales", "Research & Development", "Human Resources"]
        dept_idx = dept_opts.index(d_dept) if d_dept in dept_opts else 0
        dept = st.selectbox("Department", options=dept_opts, index=dept_idx)
        
        role_opts = sorted(df_att["JobRole"].unique())
        role_idx = role_opts.index(d_role) if d_role in role_opts else 0
        role = st.selectbox("Job Role", options=role_opts, index=role_idx)
        income = st.number_input("Monthly Income ($)", min_value=1000, max_value=25000, value=d_income, step=250)
        travel = st.selectbox("Business Travel", options=["Non-Travel", "Travel_Rarely", "Travel_Frequently"], index=1)

with c2:
    with st.container(border=True):
        st.markdown("#### Workload & Tenure")
        ot_idx = 1 if d_ot == "Yes" else 0
        overtime = st.selectbox("Mandatory OverTime", options=["No", "Yes"], index=ot_idx)
        distance = st.slider("Commute Distance (miles)", min_value=1, max_value=35, value=d_dist)
        total_exp = st.slider("Total Career Experience (Years)", min_value=0, max_value=40, value=max(d_tenure + 2, 4))
        tenure = st.slider("Tenure at Company (Years)", min_value=0, max_value=30, value=d_tenure)
        years_in_role = st.slider("Years in Current Position", min_value=0, max_value=20, value=min(d_tenure, 3))

with c3:
    with st.container(border=True):
        st.markdown("#### Sentiment & Growth")
        years_since_promo = st.slider("Years Since Last Promotion", min_value=0, max_value=15, value=d_promo)
        years_with_mgr = st.slider("Years with Current Lead", min_value=0, max_value=20, value=min(d_tenure, 3))
        job_sat = st.slider("Job Satisfaction (1-4)", min_value=1, max_value=4, value=d_sat)
        env_sat = st.slider("Environment Culture (1-4)", min_value=1, max_value=4, value=3)
        wlb = st.slider("Work-Life Balance (1-4)", min_value=1, max_value=4, value=3)
        marital = st.selectbox("Marital Status", options=["Single", "Married", "Divorced"], index=0)

emp_payload = {
    "Age": age,
    "Department": dept,
    "JobRole": role,
    "MonthlyIncome": income,
    "BusinessTravel": travel,
    "OverTime": overtime,
    "DistanceFromHome": distance,
    "TotalWorkingYears": total_exp,
    "YearsAtCompany": tenure,
    "YearsInCurrentRole": years_in_role,
    "YearsSinceLastPromotion": years_since_promo,
    "YearsWithCurrManager": years_with_mgr,
    "JobSatisfaction": job_sat,
    "EnvironmentSatisfaction": env_sat,
    "RelationshipSatisfaction": 3,
    "WorkLifeBalance": wlb,
    "MaritalStatus": marital,
    "Education": 3,
    "EducationField": "Life Sciences",
    "Gender": "Male",
    "HourlyRate": 65,
    "DailyRate": 800,
    "MonthlyRate": 15000,
    "JobInvolvement": 3,
    "JobLevel": 2,
    "NumCompaniesWorked": 2,
    "PercentSalaryHike": 14,
    "PerformanceRating": 3,
    "StockOptionLevel": 1,
    "TrainingTimesLastYear": 2
}

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

if st.button("RUN RETENTION ASSESSMENT", type="primary"):
    res = predictor.predict_attrition(emp_payload)
    
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    st.markdown("### Model Diagnostics")
    
    diag_c1, diag_c2 = st.columns([1, 1.4])
    
    with diag_c1:
        with st.container(border=True):
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=res["attrition_probability"],
                title={"text": f"<b>ATTRITION PROBABILITY</b><br><span style='color:{res['risk_color']}; font-size:1.05rem;'>RISK TIER: {res['risk_level'].upper()}</span>", "font": {"family": "Space Grotesk", "color": "#000000"}},
                number={"suffix": "%", "font": {"size": 44, "color": res["risk_color"], "family": "Space Grotesk"}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "#000000"},
                    "bar": {"color": res["risk_color"]},
                    "bgcolor": "#FAFAFA",
                    "borderwidth": 1,
                    "bordercolor": "#CBD5E1",
                    "steps": [
                        {"range": [0, 20], "color": "rgba(16, 185, 129, 0.15)"},
                        {"range": [20, 33], "color": "rgba(245, 158, 11, 0.15)"},
                        {"range": [33, 60], "color": "rgba(255, 71, 10, 0.2)"},
                        {"range": [60, 100], "color": "rgba(255, 71, 10, 0.35)"}
                    ],
                    "threshold": {
                        "line": {"color": "#FF470A", "width": 4},
                        "thickness": 0.75,
                        "value": 33
                    }
                }
            ))
            apply_fireart_plotly_theme(fig_gauge, height=300)
            fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=20, r=20, t=60, b=20))
            st.plotly_chart(fig_gauge, use_container_width=True)

    with diag_c2:
        with st.container(border=True):
            st.markdown("#### Primary Attrition Catalysts")
            for driver in res["risk_drivers"]:
                st.markdown(f"<div style='padding:6px 0; color:#000000;'>• <strong style='color:#DC2626;'>{driver}</strong></div>", unsafe_allow_html=True)

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            st.markdown("#### Prescriptive Retention Interventions")
            for action in res["retention_actions"]:
                st.markdown(f"<div style='padding:4px 0; color:#047857; font-weight:600;'>[Action] {action}</div>", unsafe_allow_html=True)

    # What-if simulator
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    st.markdown("### Real-Time Retention Policy Simulator")
    
    with st.container(border=True):
        sim_col1, sim_col2 = st.columns(2)
        
        with sim_col1:
            sim_salary_boost = st.slider("Simulate Compensation Hike (%)", min_value=0, max_value=50, value=15, step=5)
            sim_remove_ot = st.checkbox("Eliminate Mandatory Overtime (Set OverTime = No)", value=(overtime == "Yes"))
        
        sim_payload = emp_payload.copy()
        sim_payload["MonthlyIncome"] = int(income * (1 + sim_salary_boost / 100.0))
        if sim_remove_ot:
            sim_payload["OverTime"] = "No"
        
        sim_res = predictor.predict_attrition(sim_payload)
        delta_risk = round(res["attrition_probability"] - sim_res["attrition_probability"], 1)

        with sim_col2:
            st.markdown("#### Impact of Policy Intervention:")
            st.metric(
                label="Adjusted Churn Risk",
                value=f"{sim_res['attrition_probability']}%",
                delta=f"-{delta_risk}% Risk Reduction" if delta_risk > 0 else "0% Change",
                delta_color="normal"
            )
            st.markdown(f"<span class='pill pill-green'>New Risk Tier: {sim_res['risk_level'].upper()}</span> (Adjusted Salary: ${sim_payload['MonthlyIncome']:,}/mo)", unsafe_allow_html=True)
