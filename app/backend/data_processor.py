"""
Data Processing & Feature Engineering Pipeline for HRMS
Loads raw datasets, performs data cleaning, engineers domain-specific features,
and exports clean datasets to data/processed/.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Ensure config paths are accessible
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from app.backend.config import *


def process_attrition_data() -> pd.DataFrame:
    """Clean and engineer features for employee attrition dataset."""
    df = pd.read_csv(ATTRITION_DATA_PATH)
    
    # Drop useless constant columns
    cols_to_drop = ['EmployeeCount', 'Over18', 'StandardHours']
    df = df.drop(columns=[col for col in cols_to_drop if col in df.columns])
    
    # Target encoding
    df['Attrition_Numeric'] = df['Attrition'].map({'Yes': 1, 'No': 0})
    df['OverTime_Numeric'] = df['OverTime'].map({'Yes': 1, 'No': 0})
    
    # Domain Feature Engineering
    df['TotalSatisfaction'] = (
        df['EnvironmentSatisfaction'] +
        df['JobSatisfaction'] +
        df['RelationshipSatisfaction'] +
        df['WorkLifeBalance']
    )
    df['IncomePerYearExperience'] = df['MonthlyIncome'] / (df['TotalWorkingYears'] + 1)
    df['TenureToAgeRatio'] = df['YearsAtCompany'] / df['Age']
    df['RoleTenureRatio'] = df['YearsInCurrentRole'] / (df['YearsAtCompany'] + 1)
    df['ManagerTenureRatio'] = df['YearsWithCurrManager'] / (df['YearsAtCompany'] + 1)
    df['PromotionStagnation'] = df['YearsSinceLastPromotion'] / (df['YearsAtCompany'] + 1)
    
    # Save processed
    output_path = DATA_PROCESSED_DIR / "processed_attrition.csv"
    df.to_csv(output_path, index=False)
    print(f"Processed Attrition data saved: {df.shape} -> {output_path.name}")
    return df


def process_performance_data() -> pd.DataFrame:
    """Clean and engineer features for performance and promotion dataset."""
    df = pd.read_csv(PERFORMANCE_DATA_PATH)
    
    # Clean whitespace in string columns
    str_cols = df.select_dtypes(include='object').columns
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()
        
    # Target binary
    df['Promotion_Numeric'] = df['Promotion Eligibility'].map({'Yes': 1, 'No': 0})
    
    # Composite Productivity & Efficiency Indices
    df['ProductivityIndex'] = (
        df['KPI Score'] * 0.35 +
        df['Task Completion (%)'] * 0.35 +
        df['Attendance (%)'] * 0.15 +
        (df['Peer Rating'] * 20) * 0.15
    )
    df['WorkHourEfficiency'] = df['Task Completion (%)'] / (df['Work Hours Logged'] + 1)
    df['ManagerScoreRatio'] = (df['Manager Feedback'] / 5.0) * 100
    
    # Categorize performance tier
    df['PerformanceTier'] = pd.cut(
        df['ProductivityIndex'],
        bins=[0, 65, 80, 100],
        labels=['Needs Improvement', 'Meets Expectations', 'Exceeds Expectations']
    )
    
    output_path = DATA_PROCESSED_DIR / "processed_performance.csv"
    df.to_csv(output_path, index=False)
    print(f"Processed Performance data saved: {df.shape} -> {output_path.name}")
    return df


def process_training_engagement_data() -> pd.DataFrame:
    """Clean and engineer features for training programs & engagement dataset."""
    df = pd.read_csv(HR_ANALYSIS_DATA_PATH)
    
    # Strip whitespace
    str_cols = df.select_dtypes(include='object').columns
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()
        
    # Standardize Training Outcome into binary success
    df['TrainingSuccess'] = df['Training Outcome'].apply(
        lambda x: 1 if str(x).lower() in ['passed', 'completed'] else 0
    )
    
    # Engineering metrics
    df['CostPerTrainingDay'] = df['Training Cost'] / (df['Training Duration(Days)'] + 0.1)
    df['OverallSatisfactionIndex'] = (
        df['Engagement Score'] +
        df['Satisfaction Score'] +
        df['Work-Life Balance Score']
    ) / 3.0
    
    # Parse dates if present
    for date_col in ['StartDate', 'DOB', 'Survey Date', 'Training Date']:
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], format='mixed', errors='coerce')
            
    output_path = DATA_PROCESSED_DIR / "processed_training_engagement.csv"
    df.to_csv(output_path, index=False)
    print(f"Processed Training & Engagement data saved: {df.shape} -> {output_path.name}")
    return df


def process_onet_skills_taxonomy() -> pd.DataFrame:
    """Clean, aggregate, and index O*NET skills and software taxonomies."""
    occ_df = pd.read_csv(OCCUPATION_DATA_PATH)
    skills_df = pd.read_csv(ESSENTIAL_SKILLS_PATH)
    soft_df = pd.read_csv(SOFTWARE_SKILLS_PATH)
    
    # Strip whitespace
    for d in [occ_df, skills_df, soft_df]:
        for col in d.select_dtypes(include='object').columns:
            d[col] = d[col].astype(str).str.strip()
            
    # Filter for Importance scale (IM)
    im_skills = skills_df[skills_df['Scale ID'] == 'IM'].copy()
    
    # Group top skills per SOC code
    top_skills = (
        im_skills.sort_values(by=['O*NET-SOC Code', 'Data Value'], ascending=[True, False])
        .groupby('O*NET-SOC Code')
        .agg({
            'Element Name': lambda x: '|'.join(list(x)[:10]),
            'Data Value': lambda x: '|'.join([str(round(v, 2)) for v in list(x)[:10]])
        })
        .reset_index()
        .rename(columns={'Element Name': 'TopSkills', 'Data Value': 'SkillImportance'})
    )
    
    # Group top software / hot technologies
    hot_software = (
        soft_df.groupby('O*NET-SOC Code')
        .agg({
            'Workplace Example': lambda x: '|'.join(list(set(x))[:15]),
            'Hot Technology': lambda x: '|'.join(list(x)[:15])
        })
        .reset_index()
        .rename(columns={'Workplace Example': 'SoftwareTools', 'Hot Technology': 'HotTechFlags'})
    )
    
    # Merge with occupation master
    taxonomy_df = occ_df.merge(top_skills, on='O*NET-SOC Code', how='left')
    taxonomy_df = taxonomy_df.merge(hot_software, on='O*NET-SOC Code', how='left')
    
    output_path = DATA_PROCESSED_DIR / "processed_skills_taxonomy.csv"
    taxonomy_df.to_csv(output_path, index=False)
    print(f"Processed Skills Taxonomy saved: {taxonomy_df.shape} -> {output_path.name}")
    return taxonomy_df


def run_full_pipeline():
    """Execute all processing pipelines."""
    print("=" * 50)
    print("[*] Starting Data Processing & Feature Engineering Pipeline")
    print("=" * 50)
    
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    process_attrition_data()
    process_performance_data()
    process_training_engagement_data()
    process_onet_skills_taxonomy()
    
    print("\n[+] All datasets processed successfully and saved to data/processed/!")


if __name__ == "__main__":
    run_full_pipeline()
