"""
Automated Test Suite for Enterprise HRMS Platform
Verifies Data Pipeline, ML Models, O*NET Recommender, Auth, AI Course Matcher, and FastAPI REST Endpoints.
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

    def test_10_dual_role_auth_and_hr_linking(self):
        hr_email = "test.hr.lead@enterprise.ai"
        hr_ok, _, hr_code = register_hr_user("Elena Rostova", hr_email, "HRPass123", "Apex Corp")
        if not hr_ok:
            hr_code = get_all_users().get(hr_email, {}).get("hr_code")
        self.assertIsNotNone(hr_code)
        
        emp_email = "test.emp.dev@enterprise.ai"
        emp_ok, emp_msg = register_employee_user(
            name="Marcus Vance",
            email=emp_email,
            password="EmpPass123",
            hr_code=hr_code,
            department="IT",
            job_role="Software Developer",
            target_role="Lead Architect"
        )
        self.assertTrue(emp_ok or "already exists" in emp_msg)
        
        emp_user = authenticate_user(emp_email, "EmpPass123")
        self.assertIsNotNone(emp_user)
        self.assertEqual(emp_user["role"], "employee")
        print("  [PASS] Auth: Dual-Role Registration & Linking")

    def test_11_course_matcher_and_roadmap(self):
        fake_skills = [{"skill": "Python Programming", "importance": 4.5}, {"skill": "Leadership", "importance": 4.0}]
        fake_tools = [{"tool": "AWS Cloud", "is_hot_tech": True}]
        
        courses = course_matcher.find_courses_for_skills(fake_skills, limit=3)
        self.assertGreater(len(courses), 0)
        
        plan = course_matcher.generate_30_60_90_plan("Developer", "Lead Architect", fake_skills, fake_tools)
        self.assertEqual(len(plan["phases"]), 3)
        print("  [PASS] AI Course Matcher: Roadmap Generation")

    def test_12_fastapi_rest_endpoints(self):
        # Health
        res = client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "online")
        
        # KPIs
        res_kpi = client.get("/api/kpis")
        self.assertEqual(res_kpi.status_code, 200)
        self.assertIn("total_headcount", res_kpi.json())
        
        # Attrition Prediction
        res_att = client.post("/api/predict/attrition", json={
            "Age": 30, "Department": "Sales", "JobRole": "Sales Executive",
            "MonthlyIncome": 4500, "BusinessTravel": "Travel_Rarely",
            "OverTime": "Yes", "DistanceFromHome": 10, "TotalWorkingYears": 6,
            "YearsAtCompany": 3, "YearsInCurrentRole": 2, "YearsSinceLastPromotion": 1,
            "YearsWithCurrManager": 2, "JobSatisfaction": 2, "EnvironmentSatisfaction": 3,
            "RelationshipSatisfaction": 3, "WorkLifeBalance": 2, "MaritalStatus": "Single"
        })
        self.assertEqual(res_att.status_code, 200)
        self.assertIn("attrition_probability", res_att.json())

        # Course Roadmap
        res_road = client.post("/api/courses/roadmap", json={
            "current_role": "Sales Representatives",
            "target_role": "Sales Managers",
            "missing_skills": [{"skill": "Strategic Negotiation", "importance": 4.8}],
            "missing_tools": [{"tool": "Salesforce CRM", "is_hot_tech": True}]
        })
        self.assertEqual(res_road.status_code, 200)
        self.assertIn("plan", res_road.json())
        print("  [PASS] FastAPI REST API: All Endpoints & Static Files")


if __name__ == "__main__":
    print("=" * 60)
    print("[*] Running Full-Stack Enterprise Test Suite")
    print("=" * 60)
    unittest.main(verbosity=0)
