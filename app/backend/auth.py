"""
Dual-Role Authentication and User Management Module
Supports HR Managers (with unique generated HR Codes) and Employees (linked via HR Code),
persistent JSON storage, secure password hashing, and profile management.
"""

import json
import hashlib
import os
import random
import string
from pathlib import Path
from typing import Optional, Dict, List, Tuple

USERS_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "users.json"


def _hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Hashes a password with SHA-256 and a random salt."""
    if salt is None:
        salt = os.urandom(16).hex()
    hashed = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return hashed, salt


def generate_hr_code(company_name: str) -> str:
    """Generates a clean, unique HR invite code (e.g. HR-8421-ACME)."""
    clean_comp = "".join([c.upper() for c in company_name if c.isalnum()])[:4]
    if not clean_comp:
        clean_comp = "CORP"
    num_part = random.randint(1000, 9999)
    return f"HR-{num_part}-{clean_comp}"


def _init_users_file():
    """Initializes the users JSON store with default HR and Employee accounts."""
    if not USERS_FILE.exists():
        USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
        hr_hash, hr_salt = _hash_password("HR@123")
        emp_hash, emp_salt = _hash_password("Emp@123")
        
        initial_users = {
            "hr@pulse.ai": {
                "name": "Sarah Jenkins",
                "email": "hr@pulse.ai",
                "password_hash": hr_hash,
                "salt": hr_salt,
                "role": "hr",
                "company": "Acme Global Corp",
                "hr_code": "HR-7700-ACME"
            },
            "alex@pulse.ai": {
                "name": "Alex Mercer",
                "email": "alex@pulse.ai",
                "password_hash": emp_hash,
                "salt": emp_salt,
                "role": "employee",
                "company": "Acme Global Corp",
                "hr_code": "HR-7700-ACME",
                "assigned_hr": "hr@pulse.ai",
                "department": "Sales",
                "job_role": "Sales Representatives",
                "target_role": "Sales Managers",
                "kpi_score": 88.5,
                "attendance": 96.0,
                "task_completion": 92.0,
                "peer_rating": 4.6
            }
        }
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(initial_users, f, indent=2)


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
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2)


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


def register_hr_user(name: str, email: str, password: str, company: str) -> Tuple[bool, str, Optional[str]]:
    """Registers a new HR Manager and generates their unique HR code."""
    users = get_all_users()
    email_clean = email.strip().lower()
    if not email_clean or "@" not in email_clean:
        return False, "Please provide a valid work email address.", None
    if len(password) < 6:
        return False, "Password must be at least 6 characters long.", None
    if email_clean in users:
        return False, "An account with this email already exists.", None
    
    hr_code = generate_hr_code(company)
    # Ensure uniqueness
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
        "hr_code": hr_code
    }
    save_all_users(users)
    return True, "HR Account created successfully!", hr_code


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
    hr_code: str,
    department: str = "Sales",
    job_role: str = "Sales Representatives",
    target_role: str = "Sales Managers"
) -> Tuple[bool, str]:
    """Registers a new Employee account linked to an HR manager via HR code."""
    users = get_all_users()
    email_clean = email.strip().lower()
    if not email_clean or "@" not in email_clean:
        return False, "Please provide a valid work email address."
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    if email_clean in users:
        return False, "An account with this email already exists."
    
    is_valid, hr_data = validate_hr_code(hr_code)
    if not is_valid or not hr_data:
        return False, f"Invalid HR Code '{hr_code}'. Please obtain a valid HR Invite Code from your HR department."
    
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
        "department": department,
        "job_role": job_role,
        "target_role": target_role,
        "kpi_score": round(random.uniform(80.0, 95.0), 1),
        "attendance": round(random.uniform(92.0, 99.0), 1),
        "task_completion": round(random.uniform(85.0, 98.0), 1),
        "peer_rating": round(random.uniform(4.2, 4.9), 1)
    }
    save_all_users(users)
    return True, f"Employee Account registered and linked to {hr_data['name']} ({hr_data['company']})!"


def get_employees_for_hr(hr_code: str) -> List[dict]:
    """Returns all employee accounts linked to a specific HR code."""
    users = get_all_users()
    code_clean = hr_code.strip().upper()
    emps = []
    for email, u in users.items():
        if u.get("role") == "employee" and u.get("hr_code", "").upper() == code_clean:
            emps.append({k: v for k, v in u.items() if k not in ("password_hash", "salt")})
    return emps


def update_employee_profile(email: str, updates: dict) -> bool:
    """Updates an employee's profile data."""
    users = get_all_users()
    email_clean = email.strip().lower()
    if email_clean in users:
        for k, v in updates.items():
            users[email_clean][k] = v
        save_all_users(users)
        return True
    return False
