# Just check imports work
from utils.pdf_parser import extract_text_from_pdf
print("✓ PDF parser imported successfully")

from utils.skill_analyzer import extract_skills, analyze_skills

# Test extraction
test_text = "I know Python, React, and Docker"
skills = extract_skills(test_text)
print(f"Found skills: {skills}")

# Test analysis
resume = ["python", "react"]
jd = ["python", "react", "docker", "kubernetes"]
result = analyze_skills(resume, jd)
print(f"Coverage: {result['coverage_percent']}%")
print(f"Matched: {result['matched_count']} / {result['total_jd_skills']}")

from utils.similarity import calculate_job_match_score, interpret_match

resume = "I have 5 years experience with Python, React, and Machine Learning"
jd = "Looking for Python developer with React experience and machine learning skills"
skill_coverage = 75  # 75% skill match

score = calculate_job_match_score(resume, jd, skill_coverage)
interpretation, emoji, color = interpret_match(score)

print(f"Job Match Score: {score}/100 {emoji}")
print(f"Interpretation: {interpretation}")

from utils.llm import generate_summary, generate_suggestions

resume = "5 years Python experience, worked on ML projects"
jd = "Senior Python engineer needed with ML and Docker experience"
matching = ["python", "machine learning"]
missing = ["docker", "kubernetes"]

print("\n--- Testing LLM ---")
summary = generate_summary(resume, jd, matching, missing)
print(f"Summary:\n{summary}\n")

suggestions = generate_suggestions(resume, jd, missing)
print("Suggestions:")
for i, s in enumerate(suggestions, 1):
    print(f"{i}. {s}")
    