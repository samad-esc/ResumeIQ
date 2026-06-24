from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st

@st.cache_resource
def load_model():
    """Load embedding model once (cached)."""
    return SentenceTransformer('all-MiniLM-L6-v2')

def calculate_job_match_score(resume_text, jd_text, skill_coverage_percent):
    """
    Calculate Job Match Score.
    
    Combines:
    - Semantic similarity (60%)
    - Skill coverage (40%)
    
    Returns score 0-100.
    """
    try:
        model = load_model()
        
        # Semantic similarity
        resume_embedding = model.encode(resume_text)
        jd_embedding = model.encode(jd_text)
        semantic_sim = cosine_similarity([resume_embedding], [jd_embedding])[0][0]
        
        # Combine: semantic (60%) + skills (40%)
        semantic_score = semantic_sim * 100
        combined_score = (semantic_score * 0.6) + (skill_coverage_percent * 0.4)
        
        return int(min(100, max(0, combined_score)))
    
    except Exception as e:
        print(f"Error: {e}")
        return 50

def interpret_match(score):
    """Return interpretation with emoji and color."""
    if score >= 80:
        return "Excellent Match", "🟢", "#00CC96"
    elif score >= 65:
        return "Good Match", "🔵", "#00D5E9"
    elif score >= 50:
        return "Fair Match", "🟡", "#FFA15A"
    else:
        return "Needs Work", "🔴", "#FF6B6B"