/**
 * Shared Client Utilities for PULSE Multi-Page Web Platform
 * Handles session state, dynamic navigation bar, alerts, and API utilities.
 */

// Retrieve Active Session
function getCurrentUser() {
  const u = localStorage.getItem("pulse_user");
  if (!u) return null;
  try {
    return JSON.parse(u);
  } catch (e) {
    localStorage.removeItem("pulse_user");
    return null;
  }
}

// Set Active Session
function setCurrentUser(user) {
  localStorage.setItem("pulse_user", JSON.stringify(user));
}

function saveAuth(user) {
  setCurrentUser(user);
}

// Sign Out User
function logoutUser() {
  localStorage.removeItem("pulse_user");
  window.location.href = "/login";
}

// Enforce Route Protection
function requireAuth(allowedRole = null) {
  const user = getCurrentUser();
  if (!user) {
    window.location.href = "/login";
    return null;
  }
  if (!user.is_verified) {
    window.location.href = "/verify-email";
    return null;
  }
  if (user.role === "employee" && !user.is_onboarded) {
    if (!window.location.pathname.includes("/employee/onboarding")) {
      window.location.href = "/employee/onboarding";
      return null;
    }
  }
  if (allowedRole && user.role !== allowedRole) {
    if (user.role === "hr") {
      window.location.href = "/hr/dashboard";
    } else {
      window.location.href = "/employee/dashboard";
    }
    return null;
  }
  return user;
}

// Render Universal Navbar
function renderNavbar(activePage = "") {
  const user = getCurrentUser();
  const header = document.querySelector(".navbar");
  if (!header) return;

  if (user && user.is_verified) {
    const isHR = user.role === "hr";
    const rolePill = isHR ? "pill-orange" : "pill-green";
    const roleLabel = isHR ? "HR Director" : "Staff Member";
    
    let linksHtml = "";
    if (isHR) {
      linksHtml = `
        <a class="nav-link ${activePage === 'overview' ? 'active' : ''}" href="/hr/dashboard">Command Suite</a>
        <a class="nav-link ${activePage === 'attrition' ? 'active' : ''}" href="/hr/attrition">Attrition AI</a>
        <a class="nav-link ${activePage === 'performance' ? 'active' : ''}" href="/hr/performance">360° Matrix</a>
        <a class="nav-link ${activePage === 'training' ? 'active' : ''}" href="/hr/training">Training ROI</a>
        <a class="nav-link ${activePage === 'skills' ? 'active' : ''}" href="/hr/skills">Career Navigator</a>
        <a class="nav-link ${activePage === 'roster' ? 'active' : ''}" href="/hr/roster">Team Roster</a>
      `;
    } else {
      linksHtml = `
        <a class="nav-link ${activePage === 'emp_dashboard' ? 'active' : ''}" href="/employee/dashboard">My Growth Hub</a>
      `;
    }

    header.innerHTML = `
      <a class="nav-brand" href="${isHR ? '/hr/dashboard' : '/employee/dashboard'}">
        <span class="brand-dot"></span>
        <span>PULSE // HRMS</span>
      </a>
      <nav class="nav-links">
        ${linksHtml}
        <span class="pill ${rolePill}">${roleLabel}: ${user.name}</span>
        <button class="btn btn-secondary btn-sm" onclick="logoutUser()">SIGN OUT</button>
      </nav>
    `;
  } else {
    header.innerHTML = `
      <a class="nav-brand" href="/">
        <span class="brand-dot"></span>
        <span>PULSE // HRMS</span>
      </a>
      <nav class="nav-links">
        <a class="nav-link ${activePage === 'landing' ? 'active' : ''}" href="/">Overview</a>
        <a class="nav-link ${activePage === 'login' ? 'active' : ''}" href="/login">Sign In</a>
        <a class="btn btn-secondary btn-sm" href="/register-employee">EMPLOYEE JOIN</a>
        <a class="btn btn-primary btn-sm" href="/register-hr">START HR TRIAL</a>
      </nav>
    `;
  }
}

// Quick Demo Login Shortcut
function launchQuickDemo(role) {
  if (role === "hr") {
    const demoHR = {
      name: "Sarah Jenkins",
      email: "hr@pulse.ai",
      role: "hr",
      company: "Acme Global Corp",
      hr_code: "HR-7700-ACME",
      is_verified: true,
      is_onboarded: true
    };
    setCurrentUser(demoHR);
    window.location.href = "/hr/dashboard";
  } else {
    const demoEmp = {
      name: "Alex Mercer",
      email: "alex@pulse.ai",
      role: "employee",
      company: "Acme Global Corp",
      hr_code: "HR-7700-ACME",
      assigned_hr: "hr@pulse.ai",
      branch: "New York HQ (USA)",
      department: "Sales",
      job_role: "Sales Representatives",
      target_role: "Sales Managers",
      experience_years: 4,
      skills: ["Strategic Negotiation", "Client Relationship Management", "Salesforce CRM", "Presentation"],
      kpi_score: 88.5,
      attendance: 96.0,
      task_completion: 92.0,
      peer_rating: 4.6,
      is_verified: true,
      is_onboarded: true
    };
    setCurrentUser(demoEmp);
    window.location.href = "/employee/dashboard";
  }
}

// Global Ambient Background SVG Blocks Injector
function injectAmbientBackground() {
  if (!document.querySelector('.bg-ambient-layer')) {
    const layer = document.createElement('div');
    layer.className = 'bg-ambient-layer';
    layer.innerHTML = '<div class="bg-ambient-mesh"></div><div class="bg-ambient-shapes"></div>';
    document.body.prepend(layer);
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', injectAmbientBackground);
} else {
  injectAmbientBackground();
}
