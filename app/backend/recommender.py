"""
O*NET Career Pathway & Skill Gap Recommendation Engine
Matches job roles, calculates competency overlap, identifies skill gaps,
and recommends software tools and upskilling roadmaps.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
from typing import List, Dict, Any, Optional

# Path configuration
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from app.backend.config import *


class SkillRecommender:
    def __init__(self):
        self._load_taxonomy()

    def _load_taxonomy(self):
        """Load processed taxonomy file."""
        if not (DATA_PROCESSED_DIR / "processed_skills_taxonomy.csv").exists():
            from app.backend.data_processor import process_onet_skills_taxonomy
            process_onet_skills_taxonomy()
            
        self.df_taxonomy = pd.read_csv(DATA_PROCESSED_DIR / "processed_skills_taxonomy.csv")
        self.df_taxonomy["Title"] = self.df_taxonomy["Title"].fillna("")
        self.df_taxonomy["Description"] = self.df_taxonomy["Description"].fillna("")

    def search_roles(self, query: str, limit: int = 15) -> List[Dict[str, Any]]:
        """Search occupations by keyword in title or description."""
        if not query or not query.strip():
            sample = self.df_taxonomy.head(limit)
            return sample[["O*NET-SOC Code", "Title", "Description"]].to_dict(orient="records")

        q = query.strip().lower()
        mask = (
            self.df_taxonomy["Title"].str.lower().str.contains(q, na=False) |
            self.df_taxonomy["Description"].str.lower().str.contains(q, na=False)
        )
        results = self.df_taxonomy[mask].head(limit)
        return results[["O*NET-SOC Code", "Title", "Description"]].to_dict(orient="records")

    def get_role_details(self, soc_code: str) -> Optional[Dict[str, Any]]:
        """Retrieve full competencies and software profile for a specific SOC code."""
        row = self.df_taxonomy[self.df_taxonomy["O*NET-SOC Code"] == soc_code]
        if row.empty:
            return None
        
        r = row.iloc[0]
        
        # Parse skills
        skills_raw = str(r.get("TopSkills", "")).split("|") if pd.notna(r.get("TopSkills")) else []
        scores_raw = str(r.get("SkillImportance", "")).split("|") if pd.notna(r.get("SkillImportance")) else []
        skills = []
        for i, s in enumerate(skills_raw):
            if s and s.strip():
                score = float(scores_raw[i]) if i < len(scores_raw) and scores_raw[i] else 3.5
                skills.append({"skill": s.strip(), "importance": score})

        # Parse software
        software_raw = str(r.get("SoftwareTools", "")).split("|") if pd.notna(r.get("SoftwareTools")) else []
        hot_raw = str(r.get("HotTechFlags", "")).split("|") if pd.notna(r.get("HotTechFlags")) else []
        software = []
        for i, sw in enumerate(software_raw):
            if sw and sw.strip():
                is_hot = (i < len(hot_raw) and hot_raw[i] == "Y")
                software.append({"tool": sw.strip(), "is_hot_tech": is_hot})

        return {
            "soc_code": r["O*NET-SOC Code"],
            "title": r["Title"],
            "description": r["Description"],
            "skills": skills,
            "software": software
        }

    def compare_roles(self, current_soc: str, target_soc: str) -> Dict[str, Any]:
        """
        Calculates skill gap, competency overlap %, and upskilling recommendations
        between an employee's current role and a target role.
        """
        curr = self.get_role_details(current_soc)
        tgt = self.get_role_details(target_soc)

        if not curr or not tgt:
            raise ValueError("Invalid current or target SOC code provided.")

        curr_skills_set = {s["skill"].lower(): s["importance"] for s in curr["skills"]}
        tgt_skills_set = {s["skill"].lower(): s["importance"] for s in tgt["skills"]}

        curr_tools_set = {t["tool"].lower() for t in curr["software"]}
        tgt_tools_list = tgt["software"]

        # Competency overlap
        shared_skills = set(curr_skills_set.keys()).intersection(set(tgt_skills_set.keys()))
        missing_skills_keys = set(tgt_skills_set.keys()) - set(curr_skills_set.keys())

        total_target_skills = len(tgt_skills_set) if tgt_skills_set else 1
        skill_match_pct = round((len(shared_skills) / total_target_skills) * 100, 1)

        # Missing skills formatted with importance
        missing_skills = []
        for s in tgt["skills"]:
            if s["skill"].lower() in missing_skills_keys:
                missing_skills.append(s)
        missing_skills = sorted(missing_skills, key=lambda x: x["importance"], reverse=True)

        # Missing software tools to learn
        missing_software = [t for t in tgt_tools_list if t["tool"].lower() not in curr_tools_set]

        # Transition Difficulty
        if skill_match_pct >= 75:
            difficulty = "Low (Natural Progression)"
            diff_color = "#38A169"
        elif skill_match_pct >= 50:
            difficulty = "Moderate (Upskilling Required)"
            diff_color = "#D69E2E"
        else:
            difficulty = "High (Career Pivot / Extensive Training Needed)"
            diff_color = "#E53E3E"

        return {
            "current_title": curr["title"],
            "target_title": tgt["title"],
            "skill_match_pct": skill_match_pct,
            "transition_difficulty": difficulty,
            "diff_color": diff_color,
            "shared_skills_count": len(shared_skills),
            "missing_skills": missing_skills,
            "missing_software": missing_software[:10],
            "target_description": tgt["description"]
        }


# Singleton instance
recommender = SkillRecommender()
