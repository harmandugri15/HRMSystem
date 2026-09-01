"""
Automated Test Suite for PULSE Enterprise AI Platform
Covers Data Pipeline, Machine Learning Inference, O*NET Taxonomy, OTP Auth,
Multi-Page Routes, Blank Initial Onboarding State, and Live Course Web Scraper.
"""

import unittest
import pandas as pd
import json
from pathlib import Path
from fastapi.testclient import TestClient

from app.backend.config import *
from app.backend.data_processor import (
    process_attrition_data,
    process_performance_data,
    process_training_engagement_data,
    process_onet_skills_taxonomy
)
from app.backend.predictor import predictor
from app.backend.recommender import recommender
from app.backend.auth import (
    register_hr_user,
    register_employee_user,
    generate_and_send_otp,
    verify_otp_code,
    complete_employee_onboarding,
    get_all_users
)
from app.backend.course_scraper import scrape_live_courses
from app.api.main import app

client = TestClient(app)


class TestHRMSSystem(unittest.TestCase):

    def test_01_attrition_pipeline(self):
        df = process_attrition_data()
        self.assertIn("Attrition_Numeric", df.columns)
        self.assertIn("TotalSatisfaction", df.columns)
        self.assertGreater(len(df), 1000)
        print("  [PASS] Data Pipeline: Attrition Processing")

    def test_02_performance_pipeline(self):
        df = process_performance_data()
        self.assertIn("Promotion_Numeric", df.columns)
        self.assertIn("ProductivityIndex", df.columns)
        self.assertGreater(len(df), 1000)
        print("  [PASS] Data Pipeline: Performance Processing")

    def test_03_training_pipeline(self):
        df = process_training_engagement_data()
        self.assertIn("TrainingSuccess", df.columns)
        self.assertIn("CostPerTrainingDay", df.columns)
        self.assertGreater(len(df), 1000)
        print("  [PASS] Data Pipeline: Training Processing")

    def test_04_onet_taxonomy_pipeline(self):
        df = process_onet_skills_taxonomy()
        self.assertIn("TopSkills", df.columns)
        self.assertIn("SoftwareTools", df.columns)
        self.assertGreater(len(df), 500)
        print("  [PASS] Data Pipeline: O*NET Taxonomy Processing")

    def test_05_ml_attrition_predictor(self):
        sample = {
            "Age": 35, "DailyRate": 800, "DistanceFromHome": 10, "Education": 3,
            "EnvironmentSatisfaction": 2, "HourlyRate": 60, "JobInvolvement": 2,
            "JobLevel": 2, "JobSatisfaction": 2, "MonthlyIncome": 3500,
            "MonthlyRate": 15000, "NumCompaniesWorked": 3, "PercentSalaryHike": 11,
            "PerformanceRating": 3, "RelationshipSatisfaction": 2, "StockOptionLevel": 0,
            "TotalWorkingYears": 8, "TrainingTimesLastYear": 2, "WorkLifeBalance": 2,
            "YearsAtCompany": 4, "YearsInCurrentRole": 2, "YearsSinceLastPromotion": 3,
            "YearsWithCurrManager": 1, "Department": "Sales", "EducationField": "Life Sciences",
            "Gender": "Male", "JobRole": "Sales Executive", "MaritalStatus": "Single", "OverTime": "Yes"
        }
        res = predictor.predict_attrition(sample)
        self.assertIn("attrition_probability", res)
        self.assertIn("risk_level", res)
        self.assertIn("risk_drivers", res)
        print("  [PASS] ML Models: Attrition Risk Predictor")

    def test_06_ml_promotion_predictor(self):
        sample = {
            "Department": "IT", "KPI Score": 92.0, "Task Completion (%)": 95.0,
            "Attendance (%)": 98.0, "Overtime (Hours)": 5.0, "Peer Rating": 4.8,
            "Manager Feedback": 4.5, "Projects Handled": 12, "Work Hours Logged": 42.0,
            "Training Hours": 20, "Age": 29, "Total Working Years": 6, "Years at Company": 4
        }
        res = predictor.predict_promotion(sample)
        self.assertIn("promotion_probability", res)
        self.assertIn("productivity_index", res)
        print("  [PASS] ML Models: Performance & Promotion Predictor")

    def test_07_ml_training_outcome_predictor(self):
        sample = {
            "DepartmentType": "Sales", "Training Program Name": "Sales Training",
            "Training Type": "External", "Training Duration(Days)": 5, "Training Cost": 1200,
            "Age": 32, "Engagement Score": 4, "Satisfaction Score": 4, "Work-Life Balance Score": 3
        }
        res = predictor.predict_training_outcome(sample)
        self.assertIn("success_probability", res)
        self.assertIn("cost_per_day", res)
        print("  [PASS] ML Models: Training Outcome Predictor")

    def test_08_recommender_search(self):
        roles = recommender.search_roles("Engineer", limit=5)
        self.assertGreater(len(roles), 0)
        print("  [PASS] Recommender: Role Search")

    def test_09_recommender_compare_roles(self):
        roles = recommender.search_roles("Sales", limit=2)
        if len(roles) >= 2:
            res = recommender.compare_roles(roles[0]["O*NET-SOC Code"], roles[1]["O*NET-SOC Code"])
            self.assertIn("skill_match_pct", res)
            self.assertIn("missing_skills", res)
            print("  [PASS] Recommender: Role Comparison & Gap Analysis")

    def test_10_otp_generation_and_verification(self):
        test_email = "verify.candidate@pulse.ai"
        ok, msg, otp = register_employee_user(
            name="Verify Candidate",
            email=test_email,
            password="VerifyPass123",
            hr_code="HR-7700-ACME"
        )
        self.assertTrue(ok or "already exists" in msg)
        
        v_ok, v_msg = verify_otp_code(test_email, otp or "123456")
        self.assertTrue(v_ok)
        
        users = get_all_users()
        self.assertTrue(users[test_email]["is_verified"])
        print("  [PASS] Auth: 6-Digit Email OTP Generation & Verification")

    def test_11_first_time_employee_onboarding(self):
        test_email = "verify.candidate@pulse.ai"
        onb_ok, onb_msg = complete_employee_onboarding(
            email=test_email,
            branch="London Tech Hub (UK)",
            department="Engineering & IT",
            job_role="Software Developers",
            target_role="Computer and Information Systems Managers",
            experience_years=5,
            skills=["Python Programming", "AWS Cloud Architecture", "Strategic Negotiation"],
            assigned_courses=[],
            roadmap={}
        )
        self.assertTrue(onb_ok)
        users = get_all_users()
        self.assertTrue(users[test_email]["is_onboarded"])
        self.assertEqual(len(users[test_email]["assigned_courses"]), 0)
        print("  [PASS] Employee Wizard: Initial Blank Onboarding State (Awaiting HR Assignment)")

    def test_12_all_multipage_routes_status_200(self):
        routes = [
            "/",
            "/login",
            "/register-hr",
            "/register-employee",
            "/verify-email",
            "/employee/onboarding",
            "/employee/dashboard",
            "/hr/dashboard",
            "/hr/attrition",
            "/hr/performance",
            "/hr/training",
            "/hr/skills",
            "/hr/roster"
        ]
        for r in routes:
            res = client.get(r)
            self.assertEqual(res.status_code, 200, f"Route {r} failed with status {res.status_code}")
            res_head = client.head(r)
            self.assertEqual(res_head.status_code, 200, f"Route {r} HEAD failed with status {res_head.status_code}")
        print(f"  [PASS] Multi-Page Architecture: All {len(routes)} HTML Routes Serving 200 OK (GET & HEAD)")

    def test_13_live_course_web_scraper(self):
        courses = scrape_live_courses("Cloud Architecture", platform="Coursera", limit=4)
        self.assertGreater(len(courses), 0)
        self.assertIn("url", courses[0])
        self.assertIn("title", courses[0])
        self.assertIn("provider", courses[0])
        print("  [PASS] Live Web Scraper: Scrapes Live Online Courses from Web Platforms")


if __name__ == "__main__":
    print("=" * 60)
    print("[*] Running Production Multi-Page Enterprise Test Suite")
    print("=" * 60)
    unittest.main(verbosity=0)
