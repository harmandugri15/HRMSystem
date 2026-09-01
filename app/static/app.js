/**
 * PULSE // Enterprise AI People Analytics & Career Progression Client App
 * Handles SPA navigation, dual-role auth, ML predictions, Chart.js radar, and course roadmaps.
 */

// Application State
let appState = {
  currentUser: null,
  currentView: 'landing',
  perfChart: null,
  latestRoadmapMarkdown: ''
};

// Initialize App on DOM Load
document.addEventListener('DOMContentLoaded', () => {
  initApp();
});

function initApp() {
  fetchKPIs();
  // Check if session stored in localStorage
  const savedUser = localStorage.getItem('pulse_user');
  if (savedUser) {
    try {
      appState.currentUser = JSON.parse(savedUser);
      if (appState.currentUser.role === 'hr') {
        navigateTo('hr');
      } else if (appState.currentUser.role === 'employee') {
        navigateTo('employee');
      }
    } catch(e) {
      localStorage.removeItem('pulse_user');
    }
  }
}

// Navigation & View Routing
function navigateTo(view) {
  appState.currentView = view;
  
  document.getElementById('view-landing').style.display = (view === 'landing') ? 'block' : 'none';
  document.getElementById('view-hr-dashboard').style.display = (view === 'hr') ? 'block' : 'none';
  document.getElementById('view-employee-dashboard').style.display = (view === 'employee') ? 'block' : 'none';

  updateNavbar();

  if (view === 'hr') {
    loadHRDashboard();
  } else if (view === 'employee') {
    loadEmployeeDashboard();
  }
}

function handleNavClick(targetRole) {
  if (!appState.currentUser) {
    openAuthModal(targetRole);
  } else {
    if (appState.currentUser.role === targetRole) {
      navigateTo(targetRole);
    } else {
      alert(`You are currently logged in as ${appState.currentUser.role.toUpperCase()}. Please sign out first to switch portals.`);
    }
  }
}

function updateNavbar() {
  const navLinks = document.getElementById('nav-links');
  if (appState.currentUser) {
    const rolePill = (appState.currentUser.role === 'hr') ? 'pill-orange' : 'pill-green';
    const roleLabel = (appState.currentUser.role === 'hr') ? 'HR Manager' : 'Employee';
    const targetDashboard = appState.currentUser.role;
    
    navLinks.innerHTML = `
      <a class="nav-link" onclick="navigateTo('landing')">Overview</a>
      <a class="nav-link active" onclick="navigateTo('${targetDashboard}')">My Portal</a>
      <span class="pill ${rolePill}">${roleLabel}: ${appState.currentUser.name}</span>
      <button class="btn btn-secondary btn-sm" onclick="logoutUser()">SIGN OUT</button>
    `;
  } else {
    navLinks.innerHTML = `
      <a class="nav-link active" onclick="navigateTo('landing')">Overview</a>
      <a class="nav-link" onclick="openAuthModal('hr')">HR Suite</a>
      <a class="nav-link" onclick="openAuthModal('employee')">Employee Hub</a>
      <button class="btn btn-secondary btn-sm" onclick="openAuthModal('hr')">SIGN IN</button>
      <button class="btn btn-primary btn-sm" onclick="openAuthModal('hr')">LAUNCH APP</button>
    `;
  }
}

// Fetch Executive KPIs
async function fetchKPIs() {
  try {
    const res = await fetch('/api/kpis');
    if (res.ok) {
      const data = await res.json();
      if (document.getElementById('kpi-headcount')) document.getElementById('kpi-headcount').innerText = Number(data.total_headcount).toLocaleString();
      if (document.getElementById('kpi-retention')) document.getElementById('kpi-retention').innerText = `${data.retention_rate}%`;
      if (document.getElementById('kpi-salary')) document.getElementById('kpi-salary').innerText = `$${Number(data.avg_salary).toLocaleString()}`;
      if (document.getElementById('kpi-promotion')) document.getElementById('kpi-promotion').innerText = `${data.promotion_rate}%`;
      if (document.getElementById('kpi-spend')) document.getElementById('kpi-spend').innerText = `$${(Number(data.total_training_spend) / 1000000).toFixed(2)}M`;
    }
  } catch(e) {
    console.error('KPI fetch error:', e);
  }
}

// Modal Control
function openAuthModal(defaultRole = 'hr') {
  document.getElementById('auth-modal').classList.add('active');
  switchAuthModalRole(defaultRole);
}

function closeAuthModal() {
  document.getElementById('auth-modal').classList.remove('active');
}

