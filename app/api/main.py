"""
PULSE // Enterprise AI People Analytics Platform — FastAPI REST API Server
Serves real-time ML diagnostics, O*NET taxonomies, dual-role auth, and course roadmaps.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.backend.data_loader import get_executive_kpis, get_attrition_df, get_performance_df, get_training_df
from app.backend.predictor import predictor
from app.backend.recommender import recommender
from app.backend.course_matcher import course_matcher
from app.backend.auth import (
    authenticate_user,
    register_hr_user,
    register_employee_user,
    get_employees_for_hr,
    validate_hr_code
)

app = FastAPI(
    title="PULSE Enterprise AI People Analytics API",
    description="High-performance backend for workforce intelligence, retention prediction, and career pathing.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request/Response Models ---

class HRRegisterRequest(BaseModel):
    name: str
    company: str
    email: str
    password: str


class EmployeeRegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    hr_code: str
    department: str = "Sales"
    job_role: str = "Sales Representatives"
    target_role: str = "Sales Managers"


class LoginRequest(BaseModel):
    email: str
    password: str


class CompareRolesRequest(BaseModel):
    current_soc: str
    target_soc: str


class CourseRoadmapRequest(BaseModel):
    current_role: str
    target_role: str
    missing_skills: List[Dict[str, Any]] = []
    missing_tools: List[Dict[str, Any]] = []


# --- API Routes ---

@app.get("/api/health")
def health_check():
    return {"status": "online", "version": "2.0.0", "engine": "Production"}


@app.get("/api/kpis")
def get_kpis():
    try:
        kpis = get_executive_kpis()
        return kpis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/auth/register-hr")
def api_register_hr(req: HRRegisterRequest):
    ok, msg, hr_code = register_hr_user(req.name, req.email, req.password, req.company)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg, "hr_code": hr_code}


@app.post("/api/auth/register-employee")
def api_register_employee(req: EmployeeRegisterRequest):
    ok, msg = register_employee_user(
        name=req.name,
        email=req.email,
        password=req.password,
        hr_code=req.hr_code,
        department=req.department,
        job_role=req.job_role,
        target_role=req.target_role
    )
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg}


@app.post("/api/auth/login")
def api_login(req: LoginRequest):
    user = authenticate_user(req.email, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return {"success": True, "user": user}


@app.get("/api/employees/{hr_code}")
def api_get_employees(hr_code: str):
    emps = get_employees_for_hr(hr_code)
    return {"hr_code": hr_code, "employees": emps}


@app.post("/api/predict/attrition")
def api_predict_attrition(payload: Dict[str, Any]):
    try:
        res = predictor.predict_attrition(payload)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/predict/promotion")
def api_predict_promotion(payload: Dict[str, Any]):
    try:
        res = predictor.predict_promotion(payload)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/predict/training")
def api_predict_training(payload: Dict[str, Any]):
    try:
        res = predictor.predict_training_outcome(payload)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/roles/search")
def api_search_roles(q: str = "Engineer", limit: int = 15):
    results = recommender.search_roles(q, limit=limit)
    return {"query": q, "roles": results}


@app.get("/api/roles/details/{code}")
def api_role_details(code: str):
    details = recommender.get_role_details(code)
    if not details:
        raise HTTPException(status_code=404, detail="Role not found.")
    return details


@app.post("/api/roles/compare")
def api_compare_roles(req: CompareRolesRequest):
    try:
        res = recommender.compare_roles(req.current_soc, req.target_soc)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/courses/roadmap")
def api_generate_roadmap(req: CourseRoadmapRequest):
    try:
        plan = course_matcher.generate_30_60_90_plan(
            req.current_role,
            req.target_role,
            req.missing_skills,
            req.missing_tools
        )
        md = course_matcher.export_plan_markdown(plan)
        return {"plan": plan, "markdown": md}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Mount Static Files
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def serve_index():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return JSONResponse({"message": "PULSE API online. Static frontend building..."})
