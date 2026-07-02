"""
Resume Tailoring Engine - Phase 3

Provides section-aware, actionable recommendations to optimize resume
for a specific job description based on keyword gaps, ATS analysis, and
skill alignment.

Deterministic, rule-based analysis. No LLM calls. No Streamlit imports.
Reuses outputs from ATS Analyzer, Keyword Analyzer, and Skill Analyzer.
"""

import re
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import Counter


# ============================================================================
# RESUME SECTIONS MAPPING
# ============================================================================

RESUME_SECTIONS = {
    "Skills": {
        "primary_use": "List technical skills, tools, and competencies",
        "ideal_for": ["Technical Skill", "Industry Term"],
    },
    "Projects": {
        "primary_use": "Showcase application of skills in real projects",
        "ideal_for": ["Technical Skill", "Industry Term", "Action Verb"],
    },
    "Experience": {
        "primary_use": "Demonstrate impact and responsibilities using strong verbs",
        "ideal_for": ["Action Verb", "Technical Skill"],
    },
    "Education": {
        "primary_use": "Relevant degree and coursework highlights",
        "ideal_for": ["Technical Skill"],
    },
    "Professional Summary": {
        "primary_use": "Brief overview highlighting key strengths and fit",
        "ideal_for": ["Soft Skill", "Technical Skill", "Action Verb"],
    },
}

TAILORING_IMPACT_MAP = {
    "High": {
        "Technical Skill": 10,
        "Industry Term": 8,
        "Action Verb": 6,
        "Soft Skill": 3,
    },
    "Medium": {
        "Technical Skill": 6,
        "Industry Term": 5,
        "Action Verb": 4,
        "Soft Skill": 2,
    },
    "Low": {
        "Technical Skill": 3,
        "Industry Term": 2,
        "Action Verb": 2,
        "Soft Skill": 1,
    },
}


# ============================================================================
# RESUME TAILOR CLASS
# ============================================================================