function switchAuthModalRole(role) {
  const tabHr = document.getElementById('modal-tab-hr');
  const tabEmp = document.getElementById('modal-tab-emp');
  const secHr = document.getElementById('modal-hr-section');
  const secEmp = document.getElementById('modal-emp-section');

  if (role === 'hr') {
    tabHr.classList.add('active');
    tabEmp.classList.remove('active');
    secHr.style.display = 'block';
    secEmp.style.display = 'none';
  } else {
    tabEmp.classList.add('active');
    tabHr.classList.remove('active');
    secEmp.style.display = 'block';
    secHr.style.display = 'none';
  }
}

// Authentication Logic
async function submitLogin(expectedRole) {
  const email = (expectedRole === 'hr') 
    ? document.getElementById('modal-hr-email').value 
    : document.getElementById('modal-emp-email').value;
  const password = (expectedRole === 'hr') 
    ? document.getElementById('modal-hr-pwd').value 
    : document.getElementById('modal-emp-pwd').value;

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    
    const data = await res.json();
    if (res.ok && data.success) {
      appState.currentUser = data.user;
      localStorage.setItem('pulse_user', JSON.stringify(data.user));
      closeAuthModal();
      navigateTo(data.user.role);
    } else {
      alert(data.detail || 'Authentication failed. Please check your credentials.');
    }
  } catch(e) {
    alert('Server error during login.');
  }
}

function quickDemoLogin(role) {
  closeAuthModal();
  if (role === 'hr') {
    appState.currentUser = {
      name: "Sarah Jenkins",
      email: "hr@pulse.ai",
      role: "hr",
      company: "Acme Global Corp",
      hr_code: "HR-7700-ACME"
    };
  } else {
    appState.currentUser = {
      name: "Alex Mercer",
      email: "alex@pulse.ai",
      role: "employee",
      company: "Acme Global Corp",
      hr_code: "HR-7700-ACME",
      assigned_hr: "hr@pulse.ai",
      department: "Sales",
      job_role: "Sales Representatives",
      target_role: "Sales Managers",
      kpi_score: 88.5,
      attendance: 96.0,
      task_completion: 92.0,
      peer_rating: 4.6
    };
  }
  localStorage.setItem('pulse_user', JSON.stringify(appState.currentUser));
  navigateTo(role);
}

function logoutUser() {
  appState.currentUser = null;
  localStorage.removeItem('pulse_user');
  navigateTo('landing');
}

// HR Dashboard Functions
function loadHRDashboard() {
  if (!appState.currentUser) return;
  document.getElementById('hr-welcome-title').innerText = `Welcome, ${appState.currentUser.name}`;
  document.getElementById('hr-company-label').innerText = `${appState.currentUser.company} | HR Executive`;
  const hrCode = appState.currentUser.hr_code || 'HR-7700-ACME';
  document.getElementById('hr-code-display').innerText = hrCode;
  document.getElementById('roster-code-tag').innerText = hrCode;
  
  loadRoster(hrCode);
  initPerformanceChart();
}

function switchHRTab(tabId) {
  const tabs = ['tab-attrition', 'tab-performance', 'tab-roster'];
  const btns = document.querySelectorAll('#view-hr-dashboard .tab-btn');
  
  tabs.forEach((t, i) => {
    const el = document.getElementById(`hr-${t}`);
    if (t === tabId) {
      el.style.display = 'block';
      btns[i].classList.add('active');
    } else {
      el.style.display = 'none';
      btns[i].classList.remove('active');
    }
  });

  if (tabId === 'tab-performance') {
    setTimeout(initPerformanceChart, 100);
  }
}

async function loadRoster(hrCode) {
  try {
    const res = await fetch(`/api/employees/${hrCode}`);
    if (res.ok) {
      const data = await res.json();
      const tbody = document.getElementById('roster-tbody');
      tbody.innerHTML = '';
      
      if (data.employees && data.employees.length > 0) {
        data.employees.forEach(e => {
          tbody.innerHTML += `
            <tr>
              <td><strong>${e.name}</strong></td>
              <td>${e.email}</td>
              <td>${e.department || 'Sales'}</td>
              <td>${e.job_role || 'Sales Representatives'}</td>
              <td><span class="pill pill-orange">${e.target_role || 'Sales Managers'}</span></td>
              <td><strong>${e.kpi_score || '88.5'}</strong></td>
              <td>${e.attendance || '96.0'}%</td>
            </tr>
          `;
        });
      } else {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:#71717A;">No employees registered under this code yet. Share ${hrCode} with your team!</td></tr>`;
      }
    }
  } catch(e) {
    console.error('Roster error:', e);
  }
}

