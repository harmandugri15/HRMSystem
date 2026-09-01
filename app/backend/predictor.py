"""
Inference & Prediction Services for HRMS
Loads serialized model pipelines and provides real-time predictions, risk factors,
and actionable HR recommendations.
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import sys
from typing import Dict, Any, List, Tuple

# Path configuration
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from app.backend.config import *


class HRPredictor:
    def __init__(self):
        self._load_models()

    def _load_models(self):
        """Load serialized ML artifacts."""
        self.attrition_artifact = None
        self.performance_artifact = None
        self.training_artifact = None

        if ATTRITION_MODEL_PATH.exists():
            self.attrition_artifact = joblib.load(ATTRITION_MODEL_PATH)
        if PERFORMANCE_MODEL_PATH.exists():
            self.performance_artifact = joblib.load(PERFORMANCE_MODEL_PATH)
        if TRAINING_MODEL_PATH.exists():
            self.training_artifact = joblib.load(TRAINING_MODEL_PATH)

    def predict_attrition(self, emp_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predicts employee attrition probability, risk category, and key risk drivers.
        """
        if not self.attrition_artifact:
            raise FileNotFoundError("Attrition model artifact not found. Please train models first.")

        df = pd.DataFrame([emp_data])

        # Fill defaults if missing
        env = float(df["EnvironmentSatisfaction"].iloc[0]) if "EnvironmentSatisfaction" in df.columns else 3.0
        job = float(df["JobSatisfaction"].iloc[0]) if "JobSatisfaction" in df.columns else 3.0
        rel = float(df["RelationshipSatisfaction"].iloc[0]) if "RelationshipSatisfaction" in df.columns else 3.0
        wlb = float(df["WorkLifeBalance"].iloc[0]) if "WorkLifeBalance" in df.columns else 3.0
        
        income = float(df["MonthlyIncome"].iloc[0]) if "MonthlyIncome" in df.columns else 5000.0
        working_years = float(df["TotalWorkingYears"].iloc[0]) if "TotalWorkingYears" in df.columns else 5.0
        tenure = float(df["YearsAtCompany"].iloc[0]) if "YearsAtCompany" in df.columns else 3.0
        age = float(df["Age"].iloc[0]) if "Age" in df.columns else 30.0
        role_years = float(df["YearsInCurrentRole"].iloc[0]) if "YearsInCurrentRole" in df.columns else 2.0
        mgr_years = float(df["YearsWithCurrManager"].iloc[0]) if "YearsWithCurrManager" in df.columns else 2.0
        promo_years = float(df["YearsSinceLastPromotion"].iloc[0]) if "YearsSinceLastPromotion" in df.columns else 1.0

        df["TotalSatisfaction"] = env + job + rel + wlb
        df["IncomePerYearExperience"] = income / (working_years + 1.0)
        df["TenureToAgeRatio"] = tenure / (age if age > 0 else 1.0)
        df["RoleTenureRatio"] = role_years / (tenure + 1.0)
        df["ManagerTenureRatio"] = mgr_years / (tenure + 1.0)
        df["PromotionStagnation"] = promo_years / (tenure + 1.0)

        # Ensure correct column types
        num_cols = self.attrition_artifact["numerical_cols"]
        cat_cols = self.attrition_artifact["categorical_cols"]

        for col in num_cols:
            if col not in df.columns:
                df[col] = 0.0
            else:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        for col in cat_cols:
            if col not in df.columns:
                df[col] = "Unknown"
            else:
                df[col] = df[col].astype(str)

        required_cols = self.attrition_artifact["training_features"]
        X_input = df[required_cols]

        pipeline = self.attrition_artifact["pipeline"]
        prob = float(pipeline.predict_proba(X_input)[:, 1][0])
        opt_thresh = float(self.attrition_artifact.get("optimal_threshold", 0.33))

        # Risk Classification
        if prob >= 0.60:
            risk_level = "Critical"
            risk_color = "#E53E3E"
        elif prob >= opt_thresh:
            risk_level = "High"
            risk_color = "#DD6B20"
        elif prob >= 0.20:
            risk_level = "Moderate"
            risk_color = "#D69E2E"
        else:
            risk_level = "Low"
            risk_color = "#38A169"

        # Identify Specific Risk Drivers
        risk_drivers = []
        retention_actions = []

        if str(emp_data.get("OverTime", "")).strip().lower() == "yes":
            risk_drivers.append("Frequent Overtime (High burnout indicator)")
            retention_actions.append("Cap mandatory overtime hours and rebalance project workload.")

        if income < 4500:
            risk_drivers.append(f"Below-Average Monthly Income (${income:,.0f})")
            retention_actions.append("Review salary tier against industry benchmarks for retention adjustment.")

        if promo_years >= 4:
            risk_drivers.append(f"Promotion Stagnation ({promo_years:.0f} years since last promotion)")
            retention_actions.append("Initiate career progression discussions and evaluate leadership pathways.")

        if job <= 2:
            risk_drivers.append("Low Job Satisfaction score (<= 2/4)")
            retention_actions.append("Schedule confidential 1-on-1 feedback session with department lead.")

        dist = float(emp_data.get("DistanceFromHome", 5))
        if dist > 15:
            risk_drivers.append(f"High Commute Distance ({dist:.0f} miles)")
            retention_actions.append("Offer hybrid / remote work flexibility.")

        if not risk_drivers:
            risk_drivers.append("Steady employee sentiment; no immediate critical risk flags.")
            retention_actions.append("Continue periodic recognition and regular managerial check-ins.")

        return {
            "attrition_probability": round(prob * 100, 1),
            "risk_level": risk_level,
            "risk_color": risk_color,
            "is_at_risk": bool(prob >= opt_thresh),
            "risk_drivers": risk_drivers,
            "retention_actions": retention_actions
        }

    def predict_promotion(self, emp_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates promotion readiness, productivity score, and performance tier.
        """
        if not self.performance_artifact:
            raise FileNotFoundError("Performance model artifact not found. Please train models first.")

        df = pd.DataFrame([emp_data])

        kpi = float(emp_data.get("KPI Score", 75))
        task = float(emp_data.get("Task Completion (%)", 75))
        att = float(emp_data.get("Attendance (%)", 85))
        peer = float(emp_data.get("Peer Rating", 3.5))
        hours = float(emp_data.get("Work Hours Logged", 40))
        mgr = float(emp_data.get("Manager Feedback", 3.5))

        productivity_index = (kpi * 0.35) + (task * 0.35) + (att * 0.15) + ((peer * 20.0) * 0.15)
        work_efficiency = task / (hours + 1.0)
        mgr_ratio = (mgr / 5.0) * 100.0

        df["ProductivityIndex"] = productivity_index
        df["WorkHourEfficiency"] = work_efficiency
        df["ManagerScoreRatio"] = mgr_ratio

        num_cols = self.performance_artifact["numerical_cols"]
        cat_cols = self.performance_artifact["categorical_cols"]

        for col in num_cols:
            if col not in df.columns:
                df[col] = 0.0
            else:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        for col in cat_cols:
            if col not in df.columns:
                df[col] = "Unknown"
            else:
                df[col] = df[col].astype(str)

        required_cols = self.performance_artifact["training_features"]
        X_input = df[required_cols]

        pipeline = self.performance_artifact["pipeline"]
        prob = float(pipeline.predict_proba(X_input)[:, 1][0])
        is_eligible = bool(prob >= 0.5)

        if productivity_index >= 80:
            tier = "Exceeds Expectations"
            tier_color = "#38A169"
        elif productivity_index >= 65:
            tier = "Meets Expectations"
            tier_color = "#3182CE"
        else:
            tier = "Needs Improvement"
            tier_color = "#E53E3E"

        return {
            "promotion_probability": round(prob * 100, 1),
            "is_eligible": is_eligible,
            "productivity_index": round(productivity_index, 1),
            "performance_tier": tier,
            "tier_color": tier_color,
            "recommendation": (
                "Recommended for promotion and leadership consideration."
                if is_eligible else
                "Continue focusing on KPI goals and task completion consistency."
            )
        }

    def predict_training_outcome(self, train_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predicts training course completion/success probability.
        """
        if not self.training_artifact:
            raise FileNotFoundError("Training model artifact not found. Please train models first.")

        df = pd.DataFrame([train_data])
        
        cost = float(train_data.get("Training Cost", 500))
        days = float(train_data.get("Training Duration(Days)", 3))
        df["CostPerTrainingDay"] = cost / (days + 0.1)

        eng = float(train_data.get("Engagement Score", 3))
        sat = float(train_data.get("Satisfaction Score", 3))
        wlb = float(train_data.get("Work-Life Balance Score", 3))
        df["OverallSatisfactionIndex"] = (eng + sat + wlb) / 3.0

        num_cols = self.training_artifact["numerical_cols"]
        cat_cols = self.training_artifact["categorical_cols"]

        for col in num_cols:
            if col not in df.columns:
                df[col] = 0.0
            else:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        for col in cat_cols:
            if col not in df.columns:
                df[col] = "Unknown"
            else:
                df[col] = df[col].astype(str)

        required_cols = self.training_artifact["training_features"]
        X_input = df[required_cols]

        pipeline = self.training_artifact["pipeline"]
        prob = float(pipeline.predict_proba(X_input)[:, 1][0])

        return {
            "success_probability": round(prob * 100, 1),
            "predicted_outcome": "High Pass Likelihood" if prob >= 0.5 else "Needs Learning Support",
            "cost_per_day": round(cost / (days + 0.1), 2)
        }


# Singleton instance
predictor = HRPredictor()
