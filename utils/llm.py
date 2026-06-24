import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

def generate_summary(resume_text, jd_text, matching_skills, missing_skills):
    """
    Generate 2-3 sentence analysis summary using Gemini.
    """
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "⚠️ API key not configured. Skipping AI summary."
        
        genai.configure(api_key=api_key)
        
        matching_str = ", ".join(matching_skills[:5]) if matching_skills else "none"
        missing_str = ", ".join(missing_skills[:5]) if missing_skills else "none"
        
        prompt = f"""Given this resume and job description, write a 2-3 sentence summary of how well they match.

Resume (first 1000 chars): {resume_text[:1000]}

Job Description (first 1000 chars): {jd_text[:1000]}

Matching skills: {matching_str}
Missing skills: {missing_str}

Write a brief, encouraging summary. Be specific about strengths and gaps. Keep it under 3 sentences."""
        
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        return response.text
    
    except Exception as e:
        # Fallback if API fails
        return f"Resume shows potential alignment with job requirements. You have {len(matching_skills)} matching skills but are missing key ones like {', '.join(missing_skills[:3])}."

def generate_suggestions(resume_text, jd_text, missing_skills):
    """
    Generate 5 actionable improvement suggestions.
    """
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return get_fallback_suggestions()
        
        genai.configure(api_key=api_key)
        
        missing_str = ", ".join(missing_skills[:5]) if missing_skills else "none"
        
        prompt = f"""As a resume coach, give exactly 5 specific, actionable improvement suggestions for this resume to better match the job.

Resume: {resume_text[:1000]}
Job: {jd_text[:1000]}
Missing skills: {missing_str}

Format as numbered list (1-5 only). Keep each under 1 sentence. Be specific."""
        
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        suggestions = []
        for line in response.text.split('\n'):
            if line.strip() and line[0].isdigit():
                # Remove numbering
                clean = line.lstrip('0123456789.-) ')
                if clean:
                    suggestions.append(clean)
        
        return suggestions[:5] if suggestions else get_fallback_suggestions()
    
    except Exception as e:
        return get_fallback_suggestions()

def get_fallback_suggestions():
    """Fallback suggestions if API fails."""
    return [
        "Add quantifiable metrics to your projects (e.g., 'improved performance by 40%')",
        "Include technologies from the job description in your experience section",
        "Highlight relevant projects that demonstrate required skills",
        "Use industry keywords from the job posting in your resume",
        "Add a professional summary tailored to the role"
    ]