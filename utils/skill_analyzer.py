import json
import re
from pathlib import Path

def load_skills():
    """Load skills from JSON file."""
    skills_path = Path(__file__).parent.parent / "data" / "skills.json"
    
    with open(skills_path, "r") as f:
        skills_data = json.load(f)
    
    # Flatten all skills into one set
    all_skills = set()
    for category in skills_data.values():
        all_skills.update([s.lower() for s in category])
    
    return all_skills

def extract_skills(text):
    """Extract skills from text."""
    skills = load_skills()
    text_lower = text.lower()
    found_skills = []
    
    for skill in skills:
        # Word boundary to avoid partial matches
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.append(skill)
    
    return sorted(list(set(found_skills)))

def analyze_skills(resume_skills, jd_skills):
    """Compare resume skills with job description skills."""
    resume_set = set(resume_skills)
    jd_set = set(jd_skills)
    
    matching = sorted(list(resume_set & jd_set))
    missing = sorted(list(jd_set - resume_set))
    
    coverage = len(matching) / len(jd_set) if jd_set else 0
    
    return {
        "matching": matching,
        "missing": missing,
        "coverage_percent": int(coverage * 100),
        "matched_count": len(matching),
        "total_jd_skills": len(jd_set),
        "resume_skill_count": len(resume_set),
    }