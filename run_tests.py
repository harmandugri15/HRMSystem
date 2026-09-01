"""
Automated Test Suite for Multi-Page Enterprise HRMS Platform
Verifies Data Pipeline, ML Models, O*NET Recommender, Real OTP Auth, Employee Onboarding Wizard,
and all 13 Multi-Page HTML Web Routes.
"""

import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from app.api.main import app
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
    verify_otp_code,
    complete_employee_onboarding,
    authenticate_user,
    validate_hr_code,
    get_employees_for_hr,
    get_all_users
)
from app.backend.course_matcher import course_matcher

client = TestClient(app)


class TestHRMSSystem(unittest.TestCase):

    def test_01_data_pipeline_attrition(self):
        df = process_attrition_data()
        self.assertFalse(df.empty)
        self.assertIn("Attrition_Numeric", df.columns)
        self.assertIn("TotalSatisfaction", df.columns)
        print("  [PASS] Data Pipeline: Attrition Processing")

    def test_02_data_pipeline_performance(self):
        df = process_performance_data()
        self.assertFalse(df.empty)
        self.assertIn("ProductivityIndex", df.columns)
        self.assertIn("Promotion_Numeric", df.columns)
        print("  [PASS] Data Pipeline: Performance Processing")

    def test_03_data_pipeline_training(self):
        df = process_training_engagement_data()
        self.assertFalse(df.empty)
        self.assertIn("TrainingSuccess", df.columns)
        self.assertIn("CostPerTrainingDay", df.columns)
        print("  [PASS] Data Pipeline: Training Processing")

    def test_04_data_pipeline_taxonomy(self):
        df = process_onet_skills_taxonomy()
        self.assertFalse(df.empty)
        self.assertIn("O*NET-SOC Code", df.columns)
        self.assertIn("TopSkills", df.columns)
        print("  [PASS] Data Pipeline: O*NET Taxonomy Processing")

    def test_05_ml_attrition_predictor(self):
        sample = {
            "Age": 30, "Department": "Sales", "JobRole": "Sales Executive",
            "MonthlyIncome": 4500, "BusinessTravel": "Travel_Rarely",
            "OverTime": "Yes", "DistanceFromHome": 10, "TotalWorkingYears": 6,
            "YearsAtCompany": 3, "YearsInCurrentRole": 2, "YearsSinceLastPromotion": 1,
            "YearsWithCurrManager": 2, "JobSatisfaction": 2, "EnvironmentSatisfaction": 3,
            "RelationshipSatisfaction": 3, "WorkLifeBalance": 2, "MaritalStatus": "Single"
        }
        res = predictor.predict_attrition(sample)
        self.assertIn("attrition_probability", res)
        self.assertIn("risk_level", res)
        self.assertIn("risk_drivers", res)
        print("  [PASS] ML Models: Attrition Risk Predictor")

    def test_06_ml_promotion_predictor(self):
        sample = {
            "Department": "IT", "Job Role": "Software Engineer", "KPI Score": 88,
            "Task Completion (%)": 92, "Attendance (%)": 96, "Peer Rating": 4.5,
            "Work Hours Logged": 42, "Manager Feedback": 4.5, "Training Hours": 25
        }
        res = predictor.predict_promotion(sample)
        self.assertIn("promotion_probability", res)
        self.assertIn("productivity_index", res)
        print("  [PASS] ML Models: Performance & Promotion Predictor")

    def test_07_ml_training_predictor(self):
        sample = {
            "DepartmentType": "Technical", "Training Program Name": "Cloud Architecture",
            "Training Type": "External", "Training Duration(Days)": 3, "Training Cost": 600,
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
        # Register Employee
        ok, msg, otp = register_employee_user(
            name="Verify Candidate",
            email=test_email,
            password="VerifyPass123",
            hr_code="HR-7700-ACME"
        )
        self.assertTrue(ok or "already exists" in msg)
        
        # Verify with OTP
        v_ok, v_msg = verify_otp_code(test_email, otp or "123456")
        self.assertTrue(v_ok)
        
        # Verify account is marked verified
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
            assigned_courses=[{"title": "AWS Certified Solutions Architect", "url": "https://aws.amazon.com"}]
        )
        self.assertTrue(onb_ok)
        users = get_all_users()
        self.assertTrue(users[test_email]["is_onboarded"])
        self.assertEqual(users[test_email]["branch"], "London Tech Hub (UK)")
        print("  [PASS] Employee Wizard: Branch & First-Time Profile Onboarding")

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
        print(f"  [PASS] Multi-Page Architecture: All {len(routes)} HTML Routes Serving 200 OK")


if __name__ == "__main__":
    print("=" * 60)
    print("[*] Running Production Multi-Page Enterprise Test Suite")
    print("=" * 60)
    unittest.main(verbosity=0)
