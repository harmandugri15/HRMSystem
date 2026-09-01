"""
O*NET Skills Taxonomy, AI Course Matcher & 30-60-90 Day Upskilling Roadmap — Fireart Studio Light Edition (Zero Emojis)
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
from app.backend.recommender import recommender
from app.backend.course_matcher import course_matcher

st.set_page_config(page_title="Skills & Pathways // PULSE", layout="wide")
st.markdown(FIREART_CSS, unsafe_allow_html=True)

st.markdown("""
<div class="fireart-badge"><span class="fireart-dot"></span> COMPETENCY ARCHITECTURE & L&D MARKETPLACE</div>
<div class="fireart-hero-title">O*NET Career Pathways & <span>AI Course Matcher</span></div>
<div class="fireart-hero-subtitle">Bridge organizational capability gaps, map career progression pathways, and automatically generate 30-60-90 day upskilling roadmaps with verified enterprise courses.</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Cross-Role Gap Analyzer & 30-60-90 Roadmap", "O*NET Occupational Framework (1,016 Roles)"])

with tab1:
    st.markdown("### 1. Compare Current Role vs. Target Promotion Role")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.markdown("#### Current Employee Role")
            q_curr = st.text_input("Search Current Role", value="Sales Representatives", key="curr_search")
            curr_roles = recommender.search_roles(q_curr, limit=10)
            curr_options = {f"{r['Title']} ({r['O*NET-SOC Code']})": r["O*NET-SOC Code"] for r in curr_roles}
            
            if curr_options:
                sel_curr_label = st.selectbox("Select Current Profile", options=list(curr_options.keys()), key="curr_select")
                sel_curr_soc = curr_options[sel_curr_label]
            else:
                st.warning("No roles found.")
                sel_curr_soc = None

    with col2:
        with st.container(border=True):
            st.markdown("#### Target Aspiration Role")
            q_tgt = st.text_input("Search Target Role", value="Sales Managers", key="tgt_search")
            tgt_roles = recommender.search_roles(q_tgt, limit=10)
            tgt_options = {f"{r['Title']} ({r['O*NET-SOC Code']})": r["O*NET-SOC Code"] for r in tgt_roles}
            
            if tgt_options:
                sel_tgt_label = st.selectbox("Select Target Profile", options=list(tgt_options.keys()), key="tgt_select")
                sel_tgt_soc = tgt_options[sel_tgt_label]
            else:
                st.warning("No roles found.")
                sel_tgt_soc = None

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    if sel_curr_soc and sel_tgt_soc:
        if st.button("GENERATE SKILL GAP & 30-60-90 DAY ROADMAP", type="primary"):
            comp = recommender.compare_roles(sel_curr_soc, sel_tgt_soc)
            
            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
            st.markdown(f"### Pathway Blueprint: **{comp['current_title']}** ➔ **{comp['target_title']}**")
            
            m1, m2 = st.columns(2)
            with m1:
                st.markdown(f"""
                <div class='fireart-card'>
                    <div class='pill pill-blue'>Competency Overlap</div>
                    <div class='fireart-metric-val' style='color:#2563EB;'>{comp['skill_match_pct']}%</div>
                    <div class='fireart-metric-label'>Baseline Alignment</div>
                </div>
                """, unsafe_allow_html=True)
            with m2:
                diff_color = "#059669" if comp["skill_match_pct"] >= 70 else "#FF470A"
                st.markdown(f"""
                <div class='fireart-card'>
                    <div class='pill pill-orange'>Transition Feasibility</div>
                    <div class='fireart-metric-val' style='color:{diff_color}; font-size:1.6rem;'>{comp['transition_difficulty']}</div>
                    <div class='fireart-metric-label'>Upskilling Runway</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class='fireart-card' style='background:rgba(255, 71, 10, 0.04); border-color:rgba(255, 71, 10, 0.2);'>
                <h4 style='color:#FF470A; margin:0 0 8px 0;'>Target Role Summary</h4>
                <p style='color:#000000; margin:0; line-height:1.6; font-weight:500;'>{comp['target_description']}</p>
            </div>
            """, unsafe_allow_html=True)

            g_col1, g_col2 = st.columns(2)
            
            with g_col1:
                with st.container(border=True):
                    st.markdown("#### Priority Competencies to Develop")
                    if comp["missing_skills"]:
                        for s in comp["missing_skills"]:
                            st.markdown(f"""
                            <div style='display:flex; justify-content:space-between; align-items:center; padding:8px 0; border-bottom:1px solid #E2E8F0;'>
                                <span style='color:#000000; font-weight:700;'>{s['skill']}</span>
                                <span class='pill pill-orange'>Importance: {s['importance']}/5.0</span>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.success("High competency alignment. No critical skill gaps detected.")

            with g_col2:
                with st.container(border=True):
                    st.markdown("#### Required Software and Hot Technologies")
                    if comp["missing_software"]:
                        for sw in comp["missing_software"]:
                            if sw["is_hot_tech"]:
                                badge = "<span class='pill pill-orange'>HOT TECH</span>"
                            else:
                                badge = "<span class='pill pill-gray'>TOOL</span>"
                            st.markdown(f"""
                            <div style='display:flex; justify-content:space-between; align-items:center; padding:8px 0; border-bottom:1px solid #E2E8F0;'>
                                <span style='color:#000000; font-weight:600;'>{sw['tool']}</span>
                                {badge}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.success("Tech stack requirements match current domain expertise.")

            # NEW FEATURE: AI Course Recommendations & 30-60-90 Day Roadmap
            st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
            st.markdown("### 2. Verified Enterprise Course Curricula (Coursera, edX, LinkedIn Learning, Udemy)")
            
            plan = course_matcher.generate_30_60_90_plan(
                comp["current_title"],
                comp["target_title"],
                comp["missing_skills"],
                comp["missing_software"]
            )
            
            # Course Cards Grid
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
                            <a href='{c['url']}' target='_blank' style='display:inline-block; background:#FF470A; color:#FFFFFF; padding:5px 14px; border-radius:9999px; font-size:0.78rem; font-weight:700; text-decoration:none;'>ENROLL NOW ➔</a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
            st.markdown("### 3. Personalized 30-60-90 Day Upskilling Milestone Roadmap")
            
            for p in plan["phases"]:
                with st.container(border=True):
                    st.markdown(f"#### {p['phase']}: {p['title']}")
                    st.markdown(f"**Focus Skill:** <span class='pill pill-orange'>{p['focus_skill']}</span> | **Tool Target:** <span class='pill pill-blue'>{p['target_tool']}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Key Deliverable:** *{p['deliverable']}*")
                    st.markdown("**Action Milestones:**")
                    for g in p["goals"]:
                        st.checkbox(g, value=False, key=f"goal_{p['phase']}_{g[:15]}")

            # Export Career Plan Button
            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
            plan_md = course_matcher.export_plan_markdown(plan)
            st.download_button(
                label="📥 DOWNLOAD EMPLOYEE CAREER ACTION PLAN (MARKDOWN)",
                data=plan_md,
                file_name=f"career_plan_{comp['current_title'].lower().replace(' ', '_')}_to_{comp['target_title'].lower().replace(' ', '_')}.md",
                mime="text/markdown",
                use_container_width=True
            )

with tab2:
    st.markdown("### Browse O*NET Occupational Framework (1,016 Standard Roles)")
    
    with st.container(border=True):
        search_term = st.text_input("Filter Catalog by Keyword (e.g. Engineer, Manager, Data, Analyst, Director)", value="Engineer")
        results = recommender.search_roles(search_term, limit=20)
    
    st.markdown(f"Displaying **{len(results)}** occupational profiles:")
    for r in results:
        with st.expander(f"{r['Title']} (Code: {r['O*NET-SOC Code']})"):
            details = recommender.get_role_details(r["O*NET-SOC Code"])
            if details:
                st.markdown(f"<p style='color:#000000; line-height:1.6; font-weight:500;'>{details['description']}</p>", unsafe_allow_html=True)
                
                c_a, c_b = st.columns(2)
                with c_a:
                    st.markdown("**Core Skills**:")
                    for sk in details["skills"][:6]:
                        st.markdown(f"- **{sk['skill']}** *(Importance: {sk['importance']}/5.0)*")
                with c_b:
                    st.markdown("**Required Tools / Technologies**:")
                    for sw in details["software"][:6]:
                        tag = "[HOT TECH]" if sw["is_hot_tech"] else "[TOOL]"
                        st.markdown(f"- {tag} {sw['tool']}")
