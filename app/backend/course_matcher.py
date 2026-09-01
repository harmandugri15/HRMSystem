"""
AI Course Discovery & 30-60-90 Day Upskilling Roadmap Engine
Maps missing O*NET competencies, target roles, and software tools to verified enterprise courses
(Coursera, edX, LinkedIn Learning, Udemy, AWS, Google, Wharton).
"""

from typing import List, Dict, Any


COURSE_CATALOG = [
    # Computer & Information Systems Management / IT Leadership
    {
        "keywords": ["computer", "information systems", "information technology", "it manager", "systems manager", "chief information", "cto", "cio", "it leadership"],
        "title": "IT Project Management & Technology Leadership",
        "provider": "Coursera (University of Washington)",
        "rating": 4.8,
        "duration_hours": 36,
        "level": "Advanced",
        "url": "https://www.coursera.org/specializations/it-project-management",
        "cost": "$49/mo"
    },
    {
        "keywords": ["cloud", "aws", "azure", "infrastructure", "devops", "systems", "architecture", "information systems"],
        "title": "AWS Certified Solutions Architect & Enterprise Cloud Strategy",
        "provider": "AWS / Coursera",
        "rating": 4.9,
        "duration_hours": 40,
        "level": "Intermediate to Advanced",
        "url": "https://aws.amazon.com/certification/certified-solutions-architect-associate",
        "cost": "$150"
    },
    {
        "keywords": ["cybersecurity", "security", "governance", "compliance", "risk management", "information systems"],
        "title": "Google Cybersecurity & Information Systems Governance",
        "provider": "Coursera (Google)",
        "rating": 4.8,
        "duration_hours": 45,
        "level": "Beginner to Intermediate",
        "url": "https://www.coursera.org/professional-certificates/google-cybersecurity",
        "cost": "$49/mo"
    },
    {
        "keywords": ["software", "engineering", "system design", "architecture", "microservices", "computer"],
        "title": "Software Architecture & Enterprise Distributed Systems",
        "provider": "edX (Dartmouth)",
        "rating": 4.9,
        "duration_hours": 32,
        "level": "Advanced",
        "url": "https://www.edx.org/learn/software-development",
        "cost": "$149"
    },

    # Leadership & Executive Management
    {
        "keywords": ["leadership", "management", "directing", "supervision", "coaching", "executive", "general manager"],
        "title": "Strategic Leadership and Management Specialization",
        "provider": "Coursera (University of Illinois)",
        "rating": 4.8,
        "duration_hours": 32,
        "level": "Intermediate",
        "url": "https://www.coursera.org/specializations/strategic-leadership",
        "cost": "$49/mo"
    },
    {
        "keywords": ["executive", "wharton", "strategy", "organizational leadership", "director"],
        "title": "Wharton Strategic Leadership & Business Transformation",
        "provider": "Coursera (Wharton Executive Education)",
        "rating": 4.9,
        "duration_hours": 28,
        "level": "Executive",
        "url": "https://www.coursera.org/specializations/wharton-leadership",
        "cost": "$79/mo"
    },

    # Sales & Commercial Operations
    {
        "keywords": ["sales", "sales manager", "commercial", "revenue", "pipeline", "quota"],
        "title": "Sales Operations & Pipeline Management Mastery",
        "provider": "Coursera (Northwestern Kellogg)",
        "rating": 4.8,
        "duration_hours": 24,
        "level": "Intermediate",
        "url": "https://www.coursera.org/specializations/sales-management-kellogg",
        "cost": "$49/mo"
    },
    {
        "keywords": ["negotiation", "persuasion", "influencing", "client relations", "deals"],
        "title": "Successful Negotiation: Essential Strategies and Skills",
        "provider": "Coursera (University of Michigan)",
        "rating": 4.9,
        "duration_hours": 16,
        "level": "All Levels",
        "url": "https://www.coursera.org/learn/negotiation-skills",
        "cost": "$49"
    },
    {
        "keywords": ["crm", "salesforce", "customer relationship", "hubspot", "client relations"],
        "title": "Salesforce Sales Operations Professional Certificate",
        "provider": "Coursera (Salesforce)",
        "rating": 4.8,
        "duration_hours": 28,
        "level": "Beginner to Intermediate",
        "url": "https://www.coursera.org/professional-certificates/salesforce-sales-operations",
        "cost": "$49/mo"
    },

    # Data Science, AI & Analytics
    {
        "keywords": ["data science", "data scientist", "machine learning", "modeling", "statistics", "ai", "artificial intelligence"],
        "title": "Machine Learning Specialization by Andrew Ng",
        "provider": "Coursera (DeepLearning.AI / Stanford)",
        "rating": 4.9,
        "duration_hours": 48,
        "level": "Intermediate",
        "url": "https://www.coursera.org/specializations/machine-learning-introduction",
        "cost": "$49/mo"
    },
    {
        "keywords": ["data science", "data analysis", "python", "ibm", "statistics"],
        "title": "IBM Data Science Professional Certificate",
        "provider": "Coursera (IBM)",
        "rating": 4.7,
        "duration_hours": 50,
        "level": "Beginner to Intermediate",
        "url": "https://www.coursera.org/professional-certificates/ibm-data-science",
        "cost": "$49/mo"
    },
    {
        "keywords": ["python", "programming", "developer", "coding", "software engineer"],
        "title": "Python for Everybody Specialization",
        "provider": "Coursera (University of Michigan)",
        "rating": 4.8,
        "duration_hours": 40,
        "level": "Beginner to Intermediate",
        "url": "https://www.coursera.org/specializations/python",
        "cost": "$49/mo"
    },
    {
        "keywords": ["sql", "database", "data management", "mysql", "postgresql", "oracle"],
        "title": "The Complete SQL Bootcamp: Go from Zero to Hero",
        "provider": "Udemy",
        "rating": 4.7,
        "duration_hours": 22,
        "level": "All Levels",
        "url": "https://www.udemy.com/course/the-complete-sql-bootcamp",
        "cost": "$29"
    },
    {
        "keywords": ["excel", "spreadsheets", "financial analysis", "tableau", "power bi", "analytics"],
        "title": "Business Analytics with Excel and Tableau",
        "provider": "Coursera (Johns Hopkins)",
        "rating": 4.8,
        "duration_hours": 20,
        "level": "Intermediate",
        "url": "https://www.coursera.org/learn/business-analytics-excel",
        "cost": "$49"
    },

    # Human Resources & Operations Management
    {
        "keywords": ["human resources", "hr manager", "talent acquisition", "people analytics", "compensation"],
        "title": "Strategic Human Resources Leadership & People Analytics",
        "provider": "Coursera (University of Minnesota)",
        "rating": 4.8,
        "duration_hours": 26,
        "level": "Intermediate",
        "url": "https://www.coursera.org/specializations/human-resource-management",
        "cost": "$49/mo"
    },
    {
        "keywords": ["operations", "operations manager", "supply chain", "logistics", "operational excellence"],
        "title": "Operations & Supply Chain Strategy Specialization",
        "provider": "Coursera (Rutgers University)",
        "rating": 4.8,
        "duration_hours": 30,
        "level": "Intermediate",
        "url": "https://www.coursera.org/specializations/supply-chain-operations",
        "cost": "$49/mo"
    }
]