class ResumeTailor:
    """
    Provides section-aware resume optimization recommendations.

    Takes outputs from ATS Analyzer, Keyword Analyzer, and existing resume
    to generate targeted tailoring suggestions for each resume section.

    Features:
    - Section-aware recommendations
    - Priority ranking (High/Medium/Low)
    - Reuses keyword gap analysis
    - Deterministic scoring
    """

    def __init__(self):
        """Initialize the Resume Tailor."""
        pass

    # ========================================================================
    # 1. SECTION AVAILABILITY ANALYSIS
    # ========================================================================

    def analyze_section_coverage(
        self,
        ats_report: Dict[str, Any],
        keyword_report: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Analyze which resume sections are present and their gaps.

        Args:
            ats_report: Output from ATSAnalyzer.generate_ats_report()
            keyword_report: Output from KeywordAnalyzer.generate_keyword_report()

        Returns:
            Dictionary with section analysis:
            {
                "present_sections": [section_names],
                "missing_sections": [section_names],
                "section_priority": {section: priority_score},
            }
        """
        sections = ats_report["sections"]
        present = [s for s, present in sections.items() if present]
        missing = ats_report.get("missing_sections", [])

        # Calculate section priority based on keyword coverage gaps
        section_priority = {}
        gap_analysis = keyword_report["gap_analysis"]

        # Skills section priority: based on technical keyword gaps
        technical_gaps = len([k for k in gap_analysis["missing"] if True])
        section_priority["Skills"] = min(technical_gaps * 2, 100)

        # Projects section priority: high if missing industry-specific keywords
        industry_gaps = technical_gaps
        section_priority["Projects"] = min(industry_gaps * 1.5, 80)

        # Experience section priority: based on action verb and skill gaps
        underrep_count = len(gap_analysis["underrepresented"])
        section_priority["Experience"] = min(underrep_count * 2, 90)

        # Education section priority: lower unless missing educational context
        section_priority["Education"] = 30

        # Professional Summary priority: if many gaps exist
        if technical_gaps > 5:
            section_priority["Professional Summary"] = 60
        else:
            section_priority["Professional Summary"] = 20

        return {
            "present_sections": present,
            "missing_sections": missing,
            "section_priority": section_priority,
        }

    # ========================================================================
    # 2. SECTION-AWARE RECOMMENDATIONS
    # ========================================================================

    def generate_section_recommendations(
        self,
        keyword_report: Dict[str, Any],
        section_coverage: Dict[str, Any],
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate tailored recommendations for each resume section.

        Args:
            keyword_report: Output from KeywordAnalyzer.generate_keyword_report()
            section_coverage: Output from analyze_section_coverage()

        Returns:
            Dictionary with recommendations per section:
            {
                "Skills": [recommendation_dicts],
                "Projects": [recommendation_dicts],
                "Experience": [recommendation_dicts],
                "Education": [recommendation_dicts],
                "Professional Summary": [recommendation_dicts],
            }
        """
        recommendations = {
            "Skills": [],
            "Projects": [],
            "Experience": [],
            "Education": [],
            "Professional Summary": [],
        }

        ranked_keywords = keyword_report["ranked_keywords"]
        gap_analysis = keyword_report["gap_analysis"]

        # ===== SKILLS SECTION =====
        # Focus on Technical Skills and Industry Terms that are missing
        for keyword in ranked_keywords[:15]:  # Top 15 priorities
            if keyword["priority"] == "High" and keyword["category"] == "Technical Skill":
                recommendations["Skills"].append({
                    "keyword": keyword["keyword"],
                    "action": f"Add {keyword['keyword']} to your skills list",
                    "reason": f"Mentioned {keyword['jd_count']} times in job description",
                    "priority": keyword["priority"],
                    "category": keyword["category"],
                    "impact_score": 10,
                })

        # ===== PROJECTS SECTION =====
        # Focus on demonstrating technical skills with concrete examples
        for keyword in ranked_keywords:
            if keyword["priority"] in ["High", "Medium"] and keyword["category"] in [
                "Technical Skill",
                "Industry Term",
            ]:
                recommendations["Projects"].append({
                    "keyword": keyword["keyword"],
                    "action": f"Highlight a project using {keyword['keyword']}",
                    "reason": f"Demonstrates hands-on experience with {keyword['keyword']}",
                    "priority": keyword["priority"],
                    "category": keyword["category"],
                    "impact_score": 8,
                })
                if len(recommendations["Projects"]) >= 5:
                    break

        # ===== EXPERIENCE SECTION =====
        # Focus on action verbs and underrepresented keywords
        action_verbs = [k for k in ranked_keywords if k["category"] == "Action Verb"]
        for verb in action_verbs[:5]:
            if verb["priority"] in ["High", "Medium"]:
                recommendations["Experience"].append({
                    "keyword": verb["keyword"],
                    "action": f"Use '{verb['keyword']}' to describe your achievements",
                    "reason": f"Strong action verb; used in {verb['jd_count']} job requirement instances",
                    "priority": verb["priority"],
                    "category": verb["category"],
                    "impact_score": 6,
                })

        # Add underrepresented technical keywords to Experience
        for kw in gap_analysis["underrepresented"][:3]:
            keyword = kw["keyword"]
            gap = kw["gap"]
            recommendations["Experience"].append({
                "keyword": keyword,
                "action": f"Mention {keyword} more in your experience descriptions",
                "reason": f"Currently mentioned {kw['resume_count']} times, but job description emphasizes it {kw['jd_count']} times",
                "priority": "High" if gap > 3 else "Medium",
                "category": "Technical Skill",
                "impact_score": 7,
            })

        # ===== EDUCATION SECTION =====
        # Suggest highlighting relevant education and certifications
        education_keywords = [k for k in ranked_keywords if "degree" in k["keyword"].lower()
                             or "certification" in k["keyword"].lower()]
        if education_keywords:
            for kw in education_keywords:
                recommendations["Education"].append({
                    "keyword": kw["keyword"],
                    "action": f"Highlight relevant {kw['keyword']} education",
                    "reason": f"Job description mentions {kw['keyword']}",
                    "priority": kw["priority"],
                    "category": kw["category"],
                    "impact_score": 4,
                })

        # Generic education advice if many gaps exist
        if len(gap_analysis["missing"]) > 10:
            recommendations["Education"].append({
                "keyword": "Relevant Coursework",
                "action": "Add relevant coursework or projects under your degree",
                "reason": "Demonstrates foundational knowledge for required skills",
                "priority": "Medium",
                "category": "Technical Skill",
                "impact_score": 5,
            })

        # ===== PROFESSIONAL SUMMARY =====
        # Focus on soft skills and key technical differentiators
        soft_skills = [k for k in ranked_keywords if k["category"] == "Soft Skill"]
        for skill in soft_skills[:2]:
            recommendations["Professional Summary"].append({
                "keyword": skill["keyword"],
                "action": f"Highlight your {skill['keyword']} in your professional summary",
                "reason": f"Demonstrates key competency mentioned in job description",
                "priority": skill["priority"],
                "category": skill["category"],
                "impact_score": 4,
            })

        # Add top technical skills to summary
        top_tech = [k for k in ranked_keywords if k["category"] == "Technical Skill"
                   and k["priority"] == "High"][:2]
        for tech in top_tech:
            recommendations["Professional Summary"].append({
                "keyword": tech["keyword"],
                "action": f"Mention {tech['keyword']} expertise upfront",
                "reason": f"Critical skill for this role ({tech['jd_count']} mentions)",
                "priority": "High",
                "category": tech["category"],
                "impact_score": 6,
            })

        return recommendations

    # ========================================================================
    # 3. PRIORITY ACTION ITEMS
    # ========================================================================

    def prioritize_actions(
        self,
        section_recommendations: Dict[str, List[Dict[str, Any]]],
        keyword_report: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Create prioritized action list across all sections.

        Args:
            section_recommendations: Output from generate_section_recommendations()
            keyword_report: Output from KeywordAnalyzer.generate_keyword_report()

        Returns:
            Sorted list of high-impact actions:
            [
                {
                    "action": "...",
                    "section": "Skills",
                    "keyword": "...",
                    "priority": "High",
                    "impact_score": 10,
                },
                ...
            ]
        """
        all_actions = []

        for section, recommendations in section_recommendations.items():
            for rec in recommendations:
                all_actions.append({
                    "action": rec["action"],
                    "section": section,
                    "keyword": rec["keyword"],
                    "priority": rec["priority"],
                    "category": rec["category"],
                    "reason": rec["reason"],
                    "impact_score": rec["impact_score"],
                })

        # Sort by impact score (highest first), then by priority
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        all_actions.sort(
            key=lambda x: (-x["impact_score"], priority_order[x["priority"]])
        )

        return all_actions

    # ========================================================================
    # 4. TAILORING SUMMARY & SCORING
    # ========================================================================

    def calculate_tailoring_score(
        self,
        section_recommendations: Dict[str, List[Dict[str, Any]]],
        keyword_report: Dict[str, Any],
        ats_report: Dict[str, Any],
    ) -> int:
        """
        Calculate overall resume tailoring opportunity score (0-100).

        Higher score = more tailoring opportunities available.

        Args:
            section_recommendations: Output from generate_section_recommendations()
            keyword_report: Output from KeywordAnalyzer.generate_keyword_report()
            ats_report: Output from ATSAnalyzer.generate_ats_report()

        Returns:
            Tailoring score (0-100)
        """
        score = 0

        # Base on keyword match score (higher gap = higher score)
        keyword_match = keyword_report["statistics"]["keyword_match_score"]
        score += (100 - keyword_match) // 2  # Up to 50 points

        # Count recommendations
        total_recs = sum(len(recs) for recs in section_recommendations.values())
        score += min(total_recs * 2, 30)  # Up to 30 points

        # Consider missing sections (up to 20 points)
        missing_sections = ats_report.get("missing_sections", [])
        score += min(len(missing_sections) * 4, 20)

        return min(score, 100)

    def generate_tailoring_summary(
        self,
        keyword_report: Dict[str, Any],
        section_recommendations: Dict[str, List[Dict[str, Any]]],
        tailoring_score: int,
    ) -> str:
        """
        Generate a human-readable tailoring summary.

        Args:
            keyword_report: Output from KeywordAnalyzer.generate_keyword_report()
            section_recommendations: Output from generate_section_recommendations()
            tailoring_score: Output from calculate_tailoring_score()

        Returns:
            Brief summary string
        """
        keyword_stats = keyword_report["statistics"]
        coverage = keyword_stats["coverage_percent"]
        missing_count = keyword_stats["missing_keywords"]
        total_recs = sum(len(recs) for recs in section_recommendations.values())

        summary = f"Your resume covers {coverage}% of required keywords. "
        summary += f"We found {missing_count} missing keywords and {total_recs} tailoring opportunities. "

        if tailoring_score >= 70:
            summary += "Significant improvements are possible to better match this job description."
        elif tailoring_score >= 40:
            summary += "Moderate improvements can be made to strengthen your application."
        else:
            summary += "Your resume already aligns well with this job description."

        return summary

    # ========================================================================
    # 5. PUBLIC API - MAIN ENTRY POINT
    # ========================================================================

    def generate_tailoring_report(
        self,
        ats_report: Dict[str, Any],
        keyword_report: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate a complete resume tailoring report.

        This is the main entry point. Call this once per analysis.

        Args:
            ats_report: Output from ATSAnalyzer.generate_ats_report()
            keyword_report: Output from KeywordAnalyzer.generate_keyword_report()

        Returns:
            Comprehensive tailoring report:
            {
                "summary": str,
                "section_recommendations": {section: [recommendations]},
                "priority_actions": [prioritized_actions],
                "overall_tailoring_score": int (0-100),
                "section_priority": {section: priority_score},
            }
        """
        # Analyze section coverage
        section_coverage = self.analyze_section_coverage(ats_report, keyword_report)

        # Generate section-specific recommendations
        section_recommendations = self.generate_section_recommendations(
            keyword_report, section_coverage
        )

        # Prioritize actions
        priority_actions = self.prioritize_actions(
            section_recommendations, keyword_report
        )

        # Calculate tailoring score
        tailoring_score = self.calculate_tailoring_score(
            section_recommendations, keyword_report, ats_report
        )

        # Generate summary
        summary = self.generate_tailoring_summary(
            keyword_report, section_recommendations, tailoring_score
        )

        return {
            "summary": summary,
            "section_recommendations": section_recommendations,
            "priority_actions": priority_actions,
            "overall_tailoring_score": tailoring_score,
            "section_priority": section_coverage["section_priority"],
            "present_sections": section_coverage["present_sections"],
            "missing_sections": section_coverage["missing_sections"],
        }
