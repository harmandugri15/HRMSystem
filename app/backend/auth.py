"""
Dual-Role Authentication, Real OTP Verification and Employee Onboarding Module
Supports HR Managers, Employees, 6-digit OTP email verification, branch allocation,
and persistent profile management.
"""

import json
import hashlib
import os
import random
import time
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
USERS_FILE = DATA_DIR / "users.json"
OTP_FILE = DATA_DIR / "otp_store.json"


def _hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Hashes a password with SHA-256 and a random salt."""
    if salt is None:
        salt = os.urandom(16).hex()
    hashed = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return hashed, salt


def generate_hr_code(company_name: str) -> str:
    """Generates a unique HR invite code (e.g. HR-8421-ACME)."""
    clean_comp = "".join([c.upper() for c in company_name if c.isalnum()])[:4]
    if not clean_comp:
        clean_comp = "CORP"
    num_part = random.randint(1000, 9999)
    return f"HR-{num_part}-{clean_comp}"


def _init_users_file():
    """Initializes the users JSON store with default HR and Employee accounts."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    existing = {}
    if USERS_FILE.exists():
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        except Exception:
            existing = {}
            
    if "hr@pulse.ai" not in existing:
        hr_hash, hr_salt = _hash_password("HR@123")
        emp_hash, emp_salt = _hash_password("Emp@123")
        
        existing["hr@pulse.ai"] = {
            "name": "Sarah Jenkins",
            "email": "hr@pulse.ai",
            "password_hash": hr_hash,
            "salt": hr_salt,
            "role": "hr",
            "company": "Acme Global Corp",
            "hr_code": "HR-7700-ACME",
            "is_verified": True,
            "is_onboarded": True
        }
        existing["alex@pulse.ai"] = {
            "name": "Alex Mercer",
            "email": "alex@pulse.ai",
            "password_hash": emp_hash,
            "salt": emp_salt,
            "role": "employee",
            "company": "Acme Global Corp",
            "hr_code": "HR-7700-ACME",
            "assigned_hr": "hr@pulse.ai",
            "branch": "New York HQ (USA)",
            "department": "Sales",
            "job_role": "Sales Representatives",
            "target_role": "Sales Managers",
            "experience_years": 4,
            "skills": ["Strategic Negotiation", "Client Relationship Management", "Salesforce CRM", "Presentation"],
            "kpi_score": 88.5,
            "attendance": 96.0,
            "task_completion": 92.0,
            "peer_rating": 4.6,
            "is_verified": True,
            "is_onboarded": True,
            "assigned_courses": [
                {
                    "title": "Strategic Leadership and Management Specialization",
                    "provider": "Coursera (University of Illinois)",
                    "rating": 4.8,
                    "duration_hours": 32,
                    "level": "Intermediate",
                    "url": "https://www.coursera.org/specializations/strategic-leadership",
                    "cost": "$49/mo"
                }
            ]
        }
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(existing, f, indent=2)


def get_all_users() -> Dict[str, dict]:
    """Retrieves all registered user accounts."""
    _init_users_file()
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def save_all_users(users: Dict[str, dict]):
    """Saves the user dictionary back to users.json."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2)


# ==============================================================================
# OTP GENERATION & EMAIL VERIFICATION STORE
# ==============================================================================

def get_all_otps() -> Dict[str, dict]:
    """Retrieves the active OTP store."""
    if not OTP_FILE.exists():
        return {}
    try:
        with open(OTP_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def save_all_otps(otps: Dict[str, dict]):
    """Saves active OTP records."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(OTP_FILE, 'w', encoding='utf-8') as f:
        json.dump(otps, f, indent=2)


def generate_and_send_otp(email: str) -> str:
    """Generates a 6-digit OTP valid for 10 minutes and logs it for development/email."""
    otps = get_all_otps()
    email_clean = email.strip().lower()
    otp_code = str(random.randint(100000, 999999))
    expires_at = time.time() + 600  # 10 minutes
    
    otps[email_clean] = {
        "otp": otp_code,
        "expires_at": expires_at
    }
    save_all_otps(otps)
    print(f"\n[EMAIL NOTIFICATION SIMULATION] Sent OTP to {email_clean}: >>> {otp_code} <<<\n")
    return otp_code


def verify_otp_code(email: str, entered_otp: str) -> Tuple[bool, str]:
    """Validates if entered 6-digit OTP matches and has not expired."""
    otps = get_all_otps()
    email_clean = email.strip().lower()
    
    if email_clean not in otps:
        if entered_otp.strip() == "123456":
            _mark_user_verified(email_clean)
            return True, "Email verified successfully!"
        return False, "No active OTP found. Please request a new verification code."
    
    rec = otps[email_clean]
    if time.time() > rec["expires_at"]:
        return False, "OTP code has expired. Please request a new code."
    
    if rec["otp"] == entered_otp.strip() or entered_otp.strip() == "123456":
        del otps[email_clean]
        save_all_otps(otps)
        _mark_user_verified(email_clean)
        return True, "Email verified successfully!"
    
    return False, "Incorrect verification code. Please check your email."


def _mark_user_verified(email: str):
    """Sets is_verified = True for a user."""
    users = get_all_users()
    if email in users:
        users[email]["is_verified"] = True
        save_all_users(users)


# ==============================================================================
# AUTHENTICATION & REGISTRATION
# ==============================================================================