class CourseMatcher:
    """Matches skill gaps, target roles and tool deficiencies to structured learning roadmaps."""

    def __init__(self):
        self.catalog = COURSE_CATALOG

    def find_courses_for_skills(
        self,
        skills: List[Dict[str, Any]],
        target_role: str = "",
        limit: int = 4
    ) -> List[Dict[str, Any]]:
        """Finds most relevant courses based on missing skill names and target role."""
        matched = []
        seen_titles = set()
        
        skill_texts = [s.get("skill", "").lower() for s in skills if isinstance(s, dict)]
        target_role_lower = target_role.lower()
        
        for course in self.catalog:
            score = 0
            # Check target role keyword match (high priority)
            for kw in course["keywords"]:
                if kw in target_role_lower or target_role_lower in kw:
                    score += 5
                for stext in skill_texts:
                    if kw in stext or stext in kw:
                        score += 3

            if score > 0 and course["title"] not in seen_titles:
                matched.append({**course, "match_score": score})
                seen_titles.add(course["title"])

        matched.sort(key=lambda x: x["match_score"], reverse=True)
        
        # Fallback if fewer than limit
        if len(matched) < limit:
            for c in self.catalog:
                if c["title"] not in seen_titles:
                    matched.append({**c, "match_score": 1})
                    seen_titles.add(c["title"])
                if len(matched) >= limit:
                    break

        return matched[:limit]

    def generate_30_60_90_plan(
        self,
        current_role: str,
        target_role: str,
        missing_skills: List[Dict[str, Any]],
        missing_tools: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generates a phased 30-60-90 Day Upskilling Roadmap."""
        recommended_courses = self.find_courses_for_skills(missing_skills, target_role=target_role, limit=4)
        
        skill_names = [s.get("skill", "Core Competency") for s in missing_skills if isinstance(s, dict)][:4]
        tool_names = [t.get("tool", "Tech Stack") for t in missing_tools if isinstance(t, dict)][:4]

        # Customize based on target role
        if not skill_names:
            if "computer" in target_role.lower() or "systems" in target_role.lower() or "it" in target_role.lower():
                skill_names = ["Cloud Infrastructure Architecture", "IT Governance & Compliance", "Agile Systems Project Management"]
                tool_names = ["AWS / Enterprise Cloud Console", "Cybersecurity Audit Tools"]
            elif "sales" in target_role.lower():
                skill_names = ["Pipeline Analytics & Forecasting", "Executive Negotiation", "Revenue Operations"]
                tool_names = ["Salesforce CRM", "Tableau Analytics"]
            elif "data" in target_role.lower():
                skill_names = ["Machine Learning Modeling", "Statistical Analysis", "Data Pipeline Engineering"]
                tool_names = ["Python & PyTorch", "PostgreSQL & Snowflake"]
            else:
                skill_names = ["Strategic Resource Allocation", "Cross-Functional Directing", "Operational Problem Solving"]
                tool_names = ["Enterprise ERP Systems", "BI Performance Dashboards"]

        phase_1_skill = skill_names[0] if len(skill_names) > 0 else "Foundational Domain Architecture"
        phase_2_skill = skill_names[1] if len(skill_names) > 1 else (skill_names[0] if skill_names else "Advanced Execution & Workflows")
        phase_3_skill = skill_names[2] if len(skill_names) > 2 else f"Strategic Leadership & {target_role} Execution"
        
        tool_p1 = tool_names[0] if len(tool_names) > 0 else "Enterprise Domain Tools"
        tool_p2 = tool_names[1] if len(tool_names) > 1 else (tool_names[0] if tool_names else "Analytics Platforms")

        plan = {
            "current_role": current_role,
            "target_role": target_role,
            "total_estimated_hours": sum(c.get("duration_hours", 24) for c in recommended_courses),
            "recommended_courses": recommended_courses,
            "phases": [
                {
                    "phase": "Phase 1: Days 1 – 30",
                    "title": "Core Foundations & Tool Ramp-Up",
                    "focus_skill": phase_1_skill,
                    "target_tool": tool_p1,
                    "goals": [
                        f"Complete primary certification module in {phase_1_skill}.",
                        f"Gain baseline working fluency with {tool_p1}.",
                        "Establish bi-weekly 1:1 mentorship milestone review with department lead."
                    ],
                    "deliverable": "Demonstrate practical tool proficiency on a sandbox sprint project."
                },
                {
                    "phase": "Phase 2: Days 31 – 60",
                    "title": "Advanced Execution & Applied Projects",
                    "focus_skill": phase_2_skill,
                    "target_tool": tool_p2,
                    "goals": [
                        f"Master advanced operational workflows in {phase_2_skill}.",
                        f"Integrate {tool_p2} into daily departmental deliverables.",
                        f"Lead cross-functional technical sync on {target_role} project priorities."
                    ],
                    "deliverable": f"Deliver an end-to-end production deliverable aligned with {target_role} expectations."
                },
                {
                    "phase": "Phase 3: Days 61 – 90",
                    "title": "Autonomous Leadership & Role Transition",
                    "focus_skill": phase_3_skill,
                    "target_tool": "Cross-Functional Architecture",
                    "goals": [
                        f"Demonstrate mastery in {phase_3_skill} under live operational conditions.",
                        f"Shadow incumbent {target_role} on strategic planning initiatives.",
                        "Formal review of promotion eligibility portfolio with HR leadership."
                    ],
                    "deliverable": f"Final readiness evaluation and formal transition into {target_role}."
                }
            ]
        }
        return plan

    def export_plan_markdown(self, plan: Dict[str, Any]) -> str:
        """Exports the 30-60-90 Day Roadmap into formatted markdown."""
        md = []
        md.append(f"# Executive Career Development Plan: {plan['current_role']} ➔ {plan['target_role']}")
        md.append(f"**Total Upskilling Commitment:** ~{plan['total_estimated_hours']} Hours across 90 Days\n")
        md.append("## Recommended Course Curricula")
        for c in plan["recommended_courses"]:
            md.append(f"- **[{c['title']}]({c['url']})** — *{c['provider']}* ({c['duration_hours']}h | Rating: {c['rating']} ⭐ | Cost: {c['cost']})")
        md.append("\n---\n")
        for p in plan["phases"]:
            md.append(f"### {p['phase']}: {p['title']}")
            md.append(f"- **Primary Competency:** {p['focus_skill']}")
            md.append(f"- **Target Tool:** {p['target_tool']}")
            md.append(f"- **Key Milestone Deliverable:** {p['deliverable']}")
            md.append("- **Milestones:**")
            for g in p["goals"]:
                md.append(f"  - [ ] {g}")
            md.append("")
        return "\n".join(md)


course_matcher = CourseMatcher()
