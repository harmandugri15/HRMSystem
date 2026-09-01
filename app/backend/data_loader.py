"""
Data Access & Aggregation Utilities for HRMS Dashboard
Provides cached, ready-to-render data structures for the Streamlit UI.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
from typing import Dict, Any

# Path configuration
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from app.backend.config import *


def get_attrition_df() -> pd.DataFrame:
    """Load processed attrition dataset."""
    path = DATA_PROCESSED_DIR / "processed_attrition.csv"
    if not path.exists():
        from app.backend.data_processor import process_attrition_data
        return process_attrition_data()
    return pd.read_csv(path)


def get_performance_df() -> pd.DataFrame:
    """Load processed performance dataset."""
    path = DATA_PROCESSED_DIR / "processed_performance.csv"
    if not path.exists():
        from app.backend.data_processor import process_performance_data
        return process_performance_data()
    return pd.read_csv(path)


def get_training_df() -> pd.DataFrame:
    """Load processed training & engagement dataset."""
    path = DATA_PROCESSED_DIR / "processed_training_engagement.csv"
    if not path.exists():
        from app.backend.data_processor import process_training_engagement_data
        return process_training_engagement_data()
    return pd.read_csv(path)


def get_executive_kpis() -> Dict[str, Any]:
    """Calculate executive high-level metrics across datasets."""
    df_att = get_attrition_df()
    df_perf = get_performance_df()
    df_train = get_training_df()

    total_headcount = len(df_att)
    attrition_rate = (df_att["Attrition_Numeric"].mean() * 100).round(1)
    retention_rate = round(100.0 - attrition_rate, 1)
    avg_salary = int(df_att["MonthlyIncome"].mean())
    avg_tenure = round(float(df_att["YearsAtCompany"].mean()), 1)

    total_evaluated = len(df_perf)
    promotion_rate = (df_perf["Promotion_Numeric"].mean() * 100).round(1)
    avg_productivity = round(float(df_perf["ProductivityIndex"].mean()), 1)

    total_training_spend = int(df_train["Training Cost"].sum())
    training_success_rate = (df_train["TrainingSuccess"].mean() * 100).round(1)

    return {
        "total_headcount": total_headcount,
        "retention_rate": retention_rate,
        "attrition_rate": attrition_rate,
        "avg_salary": avg_salary,
        "avg_tenure": avg_tenure,
        "total_evaluated": total_evaluated,
        "promotion_rate": promotion_rate,
        "avg_productivity": avg_productivity,
        "total_training_spend": total_training_spend,
        "training_success_rate": training_success_rate
    }
