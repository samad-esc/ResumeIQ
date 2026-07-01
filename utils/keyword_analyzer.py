"""
Keyword Analyzer Module - Phase 2

Job Optimization Engine for ResumeIQ.
Analyzes keyword alignment between resume and job description,
identifies gaps, ranks priorities, and generates optimization recommendations.

Deterministic, rule-based analysis. No LLM calls. No Streamlit imports.
"""

import re
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import Counter
from utils.skill_analyzer import load_skills


# ============================================================================
# STOP WORDS & CONSTANTS
# ============================================================================

STOP_WORDS = {
    # Common articles
    "a", "an", "the",
    # Common prepositions
    "in", "on", "at", "by", "to", "of", "for", "from", "with", "as", "into",
    "through", "during", "before", "after", "above", "below", "between",
    "under", "along", "around", "over", "out", "about",
    # Common conjunctions
    "and", "or", "but", "nor", "yet", "so", "because", "since", "if", "unless",
    # Common verbs (weak)
    "is", "are", "am", "was", "were", "be", "been", "being", "have", "has",
    "had", "do", "does", "did", "will", "would", "could", "should", "may",
    "might", "must", "can", "shall", "exist", "exist",
    # Common pronouns
    "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them",
    "my", "your", "his", "her", "its", "our", "their",
    # Filler words
    "this", "that", "these", "those", "what", "which", "who", "whom", "why", "how",
    "where", "when", "there", "here", "all", "each", "every", "both", "few",
    "more", "most", "other", "some", "any", "no", "not",
    # Common modifiers
    "very", "really", "just", "only", "also", "even", "such", "same", "than", "up",
    # Digits and short words
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    # Generic terms
    "role", "position", "job", "work", "team", "company", "organization",
}

# Action verbs - powerful resume keywords
ACTION_VERBS = {
    "led", "managed", "directed", "supervised", "coordinated",
    "developed", "created", "built", "designed", "architected",
    "implemented", "deployed", "launched", "released",
    "optimized", "improved", "enhanced", "refined", "accelerated",
    "achieved", "accomplished", "completed", "delivered", "succeeded",
    "analyzed", "investigated", "examined", "researched", "explored",
    "solved", "fixed", "resolved", "debugged", "troubleshot",
    "automated", "streamlined", "simplified", "consolidated",
    "collaborated", "communicated", "presented", "explained",
    "mentored", "coached", "trained", "taught", "educated",
    "increased", "decreased", "reduced", "boosted", "grew",
    "wrote", "documented", "published", "authored",
    "tested", "validated", "verified", "confirmed",
    "planned", "designed", "structured", "organized",
    "integrated", "connected", "linked", "unified",
}

# Soft skills - important for ATS
SOFT_SKILLS = {
    "communication", "teamwork", "collaboration", "leadership",
    "problem solving", "critical thinking", "analysis",
    "time management", "organization", "planning",
    "attention to detail", "reliability", "accountability",
    "adaptability", "flexibility", "initiative",
    "creativity", "innovation", "strategic thinking",
    "project management", "agile", "scrum",
}


# ============================================================================
# KEYWORD ANALYZER CLASS
# ============================================================================

