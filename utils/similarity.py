import logging

import streamlit as st
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

logging.basicConfig(level=logging.INFO)


@st.cache_resource
def load_model():
    """
    Load SentenceTransformer once and cache it.
    """
    return SentenceTransformer("all-MiniLM-L6-v2")


def calculate_job_match_score(
    resume_text,
    jd_text,
    skill_coverage_percent
):
    """
    Calculate Job Match Score.

    Weighting:
    - Semantic Similarity: 60%
    - Skill Coverage: 40%
    """
    try:
        model = load_model()

        resume_embedding = model.encode(
            resume_text,
            convert_to_numpy=True
        )

        jd_embedding = model.encode(
            jd_text,
            convert_to_numpy=True
        )

        semantic_similarity = cosine_similarity(
            [resume_embedding],
            [jd_embedding]
        )[0][0]

        semantic_score = semantic_similarity * 100

        final_score = (
            semantic_score * 0.60
            +
            skill_coverage_percent * 0.40
        )

        final_score = int(
            max(
                0,
                min(100, round(final_score))
            )
        )

        return final_score, round(semantic_similarity * 100, 2)

    except Exception:
        logging.exception(
            "Job match calculation failed"
        )

        return 50, 0.0


def interpret_match(score):
    """
    Return label, emoji and color.
    """
    if score >= 80:
        return (
            "Excellent Match",
            "🟢",
            "#00CC96"
        )

    elif score >= 65:
        return (
            "Good Match",
            "🔵",
            "#00D5E9"
        )

    elif score >= 50:
        return (
            "Fair Match",
            "🟡",
            "#FFA15A"
        )

    return (
        "Needs Work",
        "🔴",
        "#FF6B6B"
    )