import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)


def get_model():
    """
    Initialize Gemini model.
    """
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return None

    genai.configure(api_key=api_key)

    # Keep gemini-pro if you're still using
    # google-generativeai==0.3.0
    return genai.GenerativeModel("gemini-pro")


def generate_summary(
    resume_text,
    jd_text,
    matching_skills,
    missing_skills
):
    """
    Generate a concise resume analysis.
    """
    try:
        model = get_model()

        if not model:
            return "⚠️ Gemini API key not configured."

        matching_str = (
            ", ".join(matching_skills[:5])
            if matching_skills
            else "none"
        )

        missing_str = (
            ", ".join(missing_skills[:5])
            if missing_skills
            else "none"
        )

        prompt = f"""
Given this resume and job description, write a 2-3 sentence summary.

Matching Skills: {matching_str}

Missing Skills: {missing_str}

Resume:
{resume_text[:1000]}

Job Description:
{jd_text[:1000]}

Be specific about strengths and gaps.
Keep it under 3 sentences.
"""

        response = model.generate_content(prompt)

        return response.text.strip()

    except Exception:
        logging.exception("Summary generation failed")

        return (
            f"Resume shows potential alignment with the role. "
            f"You have {len(matching_skills)} matching skills "
            f"but are missing skills such as "
            f"{', '.join(missing_skills[:3]) if missing_skills else 'none'}."
        )


def generate_suggestions(
    resume_text,
    jd_text,
    missing_skills
):
    """
    Generate 5 actionable suggestions.
    """
    try:
        model = get_model()

        if not model:
            return get_fallback_suggestions()

        missing_str = (
            ", ".join(missing_skills[:5])
            if missing_skills
            else "none"
        )

        prompt = f"""
As a resume coach, provide exactly 5 actionable suggestions.

Missing Skills:
{missing_str}

Resume:
{resume_text[:1000]}

Job Description:
{jd_text[:1000]}

Requirements:

* One sentence each
* Specific
* Actionable
* Resume focused
"""

        response = model.generate_content(prompt)

        suggestions = []

        for line in response.text.splitlines():
            line = line.strip()

            if not line:
                continue

            clean = line.lstrip("0123456789.-) ").strip()

            if clean:
                suggestions.append(clean)

        return (
            suggestions[:5]
            if suggestions
            else get_fallback_suggestions()
        )

    except Exception:
        logging.exception("Suggestion generation failed")

        return get_fallback_suggestions()


def get_fallback_suggestions():
    """
    Fallback suggestions if Gemini fails.
    """
    return [
        "Add quantifiable metrics to project descriptions.",
        "Highlight technologies from the job description.",
        "Include projects demonstrating missing skills.",
        "Increase usage of relevant industry keywords.",
        "Add a role-specific professional summary."
    ]