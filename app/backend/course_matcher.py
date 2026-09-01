"""
AI Course Discovery & 30-60-90 Day Upskilling Roadmap Engine
Maps missing O*NET competencies and software tools to verified enterprise courses
(Coursera, edX, LinkedIn Learning, Udemy, AWS, Google).
"""

from typing import List, Dict, Any


COURSE_CATALOG = [
    # Leadership & Management
    {
        "keywords": ["leadership", "management", "directing", "supervision", "coaching"],
        "title": "Strategic Leadership and Management Specialization",
        "provider": "Coursera (University of Illinois)",
        "rating": 4.8,
        "duration_hours": 32,
        "level": "Intermediate",
        "url": "https://www.coursera.org/specializations/strategic-leadership",
        "cost": "$49/mo"
    },
    {
        "keywords": ["negotiation", "persuasion", "sales", "communication", "influencing"],
        "title": "Successful Negotiation: Essential Strategies and Skills",
        "provider": "Coursera (University of Michigan)",
        "rating": 4.9,
        "duration_hours": 16,
        "level": "All Levels",
        "url": "https://www.coursera.org/learn/negotiation-skills",
        "cost": "$49"
    },
    {
        "keywords": ["critical thinking", "complex problem solving", "problem solving", "decision making"],
        "title": "Problem Solving with Critical Thinking",
        "provider": "edX (Fullbridge)",
        "rating": 4.7,
        "duration_hours": 18,
        "level": "Intermediate",
        "url": "https://www.edx.org/course/critical-thinking-and-problem-solving",
        "cost": "$99"
    },
    {
        "keywords": ["speaking", "active listening", "presentation", "public speaking"],
        "title": "Effective Executive Communication & Public Speaking",
        "provider": "LinkedIn Learning",
        "rating": 4.8,
        "duration_hours": 12,
        "level": "All Levels",
        "url": "https://www.linkedin.com/learning/executive-presence-principles",
        "cost": "$35/mo"
    },
    {
        "keywords": ["time management", "organization", "prioritization", "operations analysis"],
        "title": "Operational Excellence and Productivity Mastery",
        "provider": "Udemy",
        "rating": 4.6,
        "duration_hours": 14,
        "level": "Beginner",
        "url": "https://www.udemy.com/course/operational-excellence-foundations",
        "cost": "$29"
    },
    
    # Technical, Data & Analytics
    {
        "keywords": ["python", "programming", "software", "development", "data analysis"],
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
        "keywords": ["data science", "machine learning", "modeling", "statistics", "ai", "mathematics"],
        "title": "IBM Data Science Professional Certificate",
        "provider": "Coursera (IBM)",
        "rating": 4.7,
        "duration_hours": 50,
        "level": "Beginner",
        "url": "https://www.coursera.org/professional-certificates/ibm-data-science",
        "cost": "$49/mo"
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
    {
        "keywords": ["cloud", "aws", "azure", "devops", "infrastructure", "docker", "kubernetes"],
        "title": "AWS Certified Solutions Architect Associate Certification",
        "provider": "AWS / A Cloud Guru",
        "rating": 4.9,
        "duration_hours": 35,
        "level": "Intermediate",
        "url": "https://aws.amazon.com/certification/certified-solutions-architect-associate",
        "cost": "$150"
    },
    {
        "keywords": ["crm", "salesforce", "customer relationship", "hubspot", "client relations"],
        "title": "Salesforce Sales Operations Professional Certificate",
        "provider": "Coursera (Salesforce)",
        "rating": 4.8,
        "duration_hours": 28,
        "level": "Beginner",
        "url": "https://www.coursera.org/professional-certificates/salesforce-sales-operations",
        "cost": "$49/mo"
    },
    {
        "keywords": ["cybersecurity", "security", "governance", "compliance", "risk management"],
        "title": "Google Cybersecurity Professional Certificate",
        "provider": "Coursera (Google)",
        "rating": 4.8,
        "duration_hours": 45,
        "level": "Beginner",
        "url": "https://www.coursera.org/professional-certificates/google-cybersecurity",
        "cost": "$49/mo"
    }
]


class CourseMatcher:
    """Matches skill gaps and tool deficiencies to structured learning roadmaps."""

    def __init__(self):
        self.catalog = COURSE_CATALOG

    def find_courses_for_skills(self, skills: List[Dict[str, Any]], limit: int = 4) -> List[Dict[str, Any]]:
        """Finds most relevant courses based on missing skill names."""
        matched = []
        seen_titles = set()
        
        skill_texts = [s.get("skill", "").lower() for s in skills]
        
        for course in self.catalog:
            score = 0
            for kw in course["keywords"]:
                for stext in skill_texts:
                    if kw in stext or stext in kw:
                        score += 2
            if score > 0 and course["title"] not in seen_titles:
                matched.append({**course, "match_score": score})
                seen_titles.add(course["title"])

        matched.sort(key=lambda x: x["match_score"], reverse=True)
        
        # Fallback if few matches
        if len(matched) < limit:
            for c in self.catalog:
                if c["title"] not in seen_titles:
                    matched.append({**c, "match_score": 1})
                    seen_titles.add(c["title"])
                if len(matched) >= limit:
                    break

        return matched[:limit]

    def generate_30_60_90_plan(self, current_role: str, target_role: str, missing_skills: List[Dict[str, Any]], missing_tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generates a phased 30-60-90 Day Upskilling Roadmap."""
        recommended_courses = self.find_courses_for_skills(missing_skills, limit=4)
        
        skill_names = [s.get("skill", "Core Competency") for s in missing_skills[:4]]
        tool_names = [t.get("tool", "Tech Stack") for t in missing_tools[:4]]

        phase_1_skill = skill_names[0] if len(skill_names) > 0 else "Foundational Domain Knowledge"
        phase_2_skill = skill_names[1] if len(skill_names) > 1 else (skill_names[0] if skill_names else "Advanced Problem Solving")
        phase_3_skill = skill_names[2] if len(skill_names) > 2 else "Strategic Leadership & Execution"
        
        tool_p1 = tool_names[0] if len(tool_names) > 0 else "Enterprise Workflow Tools"
        tool_p2 = tool_names[1] if len(tool_names) > 1 else (tool_names[0] if tool_names else "Analytics Platforms")

        plan = {
            "current_role": current_role,
            "target_role": target_role,
            "total_estimated_hours": sum(c.get("duration_hours", 20) for c in recommended_courses),
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
                        "Lead cross-functional sync on target team projects."
                    ],
                    "deliverable": "Deliver an end-to-end production workflow with documented efficiency gains."
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
