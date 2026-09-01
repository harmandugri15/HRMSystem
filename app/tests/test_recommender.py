"""
Unit tests for O*NET Skills Recommender Engine.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from app.backend.recommender import recommender


def test_role_search():
    """Verify search returns matching roles."""
    results = recommender.search_roles("Engineer", limit=5)
    assert len(results) > 0
    assert all("O*NET-SOC Code" in r for r in results)


def test_role_details():
    """Verify role details contain parsed competencies and software tools."""
    roles = recommender.search_roles("Manager", limit=1)
    assert len(roles) == 1
    soc = roles[0]["O*NET-SOC Code"]
    details = recommender.get_role_details(soc)
    assert details is not None
    assert "skills" in details
    assert "software" in details


def test_role_comparison():
    """Verify comparison calculates match percentage and missing skills."""
    roles = recommender.search_roles("Software", limit=2)
    assert len(roles) >= 2
    soc1 = roles[0]["O*NET-SOC Code"]
    soc2 = roles[1]["O*NET-SOC Code"]
    comp = recommender.compare_roles(soc1, soc2)
    assert "skill_match_pct" in comp
    assert 0.0 <= comp["skill_match_pct"] <= 100.0
    assert "transition_difficulty" in comp