async function runAttritionPrediction() {
  const payload = {
    Age: parseInt(document.getElementById('att-age').value) || 31,
    Department: "Sales",
    JobRole: document.getElementById('att-role').value,
    MonthlyIncome: parseInt(document.getElementById('att-income').value) || 5400,
    OverTime: document.getElementById('att-ot').value,
    YearsAtCompany: parseInt(document.getElementById('att-tenure').value) || 4,
    DistanceFromHome: 12,
    TotalWorkingYears: 6,
    YearsInCurrentRole: 3,
    YearsSinceLastPromotion: 2,
    YearsWithCurrManager: 2,
    JobSatisfaction: 2,
    EnvironmentSatisfaction: 3,
    RelationshipSatisfaction: 3,
    WorkLifeBalance: 2,
    MaritalStatus: "Single",
    BusinessTravel: "Travel_Rarely"
  };

  try {
    const res = await fetch('/api/predict/attrition', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      const data = await res.json();
      document.getElementById('att-prob-val').innerText = `${data.attrition_probability}%`;
      document.getElementById('att-prob-val').style.color = data.risk_color;
      
      const pill = document.getElementById('att-tier-pill');
      pill.innerText = `${data.risk_level.toUpperCase()} RISK`;
      pill.className = (data.risk_level === 'High') ? 'pill pill-red' : (data.risk_level === 'Medium' ? 'pill pill-orange' : 'pill pill-green');

      let driversHtml = '';
      data.risk_drivers.forEach(d => {
        driversHtml += `• ${d}<br>`;
      });
      document.getElementById('att-drivers').innerHTML = driversHtml || 'No critical turnover catalysts detected.';
    }
  } catch(e) {
    console.error('Attrition prediction failed:', e);
  }
}

