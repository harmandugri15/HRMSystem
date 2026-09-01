from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
APP_DIR = BASE_DIR / "app"
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
NOTEBOOKS_DIR = BASE_DIR / "notebooks"

# Data Subdirectories
DATA_RAW_DIR = DATA_DIR / "raw"
DATA_PROCESSED_DIR = DATA_DIR / "processed"
DATA_EXTERNAL_DIR = DATA_DIR / "external"
MODELS_PREPROCESSORS_DIR = MODELS_DIR / "preprocessors"

# Raw File Paths
ATTRITION_DATA_PATH = DATA_RAW_DIR / "employee_attrition.csv"
PERFORMANCE_DATA_PATH = DATA_RAW_DIR / "Employee_Performance_Dataset.csv"
PERFORMANCE_PRO_DATA_PATH = DATA_RAW_DIR / "employee_performance_pro.csv"
HR_ANALYSIS_DATA_PATH = DATA_RAW_DIR / "Cleaned_HR_Data_Analysis.csv"

# External O*NET File Paths
OCCUPATION_DATA_PATH = DATA_EXTERNAL_DIR / "occupation_data.csv"
ESSENTIAL_SKILLS_PATH = DATA_EXTERNAL_DIR / "essential_skills.csv"
SOFTWARE_SKILLS_PATH = DATA_EXTERNAL_DIR / "software_skills.csv"

# Model Artifacts Paths
ATTRITION_MODEL_PATH = MODELS_DIR / "attrition_model.joblib"
PERFORMANCE_MODEL_PATH = MODELS_DIR / "performance_model.joblib"
TRAINING_MODEL_PATH = MODELS_DIR / "training_model.joblib"
