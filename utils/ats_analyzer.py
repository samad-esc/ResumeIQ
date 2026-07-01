"""
ATS Analyzer Module

Deterministic ATS resume scoring engine that evaluates resume quality
based on structure, sections, formatting, and keyword coverage.

Does NOT require LLM or API calls. Rule-based analysis only.
"""

import json
import re
from typing import Dict, List, Set, Tuple, Optional, Any
from utils.skill_analyzer import load_skills
from typing import Dict, List



class ATSAnalyzer:
    """
    Analyzes resume quality from an ATS (Applicant Tracking System) perspective.
    
    Scoring breakdown:
    - Contact Information: 20 points
    - Resume Sections: 30 points
    - Formatting: 20 points
    - Keyword Coverage: 30 points
    - Total: 100 points
    """

    # Define section keywords with extended aliases for Indian & international resumes
    SECTION_KEYWORDS = {
        "Education": [
            "education", "academic", "degree", "university", "college", "school",
            "b.tech", "bachelor", "masters", "m.tech", "bca", "bsc", "ba", "be",
            "engineering", "studies", "qualification", "cgpa", "gpa"
        ],
        "Skills": [
            "skills", "technical skills", "competencies", "expertise", "abilities",
            "core competencies", "technical competencies", "programming skills"
        ],
        "Projects": [
            "projects", "portfolio", "personal projects", "side projects",
            "academic projects", "project work", "github projects"
        ],
        "Experience": [
            "experience", "work experience", "employment", "professional",
            "internship", "internships", "work history", "professional experience",
            "career", "job history", "professional journey"
        ],
        "Certifications": [
            "certifications", "certificates", "licenses", "certifications & licenses",
            "professional certifications", "courses", "training", "credentials"
        ],
    }


    def __init__(self, skills_json_path: Optional[str] = None):
        """
        Initialize the ATS Analyzer.
        
        Args:
            skills_json_path: Optional path to skills.json for keyword extraction.
                            If not provided, uses DEFAULT_KEYWORDS.
        """
        self._skills_cache: Optional[Dict] = None

    def check_contact_information(self, resume_text: str) -> Dict[str, bool]:
        """
        Detect contact information in resume.
        Supports Indian, US, UK, and other international phone formats.

        Args:
            resume_text: Full resume text

        Returns:
            Dictionary with boolean flags for each contact type:
            {
                "email": bool,
                "phone": bool,
                "linkedin": bool,
                "github": bool
            }
        """
        text_lower = resume_text.lower()

        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        has_email = bool(re.search(email_pattern, resume_text))

        # Phone pattern: supports multiple formats
        # - US: (123) 456-7890, 123-456-7890, +1 123 456 7890
        # - India: +91-9876543210, +919876543210, 9876543210
        # - International: +44 20 7946 0958, +33 1 42 34 56 78
        phone_pattern = r'''
            (?:
                # US/International with country code
                \+?1[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}|
                # India: +91-9876543210 or 9876543210
                (?:\+91[-.\s]?)?[6-9]\d{9}|
                # Generic international: +CC pattern
                \+[1-9]\d{1,2}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}|
                # Standard 10-digit or parentheses format
                \(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}
            )
        '''
        has_phone = bool(re.search(phone_pattern, resume_text, re.VERBOSE))

        # LinkedIn URL
        linkedin_pattern = r'linkedin\.com/in/|linkedin\.com/company/'
        has_linkedin = bool(re.search(linkedin_pattern, text_lower))

        # GitHub URL
        github_pattern = r'github\.com/|github\.io'
        has_github = bool(re.search(github_pattern, text_lower))

        return {
            "email": has_email,
            "phone": has_phone,
            "linkedin": has_linkedin,
            "github": has_github,
        }

    def check_resume_sections(self, resume_text: str) -> Dict[str, bool]:
        """
        Detect presence of standard resume sections.

        Args:
            resume_text: Full resume text

        Returns:
            Dictionary with boolean flags for each section:
            {
                "Education": bool,
                "Skills": bool,
                "Projects": bool,
                "Experience": bool,
                "Certifications": bool
            }
        """
        text_lower = resume_text.lower()
        sections_found = {}

        for section, keywords in self.SECTION_KEYWORDS.items():
            # Check if any keyword matches at word boundary
            found = False
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, text_lower):
                    found = True
                    break
            sections_found[section] = found

        return sections_found

    def check_formatting(self, resume_text: str) -> Dict[str, Any]:
        """
        Evaluate resume formatting quality.
        Optimal length: 250-700 words for most resumes.

        Args:
            resume_text: Full resume text

        Returns:
            Dictionary with formatting metrics:
            {
                "length": "optimal" | "short" | "long",
                "bullet_points": bool,
                "dates": bool
            }
        """
        # Word count analysis
        word_count = len(resume_text.split())

        if word_count < 200:
            length_status = "very_short"
        elif word_count < 350:
            length_status = "short"
        elif word_count <= 750:
            length_status = "optimal"
        elif word_count <= 1000:
            length_status = "long"
        else:
            length_status = "very_long"

        # Bullet points detection
        bullet_patterns = [r'^\s*[-•*]\s', r'^\s*\d+\.\s']
        has_bullets = any(
            re.search(pattern, line)
            for pattern in bullet_patterns
            for line in resume_text.split('\n')
        )

        # Date detection (YYYY, MM/YYYY, etc.)
        date_pattern = r'\b(19|20)\d{2}\b|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s-]?\d{4}'
        has_dates = bool(re.search(date_pattern, resume_text))

        return {
            "length": length_status,
            "bullet_points": has_bullets,
            "dates": has_dates,
        }


    def calculate_contact_score(self, contact_info: Dict[str, bool]) -> int:
        """
        Calculate contact information score.

        Scoring:
        - Email: 5 points
        - Phone: 5 points
        - LinkedIn: 5 points
        - GitHub: 5 points
        - Total: 20 points

        Args:
            contact_info: Output from check_contact_information()

        Returns:
            Score out of 20
        """
        score = 0
        score += 5 if contact_info["email"] else 0
        score += 5 if contact_info["phone"] else 0
        score += 5 if contact_info["linkedin"] else 0
        score += 5 if contact_info["github"] else 0
        return score

    def calculate_section_score(self, sections: Dict[str, bool]) -> int:
        """
        Calculate resume sections score.

        Scoring:
        - 6 points per section present (max 30 points for 5 sections)
        
        Args:
            sections: Output from check_resume_sections()

        Returns:
            Score out of 30
        """
        present_sections = sum(1 for present in sections.values() if present)
        return min(present_sections * 6, 30)

    def calculate_formatting_score(self, formatting: Dict[str, Any]) -> int:
        """
        Calculate formatting quality score.

        Scoring:
        - Length (optimal): 8 points
        - Bullet points: 6 points
        - Dates present: 6 points
        - Total: 20 points

        Args:
            formatting: Output from check_formatting()

        Returns:
            Score out of 20
        """
        score = 0

        # Length score: optimal gets full points, short/long gets partial
        if formatting["length"] == "optimal":
            score += 8
        elif formatting["length"] in ["short", "long"]:
            score += 6
        else:  # very_short or very_long
            score += 3

        # Bullet points
        score += 6 if formatting["bullet_points"] else 0

        # Dates
        score += 6 if formatting["dates"] else 0

        return score

    def analyze_keyword_coverage(
        self, resume_text: str, jd_text: str = None
    ) -> Dict[str, int]:
        """
        Analyze keyword coverage in resume vs job description.

        Extracts technical skills, action verbs, and soft skills
        to score keyword relevance for ATS.

        Args:
            resume_text: Full resume text
            jd_text: Job description text (optional)

        Returns:
            Dictionary with keyword analysis:
            {
                "coverage_score": int (0-30),
                "technical_keywords": int,
                "action_verbs": int,
                "soft_keywords": int,
            }
        """
        text_lower = resume_text.lower()

        # Action verbs that show impact
        action_verbs = {
            "led", "managed", "directed", "developed", "created", "built",
            "implemented", "deployed", "optimized", "improved", "achieved",
            "analyzed", "solved", "designed", "automated", "launched",
            "coordinated", "collaborated", "increased", "reduced", "enhanced"
        }

        # Soft skills keywords
        soft_skills = {
            "communication", "teamwork", "leadership", "problem solving",
            "analytical", "strategic", "management", "planning", "organization",
            "initiative", "creativity", "innovation", "collaboration", "agile"
        }

        # Load skills from cache
        try:
            technical_keywords = load_skills()
        except:
            technical_keywords = set()

        # Count keyword occurrences
        technical_count = 0
        action_verb_count = 0
        soft_skill_count = 0

        # Count technical skills
        for skill in technical_keywords:
            pattern = r"\b" + re.escape(skill) + r"\b"
            matches = re.findall(pattern, text_lower)
            technical_count += len(matches)

        # Count action verbs
        for verb in action_verbs:
            pattern = r"\b" + re.escape(verb) + r"\b"
            matches = re.findall(pattern, text_lower)
            action_verb_count += len(matches)

        # Count soft skills
        for skill in soft_skills:
            pattern = r"\b" + re.escape(skill) + r"\b"
            matches = re.findall(pattern, text_lower)
            soft_skill_count += len(matches)

        # Calculate coverage score (0-30 points)
        # Technical skills are most important for ATS
        coverage_score = 0

        if technical_count > 0:
            coverage_score += min(15, technical_count * 2)  # Up to 15 points
        if action_verb_count > 0:
            coverage_score += min(10, action_verb_count)   # Up to 10 points
        if soft_skill_count > 0:
            coverage_score += min(5, soft_skill_count)     # Up to 5 points

        coverage_score = min(30, coverage_score)

        return {
            "coverage_score": coverage_score,
            "technical_keywords": technical_count,
            "action_verbs": action_verb_count,
            "soft_keywords": soft_skill_count,
        }

    def calculate_ats_score(
        self, resume_text: str, jd_text: str = None
    ) -> Dict[str, int]:
        """
        Calculate complete ATS score with all component breakdowns.

        Weighting:
        - Contact Information: 20 points
        - Resume Sections: 30 points
        - Formatting: 20 points
        - Keyword Coverage: 30 points
        - Total: 100 points

        Args:
            resume_text: Full resume text
            jd_text: Job description text (optional, for keyword matching)

        Returns:
            Dictionary with complete scoring breakdown:
            {
                "ats_score": int (0-100),
                "contact_score": int (0-20),
                "section_score": int (0-30),
                "format_score": int (0-20),
                "keyword_score": int (0-30)
            }
        """
        # Run all analyses
        contact_info = self.check_contact_information(resume_text)
        sections = self.check_resume_sections(resume_text)
        formatting = self.check_formatting(resume_text)
        keywords = self.analyze_keyword_coverage(resume_text, jd_text)

        # Calculate component scores
        contact_score = self.calculate_contact_score(contact_info)
        section_score = self.calculate_section_score(sections)
        format_score = self.calculate_formatting_score(formatting)
        keyword_score = keywords["coverage_score"]

        # Total ATS score
        ats_score = contact_score + section_score + format_score + keyword_score

        # Calculate grade (A+, A, B, C, D, F)
        if ats_score >= 95:
            grade = "A+"
        elif ats_score >= 90:
            grade = "A"
        elif ats_score >= 80:
            grade = "B"
        elif ats_score >= 70:
            grade = "C"
        elif ats_score >= 60:
            grade = "D"
        else:
            grade = "F"

        return {
            "ats_score": ats_score,
            "contact_score": contact_score,
            "section_score": section_score,
            "format_score": format_score,
            "keyword_score": keyword_score,
            "grade": grade,
        }

    def generate_ats_report(
        self, resume_text: str, jd_text: str = None
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive ATS report with scores and details.

        Args:
            resume_text: Full resume text
            jd_text: Job description text (optional)

        Returns:
            Dictionary containing:
            {
                "scores": {...},
                "contact_info": {...},
                "sections": {...},
                "formatting": {...},
                "keywords": {...}
            }
        """
        contact_info = self.check_contact_information(resume_text)
        sections = self.check_resume_sections(resume_text)
        formatting = self.check_formatting(resume_text)
        keywords = self.analyze_keyword_coverage(resume_text, jd_text)
        scores = self.calculate_ats_score(resume_text, jd_text)
        missing_sections = [
            section
            for section, present in sections.items()
            if not present
        ]

        return {
            "scores": scores,
            "contact_info": contact_info,
            "sections": sections,
            "missing_sections": missing_sections,
            "formatting": formatting,
            "keywords": keywords,
        }


    def generate_ats_recommendations(
        self, resume_text: str, jd_text: str = None
    ) -> List[Dict[str, str]]:
        """
        Generate actionable ATS improvement recommendations.

        Returns:
            List of recommendation dictionaries:
            [
                {
                    "severity": "high",
                    "message": "Add your email address to the top of your resume."
                },
                ...
            ]
        """
        recommendations: List[Dict[str, str]] = []

        # Get all analysis data
        contact_info = self.check_contact_information(resume_text)
        sections = self.check_resume_sections(resume_text)
        formatting = self.check_formatting(resume_text)
        keywords = self.analyze_keyword_coverage(resume_text, jd_text)
        scores = self.calculate_ats_score(resume_text, jd_text)

        # === CONTACT INFORMATION RECOMMENDATIONS ===
        if not contact_info["email"]:
            recommendations.append({
                "severity": "high",
                "message": "Add your email address to the top of your resume."
            })

        if not contact_info["phone"]:
            recommendations.append({
                "severity": "high",
                "message": "Include your phone number in the contact information section."
            })

        if not contact_info["linkedin"]:
            recommendations.append({
                "severity": "medium",
                "message": "Add your LinkedIn profile URL to improve discoverability."
            })

        if not contact_info["github"]:
            recommendations.append({
                "severity": "medium",
                "message": "Add your GitHub profile URL if you have coding projects to showcase."
            })

        # === MISSING SECTIONS RECOMMENDATIONS ===
        missing_sections = [
            section for section, present in sections.items() if not present
        ]

        section_priorities = {
            "Experience": {
                "severity": "high",
                "message": "Add a Work Experience or Employment section with your previous roles."
            },
            "Education": {
                "severity": "medium",
                "message": "Add an Education section with your degrees and institutions."
            },
            "Skills": {
                "severity": "high",
                "message": "Add a dedicated Skills section listing your technical and soft skills."
            },
            "Projects": {
                "severity": "medium",
                "message": "Include a Projects section to showcase your work and accomplishments."
            },
            "Certifications": {
                "severity": "medium",
                "message": "Add relevant certifications to increase your credibility."
            },
        }

        for section in missing_sections:
            if section in section_priorities:
                recommendations.append(section_priorities[section])

        # === FORMATTING RECOMMENDATIONS ===
        if formatting["length"] == "very_short":
            recommendations.append({
                "severity": "high",
                "message": "Your resume is very short. Expand it with more achievements, projects, and relevant experience."
            })

        elif formatting["length"] == "short":
            recommendations.append({
                "severity": "medium",
                "message": "Your resume is slightly short. Aim for 350–750 words to provide sufficient detail."
            })

        elif formatting["length"] in ("long", "very_long"):
            recommendations.append({
                "severity": "medium",
                "message": "Your resume is too long. Keep it concise and ideally within two pages."
            })

        if not formatting["bullet_points"]:
            recommendations.append({
                "severity": "medium",
                "message": "Use bullet points to make your achievements more scannable for ATS systems."
            })

        if not formatting["dates"]:
            recommendations.append({
                "severity": "medium",
                "message": "Include dates for your education and work experience in a consistent format."
            })

        # === KEYWORD COVERAGE RECOMMENDATIONS ===
        if keywords["technical_keywords"] < 3:
            recommendations.append({
                "severity": "low",
                "message": "Add more technical keywords relevant to your field (e.g., programming languages, frameworks)."
            })

        if keywords["action_verbs"] < 5:
            recommendations.append({
                "severity": "low",
                "message": "Use more action verbs to describe your achievements (e.g., 'Led', 'Designed', 'Implemented')."
            })

        if keywords["soft_keywords"] < 3:
            recommendations.append({
                "severity": "low",
                "message": "Include soft skill keywords like 'leadership', 'communication', or 'teamwork'."
            })

        if keywords["coverage_score"] < 15:
            recommendations.append({
                "severity": "low",
                "message": "Increase keyword density by incorporating industry-specific terminology throughout your resume."
            })

        return recommendations