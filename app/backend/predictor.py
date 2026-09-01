"""
Inference & Prediction Services for HRMS
Loads serialized model pipelines and provides real-time predictions, risk factors,
and actionable HR recommendations with automatic on-the-fly retraining fallback.
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
        """Load serialized ML artifacts with automatic self-healing retraining."""
        self.attrition_artifact = None
        self.performance_artifact = None
        self.training_artifact = None

        needs_retrain = False
        if not (ATTRITION_MODEL_PATH.exists() and PERFORMANCE_MODEL_PATH.exists() and TRAINING_MODEL_PATH.exists()):
            needs_retrain = True
        else:
            try:
                self.attrition_artifact = joblib.load(ATTRITION_MODEL_PATH)
                self.performance_artifact = joblib.load(PERFORMANCE_MODEL_PATH)
                self.training_artifact = joblib.load(TRAINING_MODEL_PATH)
            except Exception as e:
                print(f"[!] Warning loading model pickle: {e}. Initiating auto-retraining...")
                needs_retrain = True

        if needs_retrain:
            try:
                from app.backend.models_trainer import run_all_trainers
                run_all_trainers()
                self.attrition_artifact = joblib.load(ATTRITION_MODEL_PATH)
                self.performance_artifact = joblib.load(PERFORMANCE_MODEL_PATH)
                self.training_artifact = joblib.load(TRAINING_MODEL_PATH)
                print("[+] Auto-retraining completed successfully.")
            except Exception as e2:
                print(f"[!] Fatal error during auto-retraining: {e2}")

    def predict_attrition(self, emp_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predicts employee attrition probability, risk category, and key risk drivers.
        """
        if not self.attrition_artifact:
            self._load_models()
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
        df["PromotionWaitRatio"] = promo_years / (role_years + 1.0)
        df["ManagerTenureRatio"] = mgr_years / (tenure + 1.0)
        df["TenureRatio"] = tenure / (age - 17.0) if age > 18 else 0.1

        cat_cols = self.attrition_artifact.get("categorical_cols", [])
        num_cols = self.attrition_artifact.get("numerical_cols", [])

        for col in cat_cols:
            if col not in df.columns:
                df[col] = "Unknown"
            else:
                df[col] = df[col].astype(str)

        for col in num_cols:
            if col not in df.columns:
                df[col] = 0.0
            else:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

        train_features = self.attrition_artifact["training_features"]
        df = df[train_features]

        pipeline = self.attrition_artifact["pipeline"]
        prob = float(pipeline.predict_proba(df)[0, 1])

        # Calibrated risk tiers
        if prob >= 0.50:
            risk_level = "High"
            risk_color = "#DC2626"
        elif prob >= 0.25:
            risk_level = "Medium"
            risk_color = "#FF470A"
        else:
            risk_level = "Low"
            risk_color = "#059669"

        # Risk drivers diagnosis
        drivers = self._diagnose_risk_drivers(emp_data, prob)

        return {
            "attrition_probability": round(prob * 100, 1),
            "risk_level": risk_level,
            "risk_color": risk_color,
            "risk_drivers": drivers,
            "optimal_threshold": self.attrition_artifact.get("optimal_threshold", 0.5)
        }

    def _diagnose_risk_drivers(self, emp_data: Dict[str, Any], prob: float) -> List[str]:
        """Isolates specific organizational burnout catalysts."""
        drivers = []
        if emp_data.get("OverTime") == "Yes":
            drivers.append("Excessive Mandatory Overtime Burden")
        if emp_data.get("MonthlyIncome", 6000) < 4000:
            drivers.append("Below-Market Compensation Level for Role")
        if emp_data.get("YearsSinceLastPromotion", 0) >= 3:
            drivers.append("Compressed Career Trajectory (>3 Years Without Promotion)")
        if emp_data.get("JobSatisfaction", 3) <= 2:
            drivers.append("Low Job Fulfillment & Role Stagnation Sentiment")
        if emp_data.get("WorkLifeBalance", 3) <= 2:
            drivers.append("Poor Work-Life Balance & After-Hours Fatigue")
        if emp_data.get("DistanceFromHome", 5) > 15:
            drivers.append("Long Daily Commute Distance (>15 Miles)")
        if emp_data.get("YearsWithCurrManager", 3) <= 1 and emp_data.get("YearsAtCompany", 3) > 3:
            drivers.append("Recent Manager Transition / Disconnect")

        if not drivers:
            drivers.append("Balanced organizational stability metrics.")

        return drivers[:3]

    def predict_promotion(self, emp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates employee promotion readiness and 360 productivity index."""
        if not self.performance_artifact:
            self._load_models()
        if not self.performance_artifact:
            raise FileNotFoundError("Performance model artifact not found.")

        df = pd.DataFrame([emp_data])

        kpi = float(df["KPI Score"].iloc[0]) if "KPI Score" in df.columns else 80.0
        task = float(df["Task Completion (%)"].iloc[0]) if "Task Completion (%)" in df.columns else 85.0
        att = float(df["Attendance (%)"].iloc[0]) if "Attendance (%)" in df.columns else 90.0
        peer = float(df["Peer Rating"].iloc[0]) if "Peer Rating" in df.columns else 4.0
        mgr = float(df["Manager Feedback"].iloc[0]) if "Manager Feedback" in df.columns else 4.0
        hours = float(df["Work Hours Logged"].iloc[0]) if "Work Hours Logged" in df.columns else 40.0

        productivity = (kpi * 0.35) + (task * 0.25) + (att * 0.15) + (peer * 20 * 0.15) + (mgr * 20 * 0.10)
        df["ProductivityIndex"] = productivity
        df["WorkHourEfficiency"] = (kpi * task) / (hours + 1.0)
        df["ManagerScoreRatio"] = mgr / (peer + 0.1)

        cat_cols = self.performance_artifact.get("categorical_cols", [])
        num_cols = self.performance_artifact.get("numerical_cols", [])

        for col in cat_cols:
            if col not in df.columns:
                df[col] = "Unknown"
            else:
                df[col] = df[col].astype(str)

        for col in num_cols:
            if col not in df.columns:
                df[col] = 0.0
            else:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

        train_features = self.performance_artifact["training_features"]
        df = df[train_features]

        pipeline = self.performance_artifact["pipeline"]
        prob = float(pipeline.predict_proba(df)[0, 1])

        is_ready = prob >= 0.50
        tier = "Ready for Immediate Promotion" if is_ready else ("On Accelerated Track" if prob >= 0.35 else "Development Pathway")

        return {
            "promotion_probability": round(prob * 100, 1),
            "promotion_ready": is_ready,
            "promotion_tier": tier,
            "productivity_index": round(productivity, 1)
        }

    def predict_training_outcome(self, training_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predicts training completion success probability and unit costs."""
        if not self.training_artifact:
            self._load_models()
        if not self.training_artifact:
            raise FileNotFoundError("Training model artifact not found.")

        df = pd.DataFrame([training_data])

        cost = float(df["Training Cost"].iloc[0]) if "Training Cost" in df.columns else 500.0
        days = float(df["Training Duration(Days)"].iloc[0]) if "Training Duration(Days)" in df.columns else 3.0
        eng = float(df["Engagement Score"].iloc[0]) if "Engagement Score" in df.columns else 4.0
        sat = float(df["Satisfaction Score"].iloc[0]) if "Satisfaction Score" in df.columns else 4.0
        wlb = float(df["Work-Life Balance Score"].iloc[0]) if "Work-Life Balance Score" in df.columns else 3.0

        df["CostPerTrainingDay"] = cost / (days + 0.001)
        df["OverallSatisfactionIndex"] = (eng + sat + wlb) / 3.0

        cat_cols = self.training_artifact.get("categorical_cols", [])
        num_cols = self.training_artifact.get("numerical_cols", [])

        for col in cat_cols:
            if col not in df.columns:
                df[col] = "Unknown"
            else:
                df[col] = df[col].astype(str)

        for col in num_cols:
            if col not in df.columns:
                df[col] = 0.0
            else:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

        train_features = self.training_artifact["training_features"]
        df = df[train_features]

        pipeline = self.training_artifact["pipeline"]
        prob = float(pipeline.predict_proba(df)[0, 1])

        return {
            "success_probability": round(prob * 100, 1),
            "is_successful": prob >= 0.50,
            "cost_per_day": round(cost / max(days, 1), 2)
        }


predictor = HRPredictor()
