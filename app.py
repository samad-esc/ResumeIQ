import streamlit as st
from utils.pdf_parser import extract_text_from_pdf
from utils.skill_analyzer import extract_skills, analyze_skills
from utils.similarity import calculate_job_match_score, interpret_match
from utils.llm import generate_summary, generate_suggestions

st.set_page_config(page_title="ResumeIQ", page_icon="🎯", layout="wide")

# Custom CSS
st.markdown("""
<style>

/* Main App */
.stApp {
    background: #0f172a;
}

/* Metric Cards */
.metric-card {
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    padding: 20px;
    border-radius: 16px;
    text-align: center;
    color: white;
    box-shadow: 0 8px 25px rgba(0,0,0,0.25);
}

/* Summary Box */
.info-box {
    background: rgba(59, 130, 246, 0.12);
    border: 1px solid rgba(59, 130, 246, 0.35);
    color: #e2e8f0;
    padding: 18px;
    border-radius: 12px;
    margin-top: 10px;
    font-size: 15px;
    line-height: 1.6;
}

/* Matching Skills */
.success-box {
    background: rgba(34, 197, 94, 0.12);
    border-left: 5px solid #22c55e;
    color: #f8fafc;
    padding: 14px;
    border-radius: 10px;
    margin-bottom: 10px;
    transition: 0.2s;
}

.success-box:hover {
    transform: translateX(5px);
}

/* Missing Skills */
.warning-box {
    background: rgba(245, 158, 11, 0.12);
    border-left: 5px solid #f59e0b;
    color: #f8fafc;
    padding: 14px;
    border-radius: 10px;
    margin-bottom: 10px;
    transition: 0.2s;
}

.warning-box:hover {
    transform: translateX(5px);
}

/* Metrics */
[data-testid="stMetric"] {
    background: #111827;
    padding: 15px;
    border-radius: 14px;
    border: 1px solid #1f2937;
    text-align: center;
}

[data-testid="stMetricValue"] {
    font-size: 32px;
    color: #60a5fa;
}

[data-testid="stMetricLabel"] {
    color: #cbd5e1;
}

/* Buttons */
.stButton button {
    border-radius: 12px;
    height: 50px;
    font-weight: 600;
}

/* File Uploader */
[data-testid="stFileUploader"] {
    border-radius: 12px;
    border: 1px solid #334155;
    padding: 10px;
}

/* Text Area */
textarea {
    border-radius: 12px !important;
}

/* Section Headers */
h1, h2, h3 {
    font-weight: 700;
}

/* Score Card */
.score-card {
    background: linear-gradient(135deg,#059669,#10b981);
    padding: 20px;
    border-radius: 18px;
    text-align: center;
    color: white;
}

</style>
""", unsafe_allow_html=True)

st.title("ResumeIQ")
st.markdown("Resume-to-Job Match Analysis")
st.markdown("Powered by AI embeddings and semantic analysis")

st.markdown("---")

# Initialize session state
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
    st.session_state.results = {}

# TWO COLUMN LAYOUT
col1, col2 = st.columns(2)

with col1:
    st.subheader("Resume Upload")
    uploaded_file = st.file_uploader("Select PDF", type="pdf", key="resume_upload")
    if uploaded_file:
        st.caption(f"✓ {uploaded_file.name}")

with col2:
    st.subheader("Job Description")
    jd_text = st.text_area("Paste job description", height=120, placeholder="Senior Software Engineer...")

# ANALYZE
if st.button("Analyze Match", use_container_width=True, type="primary"):
    if not uploaded_file:
        st.error("Upload a resume to continue")
    elif not jd_text or len(jd_text) < 50:
        st.error("Paste a valid job description")
    else:
        with st.spinner("Analyzing resume and job description..."):
            resume_text, error = extract_text_from_pdf(uploaded_file)
            
            if error:
                st.error(error)
            else:
                resume_skills = extract_skills(resume_text)
                jd_skills = extract_skills(jd_text)
                skill_analysis = analyze_skills(resume_skills, jd_skills)
                job_match_score = calculate_job_match_score(
                    resume_text, jd_text, skill_analysis["coverage_percent"]
                )
                
                st.session_state.results = {
                    "resume_text": resume_text,
                    "jd_text": jd_text,
                    "resume_skills": resume_skills,
                    "jd_skills": jd_skills,
                    "skill_analysis": skill_analysis,
                    "job_match_score": job_match_score,
                }
                st.session_state.analysis_done = True

# RESULTS
if st.session_state.analysis_done:
    results = st.session_state.results
    skill_analysis = results["skill_analysis"]
    score = results["job_match_score"]
    interpretation, emoji, color = interpret_match(score)
    
    st.markdown("---")
    
    # METRICS ROW
    st.subheader("Overview")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Resume Skills", skill_analysis["resume_skill_count"])
    m2.metric("Job Skills", skill_analysis["total_jd_skills"])
    m3.metric("Matched", skill_analysis["matched_count"])
    m4.metric("Missing", len(skill_analysis["missing"]))
    
    st.markdown("---")
    
    # MATCH SCORE
    st.subheader("Job Match Score")
    score_col, bar_col = st.columns([1, 3])
    
    with score_col:
        st.markdown(f"<h1 style='color: {color}; margin: 0;'>{score}%</h1>", unsafe_allow_html=True)
        st.caption(interpretation)
    
    with bar_col:
        st.progress(score / 100)
        st.caption(f"Semantic similarity (60%) + Skill coverage (40%)")
    
    st.markdown("---")
    
    # SUMMARY
    st.subheader("Summary")
    summary = generate_summary(
        results["resume_text"],
        results["jd_text"],
        skill_analysis["matching"],
        skill_analysis["missing"]
    )
    st.markdown(f'<div class="info-box">{summary}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # SKILLS
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Matching Skills")
        if skill_analysis["matching"]:
            for skill in skill_analysis["matching"]:
                st.markdown(f'<div class="success-box">✓ {skill.capitalize()}</div>', unsafe_allow_html=True)
        else:
            st.info("No matching skills found")
    
    with col2:
        st.subheader("Missing Skills")
        if skill_analysis["missing"]:
            for skill in skill_analysis["missing"][:8]:
                st.markdown(f'<div class="warning-box">• {skill.capitalize()}</div>', unsafe_allow_html=True)
            if len(skill_analysis["missing"]) > 8:
                st.caption(f"+{len(skill_analysis['missing']) - 8} more missing skills")
        else:
            st.success("All required skills present")
    
    st.markdown("---")
    
    # SUGGESTIONS
    st.subheader("Improvement Suggestions")
    suggestions = generate_suggestions(
        results["resume_text"],
        results["jd_text"],
        skill_analysis["missing"]
    )
    
    for i, suggestion in enumerate(suggestions, 1):
        st.write(f"**{i}.** {suggestion}")
    
    st.markdown("---")
    
    if st.button("Analyze Another", use_container_width=True):
        st.session_state.analysis_done = False
        st.rerun()

st.markdown("---")
st.caption("ResumeIQ • Resume-to-Job Fit Analysis • Powered by AI")