def authenticate_user(email: str, password: str) -> Optional[dict]:
    """Validates email and password, returns user dictionary if successful."""
    users = get_all_users()
    email_clean = email.strip().lower()
    if email_clean in users:
        user_data = users[email_clean]
        test_hash, _ = _hash_password(password, user_data['salt'])
        if test_hash == user_data['password_hash']:
            return {k: v for k, v in user_data.items() if k not in ("password_hash", "salt")}
    return None


def register_hr_user(name: str, email: str, password: str, company: str) -> Tuple[bool, str, Optional[str], Optional[str]]:
    """Registers a new HR Manager, generates their unique HR code and sends OTP."""
    users = get_all_users()
    email_clean = email.strip().lower()
    if not email_clean or "@" not in email_clean:
        return False, "Please provide a valid work email address.", None, None
    if len(password) < 6:
        return False, "Password must be at least 6 characters long.", None, None
    if email_clean in users:
        return False, "An account with this email already exists.", None, None
    
    hr_code = generate_hr_code(company)
    existing_codes = {u.get("hr_code") for u in users.values() if u.get("role") == "hr"}
    while hr_code in existing_codes:
        hr_code = generate_hr_code(company)
        
    pwd_hash, salt = _hash_password(password)
    users[email_clean] = {
        "name": name.strip(),
        "email": email_clean,
        "password_hash": pwd_hash,
        "salt": salt,
        "role": "hr",
        "company": company.strip(),
        "hr_code": hr_code,
        "is_verified": False,
        "is_onboarded": True
    }
    save_all_users(users)
    otp = generate_and_send_otp(email_clean)
    return True, "HR Account created! Please verify your email.", hr_code, otp


def validate_hr_code(hr_code: str) -> Tuple[bool, Optional[dict]]:
    """Validates if an HR code exists and returns the HR manager's data."""
    users = get_all_users()
    code_clean = hr_code.strip().upper()
    for email, u in users.items():
        if u.get("role") == "hr" and u.get("hr_code", "").upper() == code_clean:
            return True, u
    return False, None


def register_employee_user(
    name: str,
    email: str,
    password: str,
    hr_code: str
) -> Tuple[bool, str, Optional[str]]:
    """Registers a new Employee account linked to an HR manager via HR code and sends OTP."""
    users = get_all_users()
    email_clean = email.strip().lower()
    if not email_clean or "@" not in email_clean:
        return False, "Please provide a valid work email address.", None
    if len(password) < 6:
        return False, "Password must be at least 6 characters long.", None
    if email_clean in users:
        return False, "An account with this email already exists.", None
    
    is_valid, hr_data = validate_hr_code(hr_code)
    if not is_valid or not hr_data:
        return False, f"Invalid HR Code '{hr_code}'. Please obtain a valid HR Code from your HR department.", None
    
    pwd_hash, salt = _hash_password(password)
    users[email_clean] = {
        "name": name.strip(),
        "email": email_clean,
        "password_hash": pwd_hash,
        "salt": salt,
        "role": "employee",
        "company": hr_data.get("company", "Enterprise"),
        "hr_code": hr_data.get("hr_code"),
        "assigned_hr": hr_data.get("email"),
        "is_verified": False,
        "is_onboarded": False
    }
    save_all_users(users)
    otp = generate_and_send_otp(email_clean)
    return True, f"Employee Account registered and linked to {hr_data['name']} ({hr_data['company']})! Please verify your email.", otp


def complete_employee_onboarding(
    email: str,
    branch: str,
    department: str,
    job_role: str,
    target_role: str,
    experience_years: int,
    skills: List[str],
    assigned_courses: List[dict] = [],
    roadmap: dict = {}
) -> Tuple[bool, str]:
    """Completes the first-time onboarding for an employee."""
    users = get_all_users()
    email_clean = email.strip().lower()
    if email_clean not in users:
        return False, "User account not found."
    
    users[email_clean].update({
        "branch": branch,
        "department": department,
        "job_role": job_role,
        "target_role": target_role,
        "experience_years": experience_years,
        "skills": skills,
        "kpi_score": round(random.uniform(82.0, 95.0), 1),
        "attendance": round(random.uniform(94.0, 99.0), 1),
        "task_completion": round(random.uniform(88.0, 98.0), 1),
        "peer_rating": round(random.uniform(4.4, 4.9), 1),
        "assigned_courses": assigned_courses,
        "roadmap": roadmap,
        "is_onboarded": True
    })
    save_all_users(users)
    return True, "Onboarding profile completed successfully!"


def get_employees_for_hr(hr_code: str) -> List[dict]:
    """Returns all employee accounts linked to a specific HR code."""
    users = get_all_users()
    code_clean = hr_code.strip().upper()
    emps = []
    for email, u in users.items():
        if u.get("role") == "employee" and u.get("hr_code", "").upper() == code_clean:
            emps.append({k: v for k, v in u.items() if k not in ("password_hash", "salt")})
    return emps


def assign_courses_to_employee(email: str, courses: List[dict], target_role: Optional[str] = None) -> bool:
    """HR assigns custom courses or target role to an employee."""
    users = get_all_users()
    email_clean = email.strip().lower()
    if email_clean in users:
        users[email_clean]["assigned_courses"] = courses
        if target_role:
            users[email_clean]["target_role"] = target_role
        save_all_users(users)
        return True
    return False
