"""
PULSE // Enterprise AI People Analytics Platform — Multi-Page FastAPI Server
Serves all dedicated HTML pages, REST API endpoints, OTP verification, live course scraper, and onboarding.
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
from app.backend.course_scraper import scrape_live_courses
from app.backend.auth import (
    authenticate_user,
    register_hr_user,
    register_employee_user,
    generate_and_send_otp,
    verify_otp_code,
    complete_employee_onboarding,
    get_employees_for_hr,
    assign_courses_to_employee,
    get_all_users,
    save_all_users,
    validate_hr_code
)

app = FastAPI(
    title="PULSE Enterprise AI People Platform",
    description="Multi-Page Enterprise People Intelligence, Retention Prediction & Skill Navigation API.",
    version="2.3.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
PAGES_DIR = STATIC_DIR / "pages"
PAGES_DIR.mkdir(parents=True, exist_ok=True)

# Mount Static Files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


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


class SendOTPRequest(BaseModel):
    email: str


class VerifyOTPRequest(BaseModel):
    email: str
    otp: str


class LoginRequest(BaseModel):
    email: str
    password: str


class EmployeeOnboardRequest(BaseModel):
    email: str
    branch: str
    department: str
    job_role: str
    target_role: str
    experience_years: int = 3
    skills: List[str] = []


class AssignCoursesRequest(BaseModel):
    employee_email: str
    target_role: str
    courses: Optional[List[Dict[str, Any]]] = None


class ScrapeCoursesRequest(BaseModel):
    query: str
    platform: Optional[str] = None
    limit: int = 6


class CompareRolesRequest(BaseModel):
    current_soc: str
    target_soc: str


class CourseRoadmapRequest(BaseModel):
    current_role: str
    target_role: str
    missing_skills: List[Dict[str, Any]] = []
    missing_tools: List[Dict[str, Any]] = []


# ==============================================================================
# 1. STANDALONE HTML PAGE ROUTES (MULTI-PAGE APPLICATION)
# ==============================================================================

def _serve_page(filename: str):
    p = PAGES_DIR / filename
    if p.exists():
        return FileResponse(str(p))
    p_alt = STATIC_DIR / filename
    if p_alt.exists():
        return FileResponse(str(p_alt))
    raise HTTPException(status_code=404, detail=f"Page {filename} not found.")


@app.api_route("/", methods=["GET", "HEAD"])
def page_landing():
    return _serve_page("landing.html")


@app.api_route("/login", methods=["GET", "HEAD"])
def page_login():
    return _serve_page("login.html")


@app.api_route("/register-hr", methods=["GET", "HEAD"])
def page_register_hr():
    return _serve_page("register_hr.html")


@app.api_route("/register-employee", methods=["GET", "HEAD"])
def page_register_employee():
    return _serve_page("register_employee.html")


@app.api_route("/verify-email", methods=["GET", "HEAD"])
def page_verify_email():
    return _serve_page("verify_email.html")


@app.api_route("/employee/onboarding", methods=["GET", "HEAD"])
def page_employee_onboarding():
    return _serve_page("employee_onboarding.html")


@app.api_route("/employee/dashboard", methods=["GET", "HEAD"])
def page_employee_dashboard():
    return _serve_page("employee_dashboard.html")


@app.api_route("/hr/dashboard", methods=["GET", "HEAD"])
def page_hr_dashboard():
    return _serve_page("hr_dashboard.html")


@app.api_route("/hr/attrition", methods=["GET", "HEAD"])
def page_hr_attrition():
    return _serve_page("hr_attrition.html")


@app.api_route("/hr/performance", methods=["GET", "HEAD"])
def page_hr_performance():
    return _serve_page("hr_performance.html")


@app.api_route("/hr/training", methods=["GET", "HEAD"])
def page_hr_training():
    return _serve_page("hr_training.html")


@app.api_route("/hr/skills", methods=["GET", "HEAD"])
def page_hr_skills():
    return _serve_page("hr_skills.html")


@app.api_route("/hr/roster", methods=["GET", "HEAD"])
def page_hr_roster():
    return _serve_page("hr_roster.html")


# ==============================================================================
# 2. REST API ENDPOINTS
# ==============================================================================

@app.api_route("/api/health", methods=["GET", "HEAD"])
def health_check():
    return {"status": "online", "version": "2.3.0", "mode": "Multi-Page Production"}


@app.get("/api/kpis")
def get_kpis():
    try:
        return get_executive_kpis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/auth/send-otp")
def api_send_otp(req: SendOTPRequest):
    otp = generate_and_send_otp(req.email)
    return {"success": True, "message": f"OTP sent to {req.email}", "otp_preview": otp}


@app.post("/api/auth/verify-otp")
def api_verify_otp(req: VerifyOTPRequest):
    ok, msg = verify_otp_code(req.email, req.otp)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    users = get_all_users()
    user = users.get(req.email.strip().lower(), {})
    user_clean = {k: v for k, v in user.items() if k not in ("password_hash", "salt")}
    return {"success": True, "message": msg, "user": user_clean}


@app.post("/api/auth/register-hr")
def api_register_hr(req: HRRegisterRequest):
    ok, msg, hr_code, otp = register_hr_user(req.name, req.email, req.password, req.company)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg, "hr_code": hr_code, "otp_preview": otp}


@app.post("/api/auth/register-employee")
def api_register_employee(req: EmployeeRegisterRequest):
    ok, msg, otp = register_employee_user(
        name=req.name,
        email=req.email,
        password=req.password,
        hr_code=req.hr_code
    )
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg, "otp_preview": otp}


@app.post("/api/auth/login")
def api_login(req: LoginRequest):
    user = authenticate_user(req.email, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return {"success": True, "user": user}


@app.post("/api/employee/onboard")
def api_employee_onboard(req: EmployeeOnboardRequest):
    # Starts with empty assigned courses until HR assigns
    ok, msg = complete_employee_onboarding(
        email=req.email,
        branch=req.branch,
        department=req.department,
        job_role=req.job_role,
        target_role=req.target_role,
        experience_years=req.experience_years,
        skills=req.skills,
        assigned_courses=[],
        roadmap={}
    )
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    
    users = get_all_users()
    user = users.get(req.email.strip().lower(), {})
    user_clean = {k: v for k, v in user.items() if k not in ("password_hash", "salt")}
    return {"success": True, "message": msg, "user": user_clean}


@app.get("/api/employee/profile/{email}")
def api_get_employee_profile(email: str):
    users = get_all_users()
    email_clean = email.strip().lower()
    if email_clean not in users:
        raise HTTPException(status_code=404, detail="Employee not found.")
    user = users[email_clean]
    return {k: v for k, v in user.items() if k not in ("password_hash", "salt")}


@app.get("/api/employees/{hr_code}")
def api_get_employees(hr_code: str):
    emps = get_employees_for_hr(hr_code)
    return {"hr_code": hr_code, "employees": emps}


@app.get("/api/courses/for-role")
def api_get_courses_for_role(target_role: str):
    """Returns matching verified courses tailored specifically for a target role."""
    courses = course_matcher.find_courses_for_skills([], target_role=target_role, limit=4)
    return {"target_role": target_role, "courses": courses}


@app.post("/api/hr/scrape-courses")
def api_scrape_courses(req: ScrapeCoursesRequest):
    """Live web scraper endpoint for HR to discover courses from Coursera, edX, Udemy, AWS."""
    courses = scrape_live_courses(req.query, req.platform, req.limit)
    return {"query": req.query, "platform": req.platform, "courses": courses}


@app.post("/api/hr/assign-courses")
def api_assign_courses(req: AssignCoursesRequest):
    users = get_all_users()
    email_clean = req.employee_email.strip().lower()
    if email_clean not in users:
        raise HTTPException(status_code=404, detail="Employee account not found.")
    
    emp = users[email_clean]
    curr_role = emp.get("job_role", "Sales Representatives")
    
    # If courses not explicitly provided, generate tailored courses for target_role
    if not req.courses:
        plan = course_matcher.generate_30_60_90_plan(curr_role, req.target_role, [], [])
        courses = plan["recommended_courses"]
        roadmap = plan
    else:
        courses = req.courses
        roadmap = course_matcher.generate_30_60_90_plan(curr_role, req.target_role, [], [])
        roadmap["recommended_courses"] = courses
    
    users[email_clean]["target_role"] = req.target_role
    users[email_clean]["assigned_courses"] = courses
    users[email_clean]["roadmap"] = roadmap
    save_all_users(users)
    
    return {
        "success": True,
        "message": f"Successfully updated promotion path to '{req.target_role}' and assigned {len(courses)} courses!",
        "target_role": req.target_role,
        "assigned_courses": courses
    }


@app.post("/api/predict/attrition")
def api_predict_attrition(payload: Dict[str, Any]):
    try:
        return predictor.predict_attrition(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/predict/promotion")
def api_predict_promotion(payload: Dict[str, Any]):
    try:
        return predictor.predict_promotion(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/predict/training")
def api_predict_training(payload: Dict[str, Any]):
    try:
        return predictor.predict_training_outcome(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/roles/search")
def api_search_roles(q: str = "Engineer", limit: int = 15):
    results = recommender.search_roles(q, limit=limit)
    return {"query": q, "roles": results}


@app.post("/api/roles/compare")
def api_compare_roles(req: CompareRolesRequest):
    try:
        return recommender.compare_roles(req.current_soc, req.target_soc)
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
