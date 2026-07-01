"""
ResumeIQ - AI-powered Resume to Job Match Analyzer
Phase 1.2: ATS Analyzer Integration
"""

import streamlit as st
import os
import time
from utils.pdf_parser import extract_text_from_pdf
from utils.skill_analyzer import extract_skills, analyze_skills
from utils.similarity import load_model, calculate_job_match_score, interpret_match
from utils.llm import generate_summary, generate_suggestions
from utils.ats_analyzer import ATSAnalyzer


# ============================================================================
# PAGE CONFIG & SESSION STATE
# ============================================================================

st.set_page_config(
    page_title="ResumeIQ - Resume Matcher",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if "results" not in st.session_state:
    st.session_state.results = None

# ============================================================================
# CUSTOM CSS STYLING (Unchanged)
# ============================================================================

st.markdown("""
<style>
    * {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    body {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        color: #fff;
    }
    
    .main {
        background: transparent;
    }
    
    .hero-title {
        font-size: 3em;
        font-weight: 700;
        background: linear-gradient(120deg, #84fab0 0%, #8fd3f4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
        text-align: center;
    }
    
    .hero-subtitle {
        font-size: 1.1em;
        color: #b0b3ff;
        text-align: center;
        margin-bottom: 30px;
    }
    
    .card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .score-card {
        background: linear-gradient(135deg, rgba(132, 250, 176, 0.1), rgba(143, 211, 244, 0.1));
        border: 2px solid rgba(132, 250, 176, 0.3);
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        backdrop-filter: blur(10px);
    }
    
    .ats-card {
        background: linear-gradient(135deg, rgba(255, 182, 193, 0.1), rgba(255, 218, 185, 0.1));
        border: 2px solid rgba(255, 182, 193, 0.3);
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        backdrop-filter: blur(10px);
    }
    
    .metric-value {
        font-size: 2.5em;
        font-weight: 700;
        color: #84fab0;
        margin: 10px 0;
    }
    
    .ats-metric-value {
        font-size: 2.5em;
        font-weight: 700;
        color: #ffc0cb;
        margin: 10px 0;
    }
    
    .metric-label {
        font-size: 0.9em;
        color: #b0b3ff;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .skill-tag {
        display: inline-block;
        background: rgba(132, 250, 176, 0.2);
        color: #84fab0;
        padding: 5px 12px;
        border-radius: 20px;
        margin: 5px;
        font-size: 0.85em;
        border: 1px solid rgba(132, 250, 176, 0.3);
    }
    
    .missing-skill-tag {
        display: inline-block;
        background: rgba(255, 182, 193, 0.2);
        color: #ff6b9d;
        padding: 5px 12px;
        border-radius: 20px;
        margin: 5px;
        font-size: 0.85em;
        border: 1px solid rgba(255, 182, 193, 0.3);
    }
    
    .recommendation-item {
        background: rgba(255, 255, 255, 0.03);
        border-left: 3px solid #84fab0;
        padding: 12px 15px;
        margin: 10px 0;
        border-radius: 5px;
        font-size: 0.95em;
    }
    
    .ats-recommendation-item {
        background: rgba(255, 255, 255, 0.03);
        border-left: 3px solid #ffc0cb;
        padding: 12px 15px;
        margin: 10px 0;
        border-radius: 5px;
        font-size: 0.95em;
    }
    
    .grade-a { color: #00ff00; font-weight: 700; }
    .grade-b { color: #84fab0; font-weight: 700; }
    .grade-c { color: #ffd700; font-weight: 700; }
    .grade-d { color: #ff6b9d; font-weight: 700; }
    .grade-f { color: #ff0000; font-weight: 700; }
    
    .health-check {
        display: flex;
        align-items: center;
        margin: 8px 0;
        font-size: 0.9em;
    }
    
    .health-check-yes {
        color: #84fab0;
    }
    
    .health-check-no {
        color: #ff6b9d;
    }
    
    .section-status {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        font-size: 0.9em;
    }
    
    .format-status {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        font-size: 0.9em;
    }
    
    .footer {
        text-align: center;
        color: #666;
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        font-size: 0.85em;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def format_ats_score_breakdown(scores: dict) -> str:
    """Format ATS score breakdown for display."""
    breakdown = f"""
    • **Contact Info:** {scores['contact_score']}/20
    • **Sections:** {scores['section_score']}/30
    • **Formatting:** {scores['format_score']}/20
    • **Keywords:** {scores['keyword_score']}/30
    """
    return breakdown


def display_resume_health(contact_info: dict):
    """Display resume contact information health check."""
    st.markdown("**📋 Contact Information Health**")
    
    health_items = [
        ("📧 Email", contact_info["email"]),
        ("📱 Phone", contact_info["phone"]),
        ("💼 LinkedIn", contact_info["linkedin"]),
        ("🐙 GitHub", contact_info["github"]),
    ]
    
    for label, present in health_items:
        status = "✅" if present else "❌"
        color_class = "health-check-yes" if present else "health-check-no"
        st.markdown(f"""
        <div class="health-check">
            <span style="margin-right: 10px;">{status}</span>
            <span class="{color_class}">{label}</span>
        </div>
        """, unsafe_allow_html=True)


def display_resume_sections(sections: dict):
    """Display resume sections status."""
    st.markdown("**📑 Resume Sections**")
    
    for section, present in sections.items():
        status = "✅" if present else "❌"
        color = "#84fab0" if present else "#ff6b9d"
        st.markdown(f"""
        <div class="section-status">
            <span>{status} {section}</span>
            <span style="color: {color};">{'Present' if present else 'Missing'}</span>
        </div>
        """, unsafe_allow_html=True)


def display_formatting_status(formatting: dict, word_count: int):
    """Display formatting status and length assessment."""
    st.markdown("**✨ Formatting Status**")
    
    length_status = formatting["length"]
    length_color = {
        "very_short": "#ff4d4f",
        "short": "#ff6b9d",
        "optimal": "#84fab0",
        "long": "#ffd700",
        "very_long": "#ff8c00"
    }.get(length_status, "#fff")
    
    length_label = {
        "very_short": "Very Short (<200 words)",
        "short": "Short (200–349 words)",
        "optimal": "Optimal (350–750 words)",
        "long": "Long (751–1000 words)",
        "very_long": "Very Long (>1000 words)"
    }.get(length_status, "Unknown")
    
    st.markdown(f"""
    <div class="format-status">
        <span>📏 Length</span>
        <span style="color: {length_color};">{length_label} ({word_count})</span>
    </div>
    """, unsafe_allow_html=True)
    
    bullets_status = "✅" if formatting["bullet_points"] else "❌"
    bullets_color = "#84fab0" if formatting["bullet_points"] else "#ff6b9d"
    bullets_text = "Present" if formatting["bullet_points"] else "Missing"
    st.markdown(f"""
    <div class="format-status">
        <span>{bullets_status} Bullet Points</span>
        <span style="color: {bullets_color};">
            {bullets_text}
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    dates_status = "✅" if formatting["dates"] else "❌"
    dates_color = "#84fab0" if formatting["dates"] else "#ff6b9d"
    dates_text = "Present" if formatting["dates"] else "Missing"
    st.markdown(f"""
    <div class="format-status">
        <span>{dates_status} Dates</span>
        <span style="color: {dates_color};">
            {dates_text}
        </span>
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# HERO SECTION
# ============================================================================

st.markdown('<div class="hero-title">📄 ResumeIQ</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">AI-Powered Resume-to-Job Match Analyzer with ATS Scoring</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

with col2:
    job_description = st.text_area(
        "Paste Job Description",
        height=150,
        placeholder="Paste the job description here..."
    )

# ============================================================================
# ANALYSIS LOGIC
# ============================================================================

if uploaded_file and job_description:
    with st.spinner("🔍 Analyzing resume..."):
        # Extract resume text
        resume_text, error = extract_text_from_pdf(uploaded_file)
        
        if error:
            st.error(f"❌ {error}")
            st.stop()
        
        # ===== EXISTING ANALYSIS (Unchanged) =====
        
        start_time = time.time()
        
        # Skill analysis
        resume_skills = extract_skills(resume_text)
        jd_skills = extract_skills(job_description)
        skill_analysis = analyze_skills(resume_skills, jd_skills)
        
        # Similarity calculation
        job_match_score, semantic_similarity = calculate_job_match_score(
            resume_text, 
            job_description, 
            skill_analysis["coverage_percent"]
        )
        interpretation, emoji, color = interpret_match(job_match_score)
        
        # LLM analysis
        summary = generate_summary(
            resume_text,
            job_description,
            skill_analysis["matching"],
            skill_analysis["missing"]
        )
        suggestions = generate_suggestions(
            resume_text,
            job_description,
            skill_analysis["missing"]
        )
        
        # ===== NEW: ATS ANALYSIS =====
        
        ats_analyzer = ATSAnalyzer()
        ats_report = ats_analyzer.generate_ats_report(resume_text, job_description)
        ats_recommendations = ats_analyzer.generate_ats_recommendations(resume_text, job_description)
        
        analysis_time = round(time.time() - start_time, 2)
        
        # Store results in session state
        st.session_state.results = {
            "resume_text": resume_text,
            "job_description": job_description,
            "resume_skills": resume_skills,
            "jd_skills": jd_skills,
            "skill_analysis": skill_analysis,
            "job_match_score": job_match_score,
            "semantic_similarity": semantic_similarity,
            "interpretation": interpretation,
            "emoji": emoji,
            "color": color,
            "summary": summary,
            "suggestions": suggestions,
            "ats_report": ats_report,
            "ats_recommendations": ats_recommendations,
            "word_count": len(resume_text.split()),
            "analysis_time": analysis_time,
        }

# ============================================================================
# RESULTS DASHBOARD
# ============================================================================

if st.session_state.results:
    results = st.session_state.results
    
    st.markdown("---")
    st.markdown("## 📊 Analysis Results")
    
    # ===== TOP ROW: Job Match Score + ATS Score =====
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="score-card">
            <div class="metric-label">Job Match Score</div>
            <div class="metric-value">{results['job_match_score']}/100</div>
            <div style="font-size: 1.2em; margin: 15px 0;">
                {results['emoji']} {results['interpretation']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        ats_score = results["ats_report"]["scores"]["ats_score"]
        ats_grade = results["ats_report"]["scores"]["grade"]

        grade_class = {
            "A+": "grade-a",
            "A": "grade-a",
            "B": "grade-b",
            "C": "grade-c",
            "D": "grade-d",
        }.get(ats_grade, "grade-f")
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="ats-card">
            <div class="metric-label">ATS Score</div>
            <div class="ats-metric-value">{ats_score}/100</div>
            <div style="font-size: 1.5em; margin: 15px 0;">
                <span class="{grade_class}">Grade {ats_grade}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ===== MIDDLE ROW: Score Breakdowns =====
    
    st.markdown("### 📈 Score Breakdown")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    scores = results["ats_report"]["scores"]
    
    with col1:
        st.metric("Contact Info", f"{scores['contact_score']}/20", delta=None)
    
    with col2:
        st.metric("Sections", f"{scores['section_score']}/30", delta=None)
    
    with col3:
        st.metric("Formatting", f"{scores['format_score']}/20", delta=None)
    
    with col4:
        st.metric("Keywords", f"{scores['keyword_score']}/30", delta=None)
    
    with col5:
        st.metric("Analysis Time", f"{results['analysis_time']}s")
    
    # ===== DETAILED ANALYSIS: 3-COLUMN LAYOUT =====
    
    col1, col2, col3 = st.columns(3)
    
    # LEFT COLUMN: Resume Health & Sections
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        display_resume_health(results["ats_report"]["contact_info"])
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("")
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        display_resume_sections(results["ats_report"]["sections"])
        
        missing = results["ats_report"]["missing_sections"]

        if missing:
            st.markdown("**Missing Sections**")

            for section in missing:
                st.markdown(f"❌ {section}")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # CENTER COLUMN: Summary, Skills, Formatting
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**📝 Resume-JD Fit Summary**")
        st.markdown(results['summary'])
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("")
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        display_formatting_status(results["ats_report"]["formatting"], results["word_count"])
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("")
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### ATS Keyword Analysis")

        keywords = results["ats_report"]["keywords"]

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Technical",
            keywords["technical_keywords"]
        )

        c2.metric(
            "Action Verbs",
            keywords["action_verbs"]
        )

        c3.metric(
            "Soft Skills",
            keywords["soft_keywords"]
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("")
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**🎯 Matching Skills**")
        for skill in sorted(results["skill_analysis"]["matching"]):
            st.markdown(f'<span class="skill-tag">{skill}</span>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # RIGHT COLUMN: Job Match Recommendations + ATS Recommendations
    with col3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**💡 Job Match Suggestions**")
        for i, suggestion in enumerate(results["suggestions"], 1):
            st.markdown(
                f'<div class="recommendation-item">{i}. {suggestion}</div>',
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("")
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**✅ ATS Improvement Tips**")
        severity_icons = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🔵"
        }

        for rec in results["ats_recommendations"]:
            icon = severity_icons.get(rec["severity"], "⚪")

            st.markdown(
                f"""
                <div class="ats-recommendation-item">
                    {icon} {rec["message"]}
                </div>
                """,
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)
    
    # ===== MISSING SKILLS SECTION =====
    
    st.markdown("---")
    st.markdown("### 🔍 Missing Skills to Add")
    
    if results["skill_analysis"]["missing"]:
        col_missing = st.columns(min(5, len(results["skill_analysis"]["missing"])))
        for i, skill in enumerate(sorted(results["skill_analysis"]["missing"])[:5]):
            with col_missing[i % len(col_missing)]:
                st.markdown(
                    f'<span class="missing-skill-tag">{skill}</span>',
                    unsafe_allow_html=True
                )
    else:
        st.markdown("✅ Great! All required skills are present in your resume.")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown('<div class="footer">ResumeIQ v1.0.0 | AI Resume Analyzer + ATS Scoring</div>', unsafe_allow_html=True)