# ResumeIQ Phase 2 – Keyword Density Analyzer & Job Optimization Engine

**Project:** ResumeIQ – ATS-Aware Resume Intelligence Platform

Current Status:

* ✅ Phase 0 Complete
* ✅ Phase 1 Complete
* ✅ Phase 1.2 Complete

We are now starting Phase 2.

---

# IMPORTANT

Do **NOT** start writing code immediately.

The codebase has been manually modified after the previous implementation.

Before making any changes, review the current project files so your implementation matches the latest architecture.

---

# Step 1 – Review Existing Codebase

Before implementing anything, ask me to provide the latest versions of the files you need.

At minimum, review:

```text
app.py
utils/skill_analyzer.py
utils/ats_analyzer.py
utils/similarity.py
utils/llm.py
```

If additional files are required, ask for them before proceeding.

Do **not** assume the project is identical to previous conversations.

Review the current implementation first.

After reviewing, summarize:

* Current architecture
* Existing data flow
* Existing ATS integration
* Existing session state structure

Only then continue.

---

# Phase 2 Goal

ResumeIQ currently tells users:

* Match Score
* ATS Score
* Missing Skills

Phase 2 should answer:

> "Exactly which keywords should I improve for THIS specific job?"

This phase transforms ResumeIQ from a resume analyzer into a resume optimization platform.

---

# Design Principles

Do NOT redesign the application.

Do NOT rewrite previous modules.

Do NOT break the existing architecture.

Follow the existing coding style.

Reuse existing utilities whenever possible.

Build incrementally.

Stop after each major milestone for review.

---

# New Module

Create:

```text
utils/keyword_analyzer.py
```

Keep it completely independent from the UI.

No Streamlit code.

No CSS.

Pure backend logic.

---

# Features

## 1. Keyword Extraction

Extract keywords from:

* Resume
* Job Description

Reuse existing skill extraction where appropriate.

Also identify:

* Multi-word skills
* Technical tools
* Frameworks
* Libraries
* Cloud platforms

Avoid duplicate logic.

---

## 2. Keyword Frequency Analysis

Calculate frequency for every keyword.

Example:

| Keyword | Resume | JD |
| ------- | -----: | -: |
| Python  |      2 |  9 |
| Docker  |      0 |  4 |
| AWS     |      1 |  5 |

Use case-insensitive matching.

Prefer regex word boundaries.

Avoid substring matches such as:

* Java
* JavaScript

---

## 3. Keyword Gap Analysis

Calculate:

Resume Count

Job Count

Difference

Coverage

Example

```text
Python

Resume: 2

Job: 8

Gap: +6
```

---

## 4. Priority Ranking

Rank missing keywords using:

* Frequency in JD
* Whether keyword exists in resume
* Importance

Return:

```python
[
    {
        "keyword": "Docker",
        "resume": 0,
        "job": 6,
        "gap": 6,
        "priority": "High"
    }
]
```

---

## 5. Optimization Opportunities

Generate actionable insights.

Example:

```text
Increase Python keyword usage.

Mention Docker experience.

Add Kubernetes to Projects.

Highlight AWS deployment experience.
```

Do not use the LLM.

This should be deterministic.

---

## 6. Resume Keyword Statistics

Return:

* Total Resume Keywords
* Total JD Keywords
* Matched Keywords
* Missing Keywords
* Coverage %
* Top Missing Keywords
* Top Overused Keywords

---

# Output API

Create one public method.

Example:

```python
generate_keyword_report(
    resume_text,
    job_description
)
```

Return a structured dictionary.

Example:

```python
{
    "statistics": {...},
    "keyword_table": [...],
    "top_missing": [...],
    "top_present": [...],
    "recommendations": [...]
}
```

Keep the output UI-friendly.

---

# Architecture Requirements

* Modular
* Typed
* Documented
* No duplicated logic
* Reuse existing skill extraction
* Reuse existing caching
* Production-ready

---

# Do NOT Integrate Yet

Do NOT modify:

* app.py
* ATS UI
* CSS

Phase 2 is backend only.

After the backend is complete and reviewed, we will integrate it into the dashboard as Phase 2.1.

---

# Deliverables

Return only:

1. Architecture review of the current codebase.
2. Any assumptions or compatibility issues.
3. Complete `utils/keyword_analyzer.py`.
4. Brief explanation of the implementation.

Then stop.

Wait for my approval before integrating the feature into the UI.

I also have a recommendation for the roadmap itself.

Instead of making Phase 2 just a "Keyword Density Analyzer," I'd treat it as a Job Optimization Engine. That gives you room to expand it later with:

Keyword density analysis
Keyword gap analysis
Priority ranking
Resume optimization suggestions
Job-specific tailoring