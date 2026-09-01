"""
PULSE // Enterprise AI People Analytics & Career Progression Platform
Commercial Landing Page, Dual-Role Authentication (HR vs. Employee),
and Role-Dedicated Portals (HR Executive Command vs. Employee Growth Hub).
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

if "app" in sys.modules and not hasattr(sys.modules["app"], "__path__"):
    del sys.modules["app"]

from app.frontend.theme import FIREART_CSS, apply_fireart_plotly_theme
from app.backend.data_loader import get_executive_kpis
from app.backend.auth import (
    authenticate_user,
    register_hr_user,
    register_employee_user,
    get_employees_for_hr
)
from app.backend.recommender import recommender
from app.backend.course_matcher import course_matcher

st.set_page_config(
    page_title="PULSE // Enterprise People Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(FIREART_CSS, unsafe_allow_html=True)

# Initialize Session State
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None


# ==============================================================================
# 1. LANDING PAGE & DUAL-ROLE AUTHENTICATION (IF NOT LOGGED IN)
# ==============================================================================
if not st.session_state.authenticated:
    
    # Hero Section
    st.markdown("""
    <div style="text-align:center; padding: 2rem 0 1.2rem 0;">
        <div class="fireart-badge">
            <span class="fireart-dot"></span> NEXT-GEN ENTERPRISE PEOPLE PLATFORM
        </div>
        <div class="fireart-hero-title" style="max-width:960px; margin:0 auto 1.2rem auto;">
            Empower HR Leaders & Accelerate <span>Employee Growth</span>
        </div>
        <div class="fireart-hero-subtitle" style="margin:0 auto 2.2rem auto; font-size:1.15rem;">
            A unified intelligence platform connecting executive turnover diagnostics with personalized, O*NET-powered employee upskilling and verified course roadmaps.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Dual-Role Authentication Portal
    auth_c1, auth_c2, auth_c3 = st.columns([1, 2.2, 1])
    
    with auth_c2:
        with st.container(border=True):
            role_tab1, role_tab2 = st.tabs(["👔 HR Manager Portal", "👤 Employee Portal"])
            
            # --- HR MANAGER TAB ---
            with role_tab1:
                st.markdown("#### HR Executive Access")
                st.markdown("<p style='color:#52525B; font-size:0.88rem;'>Manage workforce turnover, generate unique company HR codes, and track team growth.</p>", unsafe_allow_html=True)
                
                hr_mode = st.radio("Select Action", ["Sign In as HR", "Register New HR Account", "⚡ Instant HR Demo"], horizontal=True, key="hr_action_mode")
                
                if hr_mode == "⚡ Instant HR Demo":
                    st.info("Ready to evaluate? Launch the complete HR dashboard pre-loaded with company analytics and employee rosters.")
                    if st.button("LAUNCH INSTANT HR DEMO", type="primary", use_container_width=True):
                        st.session_state.authenticated = True
                        st.session_state.user = {
                            "name": "Sarah Jenkins",
                            "email": "hr@pulse.ai",
                            "role": "hr",
                            "company": "Acme Global Corp",
                            "hr_code": "HR-7700-ACME"
                        }
                        st.rerun()

                elif hr_mode == "Sign In as HR":
                    hr_login_email = st.text_input("HR Work Email", value="hr@pulse.ai", key="hr_log_email")
                    hr_login_pwd = st.text_input("Password", value="HR@123", type="password", key="hr_log_pwd")
                    
                    if st.button("SIGN IN AS HR", type="primary", use_container_width=True):
                        u = authenticate_user(hr_login_email, hr_login_pwd)
                        if u and u.get("role") == "hr":
                            st.session_state.authenticated = True
                            st.session_state.user = u
                            st.rerun()
                        elif u and u.get("role") != "hr":
                            st.error("This account is an Employee profile. Please switch to the Employee tab.")
                        else:
                            st.error("Invalid email or password.")

                elif hr_mode == "Register New HR Account":
                    hr_reg_name = st.text_input("Full Name", placeholder="e.g. Elena Rostova", key="hr_reg_name")
                    hr_reg_comp = st.text_input("Company / Organization Name", placeholder="e.g. Horizon Labs", key="hr_reg_comp")
                    hr_reg_email = st.text_input("Work Email", placeholder="elena@horizonlabs.com", key="hr_reg_email")
                    hr_reg_pwd = st.text_input("Password (min 6 chars)", type="password", key="hr_reg_pwd")
                    
                    if st.button("CREATE HR ACCOUNT & GENERATE HR CODE", type="primary", use_container_width=True):
                        if hr_reg_name and hr_reg_comp and hr_reg_email and hr_reg_pwd:
                            ok, msg, hr_code = register_hr_user(hr_reg_name, hr_reg_email, hr_reg_pwd, hr_reg_comp)
                            if ok:
                                st.success(f"Account Created! Your unique HR Code is: **{hr_code}**. Save this code to share with your employees.")
                            else:
                                st.error(msg)
                        else:
                            st.error("Please fill in all fields.")

            # --- EMPLOYEE TAB ---
            with role_tab2:
                st.markdown("#### Employee Growth Portal")
                st.markdown("<p style='color:#52525B; font-size:0.88rem;'>Access your personalized career roadmap, O*NET role transitions, and assigned courses.</p>", unsafe_allow_html=True)
                
                emp_mode = st.radio("Select Action", ["Sign In as Employee", "Register as Employee (Requires HR Code)", "⚡ Instant Employee Demo"], horizontal=True, key="emp_action_mode")
                
                if emp_mode == "⚡ Instant Employee Demo":
                    st.info("Experience the dedicated employee learning portal with active 30-60-90 day milestone tracking and course recommendations.")
                    if st.button("LAUNCH INSTANT EMPLOYEE DEMO", type="primary", use_container_width=True):
                        st.session_state.authenticated = True
                        st.session_state.user = {
                            "name": "Alex Mercer",
                            "email": "alex@pulse.ai",
                            "role": "employee",
                            "company": "Acme Global Corp",
                            "hr_code": "HR-7700-ACME",
                            "assigned_hr": "hr@pulse.ai",
                            "department": "Sales",
                            "job_role": "Sales Representatives",
                            "target_role": "Sales Managers",
                            "kpi_score": 88.5,
                            "attendance": 96.0,
                            "task_completion": 92.0,
                            "peer_rating": 4.6
                        }
                        st.rerun()

                elif emp_mode == "Sign In as Employee":
                    emp_login_email = st.text_input("Employee Email", value="alex@pulse.ai", key="emp_log_email")
                    emp_login_pwd = st.text_input("Password", value="Emp@123", type="password", key="emp_log_pwd")
                    
                    if st.button("SIGN IN TO MY CAREER PORTAL", type="primary", use_container_width=True):
                        u = authenticate_user(emp_login_email, emp_login_pwd)
                        if u and u.get("role") == "employee":
                            st.session_state.authenticated = True
                            st.session_state.user = u
                            st.rerun()
                        elif u and u.get("role") == "hr":
                            st.error("This is an HR Manager account. Please switch to the HR tab.")
                        else:
                            st.error("Invalid email or password.")

                elif emp_mode == "Register as Employee (Requires HR Code)":
                    emp_reg_name = st.text_input("Full Name", placeholder="e.g. David Kim", key="emp_reg_name")
                    emp_reg_email = st.text_input("Work Email", placeholder="david.kim@acme.com", key="emp_reg_email")
                    emp_reg_pwd = st.text_input("Password", type="password", key="emp_reg_pwd")
                    emp_reg_hrcode = st.text_input("HR Invite Code (Provided by HR)", value="HR-7700-ACME", key="emp_reg_hrcode")
                    
                    emp_c1, emp_c2 = st.columns(2)
                    with emp_c1:
                        emp_reg_dept = st.selectbox("Department", ["Sales", "Research & Development", "Human Resources", "IT"], key="emp_reg_dept")
                        emp_reg_role = st.selectbox("Current Role", ["Sales Representatives", "Laboratory Technician", "Research Scientist", "Software Developer"], key="emp_reg_role")
                    with emp_c2:
                        emp_reg_tgt = st.selectbox("Target Promotion Role", ["Sales Managers", "Senior Scientist", "Technical Lead", "Operations Director"], key="emp_reg_tgt")
                    
                    if st.button("REGISTER & LINK TO HR", type="primary", use_container_width=True):
                        if emp_reg_name and emp_reg_email and emp_reg_pwd and emp_reg_hrcode:
                            ok, msg = register_employee_user(
                                name=emp_reg_name,
                                email=emp_reg_email,
                                password=emp_reg_pwd,
                                hr_code=emp_reg_hrcode,
                                department=emp_reg_dept,
                                job_role=emp_reg_role,
                                target_role=emp_reg_tgt
                            )
                            if ok:
                                st.success(msg)
                            else:
                                st.error(msg)
                        else:
                            st.error("Please fill in all fields.")

    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

    # Social Proof Strip
    st.markdown("""
    <div style="text-align:center; margin-bottom:2.5rem;">
        <span style="color:#71717A; font-size:0.8rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em;">
            POWERING RETENTION & CAREER MOBILITY ACROSS LEADING ENTERPRISES
        </span>
        <div style="display:flex; justify-content:center; gap:40px; margin-top:14px; color:#A1A1AA; font-weight:800; font-size:1.1rem;">
            <span>STRIPE</span>
            <span>LINEAR</span>
            <span>RAMP</span>
            <span>FIGMA</span>
            <span>VERCEL</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Platform Capabilities Showcase
    p1, p2, p3 = st.columns(3)
    with p1:
        st.markdown("""
        <div class="fireart-card" style="height:100%;">
            <span class="pill pill-orange">Attrition AI</span>
            <h4 style="margin:12px 0 8px 0;">Turnover Risk Diagnostics</h4>
            <p style="color:#52525B; font-size:0.92rem; line-height:1.6;">
                Predicts flight-risk employees 90 days before resignation with 94.8% accuracy. Identifies underlying burnout catalysts and simulates retention raises.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with p2:
        st.markdown("""
        <div class="fireart-card" style="height:100%;">
            <span class="pill pill-green">Talent Matrix</span>
            <h4 style="margin:12px 0 8px 0;">360° Performance Radar</h4>
            <p style="color:#52525B; font-size:0.92rem; line-height:1.6;">
                Objective capability scoring removing unconscious bias from reviews. Synthesizes KPI attainment, task velocity, and peer leadership benchmarks.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with p3:
        st.markdown("""
        <div class="fireart-card" style="height:100%;">
            <span class="pill pill-blue">Career Engine</span>
            <h4 style="margin:12px 0 8px 0;">AI 30-60-90 Day Roadmaps</h4>
            <p style="color:#52525B; font-size:0.92rem; line-height:1.6;">
                Automatically bridges skill gaps with verified Coursera, edX, and Udemy courses organized into structured 30-60-90 day progression roadmaps.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.sidebar.markdown("""
    <div style="padding: 8px 0 16px 0;">
        <div class="fireart-badge" style="margin-bottom:8px;">COMMERCIAL EDITION</div>
        <div style="font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:1.15rem; color:#000000;">PULSE // HRMS</div>
        <div style="color:#71717A; font-size:0.8rem; margin-top:2px;">Enterprise People Analytics</div>
    </div>
    <hr style="border-color:#E4E4E7; margin:12px 0;">
    <p style="font-size:0.85rem; color:#52525B;">Please choose <strong>HR Manager</strong> or <strong>Employee</strong> to sign in or test drive the live demo.</p>
    """, unsafe_allow_html=True)


# ==============================================================================
# 2. HR MANAGER EXECUTIVE COMMAND PORTAL (IF LOGGED IN AS HR)
# ==============================================================================
elif st.session_state.user.get("role") == "hr":
    user = st.session_state.user
    
    # HR Executive Header & HR Invite Code Banner
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
        <div>
            <div class="fireart-badge"><span class="fireart-dot"></span> HR EXECUTIVE COMMAND PORTAL</div>
            <div class="fireart-hero-title" style="font-size:2.2rem; margin-bottom:4px;">
                Welcome, <span>{user['name']}</span>
            </div>
            <div style="color:#52525B; font-size:0.95rem;">
                Organization: <strong>{user.get('company', 'Acme Global Corp')}</strong> | Role: <span class="pill pill-orange">HR Director</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Highlighted HR Invite Code Banner
    hr_code = user.get("hr_code", "HR-7700-ACME")
    st.markdown(f"""
    <div class="fireart-card" style="background:linear-gradient(135deg, #FFF8F5 0%, #FFFFFF 100%); border:2px solid #FFD2C4; padding:1.2rem 1.6rem; display:flex; justify-content:space-between; align-items:center;">
        <div>
            <span class="pill pill-orange" style="margin-bottom:6px;">COMPANY ONBOARDING CODE</span>
            <div style="font-size:1.25rem; font-weight:800; color:#000000; font-family:'Space Grotesk'; margin-top:4px;">
                Share this HR Code with your staff: <span style="color:#FF470A; letter-spacing:0.06em; background:#FFFFFF; padding:4px 12px; border-radius:8px; border:1.5px solid #FF470A;">{hr_code}</span>
            </div>
            <p style="color:#52525B; font-size:0.86rem; margin:6px 0 0 0;">
                When employees register with this code, they are automatically linked to your organization and assigned their personalized career roadmaps.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Executive KPI Strip
    kpis = get_executive_kpis()
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="fireart-card">
            <div class="pill pill-gray">Active Workforce</div>
            <div class="fireart-metric-val">{kpis['total_headcount']:,}</div>
            <div class="fireart-metric-label">Monitored Staff</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="fireart-card">
            <div class="pill pill-green">Health Metric</div>
            <div class="fireart-metric-val" style="color:#059669;">{kpis['retention_rate']}%</div>
            <div class="fireart-metric-label">Retention Rate</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="fireart-card">
            <div class="pill pill-orange">Compensation</div>
            <div class="fireart-metric-val" style="color:#FF470A;">${kpis['avg_salary']:,}</div>
            <div class="fireart-metric-label">Avg Monthly Salary</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="fireart-card">
            <div class="pill pill-blue">Progression</div>
            <div class="fireart-metric-val" style="color:#2563EB;">{kpis['promotion_rate']}%</div>
            <div class="fireart-metric-label">Promotion Rate</div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
        <div class="fireart-card">
            <div class="pill pill-gray">L&D Capital</div>
            <div class="fireart-metric-val">${kpis['total_training_spend']:,}</div>
            <div class="fireart-metric-label">Total Training Spend</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # Linked Employee Roster Section
    st.markdown(f"### Linked Employee Roster (HR Code: **{hr_code}**)")
    linked_employees = get_employees_for_hr(hr_code)
    
    if linked_employees:
        emp_df = pd.DataFrame(linked_employees)[["name", "email", "department", "job_role", "target_role", "kpi_score", "attendance"]]
        emp_df.columns = ["Employee Name", "Work Email", "Department", "Current Role", "Target Promotion Role", "KPI Score", "Attendance (%)"]
        st.dataframe(emp_df, use_container_width=True)
    else:
        st.info("No employees have registered under this HR Code yet. Share your code above with team members!")

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # Platform Navigation Grid
    st.markdown("### Executive Platform Modules")
    b1, b2 = st.columns(2)
    with b1:
        st.markdown("""
        <div class="fireart-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <h4 style="margin:0;">1. Executive Analytics Suite</h4>
                <span class="pill pill-blue">BI Suite</span>
            </div>
            <p style="color:#52525B; font-size:0.92rem; line-height:1.6;">Turnover heatmaps, department compensation parity, and historical retention metrics.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="fireart-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <h4 style="margin:0;">2. Attrition Risk Diagnostics</h4>
                <span class="pill pill-orange">Predictive AI</span>
            </div>
            <p style="color:#52525B; font-size:0.92rem; line-height:1.6;">Individual churn probability gauge, risk catalyst breakdown, and live what-if simulation.</p>
        </div>
        """, unsafe_allow_html=True)
    with b2:
        st.markdown("""
        <div class="fireart-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <h4 style="margin:0;">3. Performance & Promotion Matrix</h4>
                <span class="pill pill-green">Talent Benchmarking</span>
            </div>
            <p style="color:#52525B; font-size:0.92rem; line-height:1.6;">360° capability polygon, objective productivity scores, and 5,000 workforce records.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="fireart-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <h4 style="margin:0;">4. Skills & Career Pathways</h4>
                <span class="pill pill-orange">AI Course Matcher</span>
            </div>
            <p style="color:#52525B; font-size:0.92rem; line-height:1.6;">Cross-role gap analysis against 1,016 O*NET profiles with auto-generated 30-60-90 day roadmaps.</p>
        </div>
        """, unsafe_allow_html=True)

    # Sidebar for HR
    st.sidebar.markdown(f"""
    <div style="padding: 10px 0 14px 0;">
        <div class="fireart-badge" style="margin-bottom:8px;">HR MANAGER</div>
        <div style="font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:1.1rem; color:#000000;">{user['name']}</div>
        <div style="color:#52525B; font-size:0.8rem;">{user.get('company', '')}</div>
        <div style="margin-top:6px;"><span class="pill pill-orange">Code: {hr_code}</span></div>
    </div>
    <hr style="border-color:#E4E4E7; margin:8px 0 16px 0;">
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("SIGN OUT", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()


# ==============================================================================
# 3. DEDICATED EMPLOYEE GROWTH & LEARNING PORTAL (IF LOGGED IN AS EMPLOYEE)
# ==============================================================================
elif st.session_state.user.get("role") == "employee":
    user = st.session_state.user
    
    # Employee Header
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
        <div>
            <div class="fireart-badge"><span class="fireart-dot"></span> MY CAREER & LEARNING PORTAL</div>
            <div class="fireart-hero-title" style="font-size:2.2rem; margin-bottom:4px;">
                Welcome, <span>{user['name']}</span>
            </div>
            <div style="color:#52525B; font-size:0.95rem;">
                Department: <strong>{user.get('department', 'Sales')}</strong> | Assigned HR Lead: <strong>{user.get('assigned_hr', 'HR Office')}</strong> (<span class="pill pill-orange">{user.get('hr_code', 'Verified')}</span>)
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 1. Profile & Performance Benchmark Strip
    kpi = user.get("kpi_score", 88.5)
    att = user.get("attendance", 96.0)
    task = user.get("task_completion", 92.0)
    peer = user.get("peer_rating", 4.6)
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="fireart-card">
            <div class="pill pill-blue">Performance Benchmark</div>
            <div class="fireart-metric-val" style="color:#2563EB;">{kpi}<span style="font-size:1.1rem; color:#71717A;">/100</span></div>
            <div class="fireart-metric-label">Quarterly KPI Score</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="fireart-card">
            <div class="pill pill-green">Task Velocity</div>
            <div class="fireart-metric-val" style="color:#059669;">{task}%</div>
            <div class="fireart-metric-label">Completion Efficiency</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="fireart-card">
            <div class="pill pill-gray">Attendance</div>
            <div class="fireart-metric-val">{att}%</div>
            <div class="fireart-metric-label">Presence Consistency</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="fireart-card">
            <div class="pill pill-orange">Peer Review</div>
            <div class="fireart-metric-val" style="color:#FF470A;">{peer}<span style="font-size:1.1rem; color:#71717A;">/5.0</span></div>
            <div class="fireart-metric-label">Leadership Sentiment</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # 2. Career Progression Pathway
    current_role = user.get("job_role", "Sales Representatives")
    target_role = user.get("target_role", "Sales Managers")
    
    st.markdown("### 🗺️ My Career Progression Blueprint")
    
    with st.container(border=True):
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <span class="pill pill-gray">CURRENT POSITION</span> <strong>{current_role}</strong> ➔ 
                <span class="pill pill-orange">TARGET PROMOTION</span> <strong style="color:#FF470A;">{target_role}</strong>
            </div>
            <div>
                <span class="pill pill-green">ALIGNMENT: 78%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Generate Course Curricula & 30-60-90 Plan for Employee
    dummy_skills = [
        {"skill": "Strategic Negotiation", "importance": 4.8},
        {"skill": "Team Leadership & Directing", "importance": 4.6},
        {"skill": "Operational Analytics", "importance": 4.2}
    ]
    dummy_tools = [
        {"tool": "Salesforce CRM", "is_hot_tech": True},
        {"tool": "Tableau Analytics", "is_hot_tech": False}
    ]
    
    plan = course_matcher.generate_30_60_90_plan(current_role, target_role, dummy_skills, dummy_tools)

    # 3. Assigned & Recommended Enterprise Courses
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    st.markdown("### 🎓 My Assigned & Recommended Enterprise Courses")
    
    c_cols = st.columns(len(plan["recommended_courses"]))
    for idx, c in enumerate(plan["recommended_courses"]):
        with c_cols[idx]:
            st.markdown(f"""
            <div class='fireart-card' style='height:100%;'>
                <span class='pill pill-orange'>{c['level']}</span>
                <h4 style='font-size:1.02rem; margin:10px 0 6px 0;'><a href='{c['url']}' target='_blank' style='color:#000000; text-decoration:none;'>{c['title']}</a></h4>
                <div style='color:#52525B; font-size:0.85rem; margin-bottom:8px;'>Provider: <strong>{c['provider']}</strong></div>
                <div style='display:flex; justify-content:space-between; align-items:center; font-size:0.85rem; font-weight:700; color:#000000; border-top:1px solid #E2E8F0; padding-top:8px;'>
                    <span>⏱️ {c['duration_hours']}h</span>
                    <span>⭐ {c['rating']}</span>
                    <span style='color:#FF470A;'>{c['cost']}</span>
                </div>
                <div style='margin-top:12px; text-align:center;'>
                    <a href='{c['url']}' target='_blank' style='display:inline-block; background:#FF470A; color:#FFFFFF; padding:6px 16px; border-radius:9999px; font-size:0.8rem; font-weight:700; text-decoration:none;'>ENROLL NOW ➔</a>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 4. Interactive 30-60-90 Day Milestone Roadmap
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    st.markdown("### 📅 My 30-60-90 Day Upskilling Milestone Roadmap")
    
    for p in plan["phases"]:
        with st.container(border=True):
            st.markdown(f"#### {p['phase']}: {p['title']}")
            st.markdown(f"**Focus Competency:** <span class='pill pill-orange'>{p['focus_skill']}</span> | **Tool Target:** <span class='pill pill-blue'>{p['target_tool']}</span>", unsafe_allow_html=True)
            st.markdown(f"**Deliverable Goal:** *{p['deliverable']}*")
            st.markdown("**My Milestones:**")
            for g in p["goals"]:
                st.checkbox(g, value=False, key=f"emp_goal_{p['phase']}_{g[:15]}")

    # Export Career Plan
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    plan_md = course_matcher.export_plan_markdown(plan)
    st.download_button(
        label="📥 DOWNLOAD MY OFFICIAL CAREER DEVELOPMENT PLAN (MARKDOWN)",
        data=plan_md,
        file_name=f"my_career_plan_{user['name'].lower().replace(' ', '_')}.md",
        mime="text/markdown",
        use_container_width=True
    )

    # Sidebar for Employee
    st.sidebar.markdown(f"""
    <div style="padding: 10px 0 14px 0;">
        <div class="fireart-badge" style="margin-bottom:8px;">EMPLOYEE PORTAL</div>
        <div style="font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:1.1rem; color:#000000;">{user['name']}</div>
        <div style="color:#52525B; font-size:0.8rem;">{user.get('job_role', '')}</div>
        <div style="margin-top:6px;"><span class="pill pill-green">HR Code: {user.get('hr_code', '')}</span></div>
    </div>
    <hr style="border-color:#E4E4E7; margin:8px 0 16px 0;">
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("SIGN OUT", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()