function initPerformanceChart() {
  const ctx = document.getElementById('perfChart');
  if (!ctx) return;
  
  if (appState.perfChart) {
    appState.perfChart.destroy();
  }

  appState.perfChart = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: ['KPI Target', 'Task Velocity', 'Attendance', 'Peer Rating', 'Manager Score'],
      datasets: [{
        label: 'Employee Capability',
        data: [88, 92, 96, 92, 90],
        backgroundColor: 'rgba(255, 71, 10, 0.15)',
        borderColor: '#FF470A',
        pointBackgroundColor: '#FF470A',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          min: 0,
          max: 100,
          ticks: { display: false },
          grid: { color: '#E2E8F0' },
          angleLines: { color: '#E2E8F0' }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

function runPerformancePrediction() {
  const kpi = parseFloat(document.getElementById('perf-kpi').value) || 88;
  const task = parseFloat(document.getElementById('perf-task').value) || 92;
  const att = parseFloat(document.getElementById('perf-att').value) || 96;
  const peer = parseFloat(document.getElementById('perf-peer').value) || 4.6;

  if (appState.perfChart) {
    appState.perfChart.data.datasets[0].data = [kpi, task, att, peer * 20, 90];
    appState.perfChart.update();
  }

  const prodScore = ((kpi * 0.4) + (task * 0.3) + (att * 0.2) + (peer * 20 * 0.1)).toFixed(1);
  document.getElementById('perf-score-display').innerText = `Productivity: ${prodScore}/100`;
  
  const pill = document.getElementById('perf-status-pill');
  if (prodScore >= 80) {
    pill.className = 'pill pill-green';
    pill.innerText = 'PROMOTION READY';
  } else {
    pill.className = 'pill pill-orange';
    pill.innerText = 'DEVELOPMENT PATHWAY';
  }
}

// Employee Dashboard Functions
async function loadEmployeeDashboard() {
  if (!appState.currentUser) return;
  
  document.getElementById('emp-welcome-title').innerText = `Welcome, ${appState.currentUser.name}`;
  document.getElementById('emp-meta-label').innerText = `${appState.currentUser.department || 'Sales Department'} | Assigned HR: ${appState.currentUser.assigned_hr || 'HR Office'} (${appState.currentUser.hr_code || 'HR-7700-ACME'})`;
  
  document.getElementById('emp-kpi').innerHTML = `${appState.currentUser.kpi_score || 88.5}<span style="font-size:1.1rem; color:var(--text-muted);">/100</span>`;
  document.getElementById('emp-task').innerText = `${appState.currentUser.task_completion || 92.0}%`;
  document.getElementById('emp-att').innerText = `${appState.currentUser.attendance || 96.0}%`;
  document.getElementById('emp-peer').innerHTML = `${appState.currentUser.peer_rating || 4.6}<span style="font-size:1.1rem; color:var(--text-muted);">/5.0</span>`;

  document.getElementById('emp-curr-role').innerText = appState.currentUser.job_role || 'Sales Representatives';
  document.getElementById('emp-tgt-role').innerText = appState.currentUser.target_role || 'Sales Managers';

  loadEmployeeRoadmap(appState.currentUser.job_role || 'Sales Representatives', appState.currentUser.target_role || 'Sales Managers');
}

async function loadEmployeeRoadmap(currRole, tgtRole) {
  try {
    const res = await fetch('/api/courses/roadmap', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        current_role: currRole,
        target_role: tgtRole,
        missing_skills: [
          { skill: "Strategic Negotiation", importance: 4.8 },
          { skill: "Team Leadership and Coaching", importance: 4.6 },
          { skill: "Operational Problem Solving", importance: 4.2 }
        ],
        missing_tools: [
          { tool: "Salesforce CRM", is_hot_tech: true },
          { tool: "Tableau Analytics", is_hot_tech: false }
        ]
      })
    });

    if (res.ok) {
      const data = await res.json();
      appState.latestRoadmapMarkdown = data.markdown;
      
      // Render Course Cards
      const coursesGrid = document.getElementById('courses-grid');
      coursesGrid.innerHTML = '';
      data.plan.recommended_courses.forEach(c => {
        coursesGrid.innerHTML += `
          <div class="card" style="display:flex; flex-direction:column; justify-content:space-between;">
            <div>
              <span class="pill pill-orange">${c.level}</span>
              <h4 style="margin: 10px 0 6px 0; font-size: 1rem;">
                <a href="${c.url}" target="_blank" style="color:var(--text-primary); text-decoration:none;">${c.title}</a>
              </h4>
              <div style="color: var(--text-secondary); font-size: 0.82rem; margin-bottom: 8px;">Provider: <strong>${c.provider}</strong></div>
            </div>
            <div>
              <div style="display:flex; justify-content:space-between; font-size:0.85rem; font-weight:700; border-top:1px solid var(--border-color); padding-top:8px;">
                <span>⏱️ ${c.duration_hours}h</span>
                <span>⭐ ${c.rating}</span>
                <span style="color:var(--accent-flame);">${c.cost}</span>
              </div>
              <div style="margin-top:10px; text-align:center;">
                <a href="${c.url}" target="_blank" class="btn btn-primary btn-sm" style="width:100%;">ENROLL NOW ➔</a>
              </div>
            </div>
          </div>
        `;
      });

      // Render 30-60-90 Roadmap
      const roadmapContainer = document.getElementById('roadmap-container');
      roadmapContainer.innerHTML = '';
      data.plan.phases.forEach(p => {
        let goalsHtml = '';
        p.goals.forEach(g => {
          goalsHtml += `
            <div style="display:flex; align-items:center; gap:8px; margin: 6px 0;">
              <input type="checkbox" style="accent-color:var(--accent-flame); width:16px; height:16px;">
              <span style="font-size:0.92rem; color:var(--text-primary); font-weight:600;">${g}</span>
            </div>
          `;
        });

        roadmapContainer.innerHTML += `
          <div class="card">
            <h4>${p.phase}: ${p.title}</h4>
            <div style="margin: 6px 0 10px 0; font-size: 0.88rem; color: var(--text-secondary);">
              Focus Competency: <span class="pill pill-orange">${p.focus_skill}</span> | Target Tool: <span class="pill pill-blue">${p.target_tool}</span>
            </div>
            <div style="background:#F8FAFC; border:1px solid var(--border-color); border-radius:8px; padding:10px 14px; margin-bottom:12px;">
              <strong>Milestone Deliverable:</strong> <em>${p.deliverable}</em>
            </div>
            <div>
              ${goalsHtml}
            </div>
          </div>
        `;
      });

    }
  } catch(e) {
    console.error('Roadmap error:', e);
  }
}

function downloadCareerPlan() {
  if (!appState.latestRoadmapMarkdown) {
    alert('Plan is generating, please try in a moment.');
    return;
  }
  const blob = new Blob([appState.latestRoadmapMarkdown], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `career_action_plan_${(appState.currentUser.name || 'employee').toLowerCase().replace(/\s+/g, '_')}.md`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
