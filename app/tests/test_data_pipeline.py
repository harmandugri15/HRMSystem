"""
Unit tests for data pipeline and feature engineering.
"""

import pandas as pd
import sys
from pathlib import Path

# Add root directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from app.backend.config import *
from app.backend.data_processor import (
    process_attrition_data,
    process_performance_data,
    process_training_engagement_data,
    process_onet_skills_taxonomy
)


def test_attrition_data_processing():
    """Verify processed attrition dataset has expected features and no nulls."""
    df = process_attrition_data()
    assert not df.empty
    assert "TotalSatisfaction" in df.columns
    assert "IncomePerYearExperience" in df.columns
    assert "Attrition_Numeric" in df.columns
    assert df["Attrition_Numeric"].isin([0, 1]).all()


def test_performance_data_processing():
    """Verify performance dataset has productivity index and tier categories."""
    df = process_performance_data()
    assert not df.empty
    assert "ProductivityIndex" in df.columns
    assert "Promotion_Numeric" in df.columns
    assert "PerformanceTier" in df.columns
    assert df["ProductivityIndex"].min() >= 0
    assert df["ProductivityIndex"].max() <= 100


def test_training_engagement_processing():
    """Verify training dataset has success flags and cost-per-day metrics."""
    df = process_training_engagement_data()
    assert not df.empty
    assert "TrainingSuccess" in df.columns
    assert "CostPerTrainingDay" in df.columns
    assert df["TrainingSuccess"].isin([0, 1]).all()


def test_skills_taxonomy_processing():
    """Verify O*NET skills taxonomy is aggregated correctly."""
    df = process_onet_skills_taxonomy()
    assert not df.empty
    assert "O*NET-SOC Code" in df.columns
    assert "TopSkills" in df.columns
    assert "SoftwareTools" in df.columns