class KeywordAnalyzer:
    """
    Analyzes keyword alignment between resume and job description.
    
    Features:
    - Extract technical skills (from skills.json)
    - Extract multi-word terms, tools, frameworks
    - Calculate keyword frequency
    - Identify gaps and opportunities
    - Rank missing keywords by priority
    - Generate optimization recommendations
    """

    def __init__(self):
        """Initialize the analyzer with cached skills."""
        self.skills = load_skills()

    # ========================================================================
    # 1. KEYWORD EXTRACTION
    # ========================================================================

    def extract_keywords(self, text: str, include_soft_skills: bool = True) -> Dict[str, int]:
        """
        Extract all keywords from text with frequency counts.

        Extracts:
        - Technical skills (from skills.json)
        - Multi-word technical terms
        - Action verbs
        - Soft skills (if enabled)

        Args:
            text: Input text (resume or job description)
            include_soft_skills: Whether to count soft skills (default: True)

        Returns:
            Dictionary with keyword frequencies: {keyword: count}
        """
        if not text:
            return {}

        text_lower = text.lower()
        keyword_counts = Counter()

        # ===== Extract Technical Skills (from skills.json) =====
        for skill in self.skills:
            pattern = r"\b" + re.escape(skill) + r"\b"
            matches = re.findall(pattern, text_lower)
            if matches:
                keyword_counts[skill] += len(matches)

        # ===== Extract Action Verbs =====
        for verb in ACTION_VERBS:
            pattern = r"\b" + re.escape(verb) + r"\b"
            matches = re.findall(pattern, text_lower)
            if matches:
                keyword_counts[verb] += len(matches)

        # ===== Extract Soft Skills =====
        if include_soft_skills:
            for skill in SOFT_SKILLS:
                pattern = r"\b" + re.escape(skill) + r"\b"
                matches = re.findall(pattern, text_lower)
                if matches:
                    keyword_counts[skill] += len(matches)

        # ===== Extract Multi-word Terms (2-3 grams from high-frequency words) =====
        # Look for common technical phrases
        multiword_patterns = [
            r"\b(machine learning)\b",
            r"\b(deep learning)\b",
            r"\b(natural language processing|nlp)\b",
            r"\b(data science)\b",
            r"\b(data engineering)\b",
            r"\b(cloud computing)\b",
            r"\b(devops|dev ops)\b",
            r"\b(continuous integration|ci)\b",
            r"\b(continuous deployment|cd)\b",
            r"\b(rest api|rest apis)\b",
            r"\b(microservices)\b",
            r"\b(relational database|sql database)\b",
            r"\b(nosql)\b",
            r"\b(api design)\b",
            r"\b(api development)\b",
            r"\b(web development)\b",
            r"\b(mobile development)\b",
            r"\b(frontend development)\b",
            r"\b(backend development)\b",
            r"\b(full stack)\b",
            r"\b(object oriented)\b",
            r"\b(object-oriented)\b",
        ]

        for pattern in multiword_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                # Normalize to lowercase
                for match in matches:
                    normalized = match.lower().replace("-", " ")
                    keyword_counts[normalized] += 1

        return dict(keyword_counts)

    # ========================================================================
    # 2. KEYWORD FREQUENCY ANALYSIS
    # ========================================================================

    def calculate_keyword_density(self, text: str) -> Dict[str, float]:
        """
        Calculate keyword density (percentage of total keywords).

        Args:
            text: Input text

        Returns:
            Dictionary with density percentages: {keyword: density_percent}
        """
        keywords = self.extract_keywords(text)
        total = sum(keywords.values())

        if total == 0:
            return {}

        return {
            keyword: round((count / total) * 100, 2)
            for keyword, count in keywords.items()
        }

    # ========================================================================
    # 3. KEYWORD GAP ANALYSIS
    # ========================================================================

    def analyze_keyword_gaps(
        self, resume_keywords: Dict[str, int], jd_keywords: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Analyze keyword gaps between resume and job description.

        Categorizes keywords as:
        - Missing: In JD, not in resume
        - Underrepresented: In both, but lower frequency in resume
        - Well-matched: Similar frequency in both
        - Overused: Higher in resume than JD

        Args:
            resume_keywords: Output from extract_keywords(resume_text)
            jd_keywords: Output from extract_keywords(jd_text)

        Returns:
            Dictionary with gap analysis:
            {
                "missing": [{keyword, jd_count}, ...],
                "underrepresented": [{keyword, resume_count, jd_count, gap}, ...],
                "well_matched": [{keyword, resume_count, jd_count}, ...],
                "overused": [{keyword, resume_count, jd_count, excess}, ...],
            }
        """
        resume_set = set(resume_keywords.keys())
        jd_set = set(jd_keywords.keys())

        missing = []
        underrepresented = []
        well_matched = []
        overused = []

        # ===== Analyze keywords from JD =====
        for keyword in jd_set:
            jd_count = jd_keywords[keyword]

            if keyword not in resume_set:
                # Missing
                missing.append({
                    "keyword": keyword,
                    "jd_count": jd_count,
                })
            else:
                resume_count = resume_keywords[keyword]
                gap = jd_count - resume_count

                # Calculate ratio (how much of JD frequency is in resume)
                coverage_ratio = resume_count / jd_count if jd_count > 0 else 0

                if coverage_ratio >= 0.75 and coverage_ratio <= 1.25:
                    # Well-matched: within 75-125% of JD frequency
                    well_matched.append({
                        "keyword": keyword,
                        "resume_count": resume_count,
                        "jd_count": jd_count,
                        "coverage_ratio": round(coverage_ratio, 2),
                    })
                elif resume_count > jd_count:
                    # Overused
                    excess = resume_count - jd_count
                    overused.append({
                        "keyword": keyword,
                        "resume_count": resume_count,
                        "jd_count": jd_count,
                        "excess": excess,
                    })
                else:
                    # Underrepresented
                    underrepresented.append({
                        "keyword": keyword,
                        "resume_count": resume_count,
                        "jd_count": jd_count,
                        "gap": gap,
                        "coverage_ratio": round(coverage_ratio, 2),
                    })

        return {
            "missing": sorted(missing, key=lambda x: x["jd_count"], reverse=True),
            "underrepresented": sorted(
                underrepresented, key=lambda x: x["gap"], reverse=True
            ),
            "well_matched": sorted(
                well_matched, key=lambda x: x["jd_count"], reverse=True
            ),
            "overused": sorted(overused, key=lambda x: x["excess"], reverse=True),
        }

    # ========================================================================
    # 4. PRIORITY RANKING
    # ========================================================================

    def rank_missing_keywords(
        self, gap_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Rank missing keywords by priority.

        Priority factors:
        - Frequency in JD (higher = more important)
        - Whether keyword exists in resume (missing = higher priority)
        - Keyword category (technical > action verb > soft skill)

        Args:
            gap_analysis: Output from analyze_keyword_gaps()

        Returns:
            Sorted list of keywords with priority levels:
            [
                {
                    "keyword": str,
                    "jd_count": int,
                    "priority": "High" | "Medium" | "Low",
                    "category": "Technical Skill" | "Action Verb" | "Soft Skill",
                    "reason": str,
                },
                ...
            ]
        """
        missing = gap_analysis["missing"]
        ranked = []

        for item in missing:
            keyword = item["keyword"]
            jd_count = item["jd_count"]

            # ===== Determine Category =====
            if keyword in self.skills:
                category = "Technical Skill"
            elif keyword in ACTION_VERBS:
                category = "Action Verb"
            elif keyword in SOFT_SKILLS:
                category = "Soft Skill"
            else:
                category = "Industry Term"

            # ===== Calculate Priority =====
            # Higher frequency + technical skills = higher priority
            priority_score = jd_count * (
                4 if category == "Technical Skill"
                else 3 if category == "Industry Term"
                else 2 if category == "Action Verb"
                else 1
            )

            if priority_score >= 12:
                priority = "High"
            elif priority_score >= 6:
                priority = "Medium"
            else:
                priority = "Low"

            # ===== Reason =====
            reason = f"Mentioned {jd_count} time(s) in job description"

            ranked.append({
                "keyword": keyword,
                "jd_count": jd_count,
                "priority": priority,
                "category": category,
                "reason": reason,
            })

        # Sort by priority then frequency
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        return sorted(
            ranked,
            key=lambda x: (priority_order[x["priority"]], -x["jd_count"])
        )

    # ========================================================================
    # 5. OPTIMIZATION RECOMMENDATIONS
    # ========================================================================

    def generate_recommendations(
        self, gap_analysis: Dict[str, Any], ranked_keywords: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Generate actionable, deterministic optimization recommendations.

        No LLM calls. Pure logic-based suggestions.

        Args:
            gap_analysis: Output from analyze_keyword_gaps()
            ranked_keywords: Output from rank_missing_keywords()

        Returns:
            List of actionable recommendations:
            [
                "Add Python to your skills section (mentioned 8 times in JD)",
                "Mention Docker in your projects section (mentioned 4 times)",
                ...
            ]
        """
        recommendations = []

        # ===== Missing Keywords Recommendations =====
        high_priority = [k for k in ranked_keywords if k["priority"] == "High"]
        medium_priority = [k for k in ranked_keywords if k["priority"] == "Medium"]

        for item in high_priority[:3]:  # Top 3 high-priority
            keyword = item["keyword"]
            count = item["jd_count"]
            category_lower = item["category"].lower()

            if category_lower == "technical skill":
                recommendations.append(
                    f"Add {keyword} to your skills section ({count} mentions in JD)."
                )
            elif category_lower == "action verb":
                recommendations.append(
                    f"Use '{keyword}' more frequently in your experience descriptions ({count} mentions in JD)."
                )
            else:
                recommendations.append(
                    f"Include {keyword} in your resume ({count} mentions in JD)."
                )

        for item in medium_priority[:2]:  # Top 2 medium-priority
            keyword = item["keyword"]
            count = item["jd_count"]
            recommendations.append(
                f"Consider adding {keyword} where applicable ({count} mentions in JD)."
            )

        # ===== Underrepresented Keywords Recommendations =====
        underrep = gap_analysis["underrepresented"][:3]
        for item in underrep:
            keyword = item["keyword"]
            gap = item["gap"]
            recommendations.append(
                f"Increase mentions of {keyword} by ~{gap} more usage(s)."
            )

        # ===== Overused Keywords Recommendations =====
        overused = gap_analysis["overused"]
        if overused:
            for item in overused[:2]:
                keyword = item["keyword"]
                recommendations.append(
                    f"Consider reducing redundant mentions of {keyword} (appears {item['excess']} more times than JD)."
                )

        # ===== Coverage-based Recommendations =====
        missing_count = len(gap_analysis["missing"])
        if missing_count > 15:
            recommendations.append(
                f"Review the job description carefully—you're missing {missing_count} keywords. "
                f"Prioritize high-frequency terms."
            )

        well_matched = gap_analysis["well_matched"]
        if well_matched:
            recommendations.append(
                f"Great! You have strong alignment on {len(well_matched)} key keywords. "
                f"Maintain this coverage."
            )

        return recommendations

    # ========================================================================
    # 6. STATISTICS & METRICS
    # ========================================================================

    def calculate_statistics(
        self,
        resume_keywords: Dict[str, int],
        jd_keywords: Dict[str, int],
        gap_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive keyword statistics.

        Args:
            resume_keywords: Output from extract_keywords(resume_text)
            jd_keywords: Output from extract_keywords(jd_text)
            gap_analysis: Output from analyze_keyword_gaps()

        Returns:
            Statistics dictionary:
            {
                "resume_keywords_total": int,
                "jd_keywords_total": int,
                "unique_resume_keywords": int,
                "unique_jd_keywords": int,
                "matched_keywords": int,
                "missing_keywords": int,
                "coverage_percent": float,
                "top_missing_keywords": [str],
                "top_present_keywords": [str],
                "keyword_match_score": int (0-100),
            }
        """
        resume_set = set(resume_keywords.keys())
        jd_set = set(jd_keywords.keys())
        matched = resume_set & jd_set
        missing_count = len(gap_analysis["missing"])

        # Calculate coverage percentage
        coverage_percent = (
            (len(matched) / len(jd_set) * 100) if jd_set else 0
        )

        # Calculate keyword match score (0-100)
        # Based on: coverage, underrepresentation, overuse
        base_score = coverage_percent  # 0-100

        # Bonus for well-matched keywords
        well_matched_bonus = min(len(gap_analysis["well_matched"]) * 2, 20)

        # Penalty for underrepresented keywords
        underrep_penalty = min(len(gap_analysis["underrepresented"]) * 1.5, 20)

        # Penalty for overused keywords
        overuse_penalty = min(len(gap_analysis["overused"]) * 1, 15)

        keyword_match_score = max(
            0,
            min(100, base_score + well_matched_bonus - underrep_penalty - overuse_penalty)
        )

        # Get top keywords
        top_missing = [
            item["keyword"] for item in gap_analysis["missing"][:5]
        ]
        top_present = sorted(
            matched,
            key=lambda x: (
                resume_keywords[x] * (4 if x in self.skills else 1),
            ),
            reverse=True
        )[:5]

        return {
            "resume_keywords_total": sum(resume_keywords.values()),
            "jd_keywords_total": sum(jd_keywords.values()),
            "unique_resume_keywords": len(resume_set),
            "unique_jd_keywords": len(jd_set),
            "matched_keywords": len(matched),
            "missing_keywords": missing_count,
            "coverage_percent": round(coverage_percent, 2),
            "top_missing_keywords": top_missing,
            "top_present_keywords": top_present,
            "keyword_match_score": int(keyword_match_score),
        }

    # ========================================================================
    # 7. PUBLIC API - MAIN ENTRY POINT
    # ========================================================================

    def generate_keyword_report(
        self, resume_text: str, jd_text: str
    ) -> Dict[str, Any]:
        """
        Generate a complete keyword optimization report.

        This is the main entry point. Call this once per analysis.

        Args:
            resume_text: Full resume text
            jd_text: Full job description text

        Returns:
            Comprehensive report:
            {
                "statistics": {...},
                "keywords": {
                    "resume": {keyword: count, ...},
                    "jd": {keyword: count, ...},
                },
                "gap_analysis": {...},
                "ranked_keywords": [...],
                "recommendations": [str],
            }
        """
        # Extract keywords from both texts
        resume_keywords = self.extract_keywords(resume_text)
        jd_keywords = self.extract_keywords(jd_text)

        # Analyze gaps
        gap_analysis = self.analyze_keyword_gaps(resume_keywords, jd_keywords)

        # Rank missing keywords
        ranked_keywords = self.rank_missing_keywords(gap_analysis)

        # Generate recommendations
        recommendations = self.generate_recommendations(gap_analysis, ranked_keywords)

        # Calculate statistics
        statistics = self.calculate_statistics(
            resume_keywords, jd_keywords, gap_analysis
        )

        return {
            "statistics": statistics,
            "keywords": {
                "resume": resume_keywords,
                "jd": jd_keywords,
            },
            "gap_analysis": gap_analysis,
            "ranked_keywords": ranked_keywords,
            "recommendations": recommendations,
        }
