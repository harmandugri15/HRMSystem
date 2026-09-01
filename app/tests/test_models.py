"""
Unit tests for Machine Learning Predictors & Risk Engines.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from app.backend.predictor import predictor


def test_attrition_prediction_structure():
    """Verify attrition prediction returns valid probabilities and categories."""
    emp_payload = {
        "Age": 28,
        "Department": "Sales",
        "JobRole": "Sales Representative",
        "MonthlyIncome": 2500,
        "BusinessTravel": "Travel_Frequently",
        "OverTime": "Yes",
        "DistanceFromHome": 25,
        "TotalWorkingYears": 3,
        "YearsAtCompany": 1,
        "YearsInCurrentRole": 1,
        "YearsSinceLastPromotion": 0,
        "YearsWithCurrManager": 1,
        "JobSatisfaction": 1,
        "EnvironmentSatisfaction": 1,
        "RelationshipSatisfaction": 2,
        "WorkLifeBalance": 1,
        "MaritalStatus": "Single"
    }
    res = predictor.predict_attrition(emp_payload)
    assert "attrition_probability" in res
    assert 0.0 <= res["attrition_probability"] <= 100.0
    assert res["risk_level"] in ["Low", "Moderate", "High", "Critical"]
    assert isinstance(res["risk_drivers"], list)
    assert len(res["risk_drivers"]) > 0


def test_promotion_prediction():
    """Verify promotion evaluation outputs valid metrics."""
    perf_payload = {
        "Department": "IT",
        "Job Role": "Software Engineer",
        "KPI Score": 95.0,
        "Attendance (%)": 98.0,
        "Peer Rating": 4.8,
        "Task Completion (%)": 94.0,
        "Work Hours Logged": 42,
        "Manager Feedback": 4.8,
        "Training Hours": 30
    }
    res = predictor.predict_promotion(perf_payload)
    assert "promotion_probability" in res
    assert "productivity_index" in res
    assert res["productivity_index"] >= 80
    assert res["performance_tier"] == "Exceeds Expectations"


def test_training_outcome_prediction():
    """Verify training outcome prediction."""
    train_payload = {
        "DepartmentType": "Sales",
        "Training Program Name": "Customer Service",
        "Training Type": "Internal",
        "Training Duration(Days)": 3,
        "Training Cost": 500,
        "Age": 30,
        "Engagement Score": 4,
        "Satisfaction Score": 4,
        "Work-Life Balance Score": 4
    }
    res = predictor.predict_training_outcome(train_payload)
    assert "success_probability" in res
    assert 0.0 <= res["success_probability"] <= 100.0
