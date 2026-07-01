import json
import re
from pathlib import Path
import streamlit as st

@st.cache_data
def load_skills():
    """
    Load skills from JSON file.
    Cached so the file is read only once.
    """
    skills_path = Path(__file__).parent.parent / "data" / "skills.json"
    
    with open(skills_path, "r", encoding="utf-8") as f:
        skills_data = json.load(f)
    
    all_skills = set()
    
    for category in skills_data.values():
        all_skills.update(
            [skill.lower().strip() for skill in category]
        )
    
    return all_skills

def extract_skills(text):
    """
    Extract skills from text using regex matching.
    """
    if not text:
        return []

    skills = load_skills()
    text_lower = text.lower()

    found_skills = set()

    for skill in skills:
        pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, text_lower):
            found_skills.add(skill)

    return sorted(found_skills)

def analyze_skills(resume_skills, jd_skills):
    """
    Compare resume skills against job description skills.
    """
    resume_set = set(resume_skills)
    jd_set = set(jd_skills)

    matching = sorted(resume_set & jd_set)
    missing = sorted(jd_set - resume_set)

    coverage = (
        len(matching) / len(jd_set)
        if jd_set
        else 0
    )

    return {
        "matching": matching,
        "missing": missing,
        "coverage_percent": int(coverage * 100),
        "matched_count": len(matching),
        "total_jd_skills": len(jd_set),
        "resume_skill_count": len(resume_set),
    }