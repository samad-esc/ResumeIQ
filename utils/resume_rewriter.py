"""
Resume Rewriter Engine - Phase 4

Provides AI-powered resume content improvements using Gemini LLM.
Rewrites professional summary, bullet points, and suggests achievement enhancements.
Naturally incorporates ATS keywords without fabricating experience.

Uses existing llm.py interface. Deterministic fallback when API unavailable.
Never invents experience, employers, certifications, or metrics.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from utils.llm import get_model

logging.basicConfig(level=logging.INFO)


# ============================================================================
# CONSTANTS
# ============================================================================

PROFESSIONAL_SUMMARY_PROMPT_TEMPLATE = """
You are a professional resume writer specializing in ATS-optimized content.

Rewrite the professional summary below to better match the job description.

REQUIREMENTS:
- 3-5 lines maximum
- ATS-friendly (use keywords naturally)
- Job-specific and compelling
- Professional tone
- Include only factual information from the original summary
- Do NOT add false experience, skills, or achievements

ORIGINAL SUMMARY:
{original_summary}

JOB DESCRIPTION (relevant keywords):
{jd_keywords}

TAILORING FOCUS:
{tailoring_focus}

Provide ONLY the rewritten summary, no explanations.
"""

BULLET_REWRITE_PROMPT_TEMPLATE = """
You are a professional resume writer specializing in ATS-optimized bullet points.

Rewrite the following resume bullet point to be stronger and more ATS-friendly.

REQUIREMENTS:
- Start with a strong action verb
- Include measurable achievements (if present in original)
- Incorporate relevant job keywords naturally
- Keep factual - do NOT fabricate metrics, technologies, or achievements
- Maximum 2 lines
- Professional tone

ORIGINAL BULLET:
{original_bullet}

CONTEXT (your role/project):
{context}

KEY KEYWORDS TO INCORPORATE (if applicable):
{keywords}

Provide ONLY the rewritten bullet point, no explanations or alternatives.
"""

ACHIEVEMENT_ENHANCEMENT_PROMPT_TEMPLATE = """
You are a professional resume coach specializing in achievement quantification.

Analyze the following resume bullet and suggest how to make it more impactful.

REQUIREMENTS:
- If the bullet lacks metrics, suggest adding measurable outcomes
- If metrics are already present, suggest alternative quantifications
- DO NOT fabricate numbers or false metrics
- If exact numbers are unavailable, suggest frameworks for measurement
- Examples: performance improvements, user adoption, time savings, cost reduction, etc.

ORIGINAL BULLET:
{original_bullet}

Provide suggestions for improvement without inventing false metrics.
Format: "Consider adding: [suggestion]" or "If possible, quantify: [framework]"
"""

KEYWORD_INJECTION_PROMPT_TEMPLATE = """
You are an ATS optimization specialist.

Review the resume content and suggest natural ways to incorporate missing keywords.

REQUIREMENTS:
- Never force keywords unnaturally
- Integrate keywords only where contextually relevant
- Provide specific, location-based suggestions
- Only suggest if genuinely applicable to the content

RESUME EXCERPT:
{resume_excerpt}

IMPORTANT MISSING KEYWORDS:
{missing_keywords}

Provide specific suggestions in format:
"[Section]: Replace '[original phrase]' with '[improved phrase containing keyword]'" or
"[Section]: Consider adding '[context with keyword]' to [description]"
"""


# ============================================================================
# RESUME REWRITER CLASS
# ============================================================================

class ResumeRewriter:
    """
    AI-powered resume content rewriter using Gemini LLM.

    Features:
    - Professional summary rewriting
    - Bullet point enhancement
    - Achievement quantification suggestions
    - ATS keyword injection
    - Fallback suggestions when API unavailable
    """

    def __init__(self):
        """Initialize the Resume Rewriter."""
        self.model = get_model()

    # ========================================================================
    # 1. PROFESSIONAL SUMMARY REWRITER
    # ========================================================================

    def rewrite_professional_summary(
        self,
        resume_text: str,
        jd_text: str,
        tailoring_report: Dict[str, Any],
        keyword_report: Dict[str, Any],
    ) -> Optional[str]:
        """
        Rewrite professional summary to match job description.

        Args:
            resume_text: Full resume text
            jd_text: Job description
            tailoring_report: Output from ResumeTailor.generate_tailoring_report()
            keyword_report: Output from KeywordAnalyzer.generate_keyword_report()

        Returns:
            Rewritten professional summary or None if API unavailable
        """
        if not self.model:
            return None

        # Extract existing summary from resume (first 3-5 lines usually)
        summary_lines = resume_text.split('\n')[:10]
        original_summary = '\n'.join(summary_lines).strip()

        if not original_summary or len(original_summary) < 20:
            return None

        # Get top keywords from job description
        ranked_keywords = keyword_report["ranked_keywords"]
        top_keywords = [k["keyword"] for k in ranked_keywords[:8]]
        jd_keywords_str = ", ".join(top_keywords)

        # Get summary recommendations from tailoring
        summary_recs = tailoring_report.get("section_recommendations", {}).get(
            "Professional Summary", []
        )
        tailoring_focus = "; ".join(
            [r["action"] for r in summary_recs[:3]]
        ) or "Improve job fit and keyword alignment"

        prompt = PROFESSIONAL_SUMMARY_PROMPT_TEMPLATE.format(
            original_summary=original_summary[:500],
            jd_keywords=jd_keywords_str,
            tailoring_focus=tailoring_focus,
        )

        try:
            response = self.model.generate_content(prompt)
            result = response.text.strip()

            # Validate response isn't empty
            if result and len(result) > 20:
                return result
            return None

        except Exception as e:
            logging.exception(f"Professional summary rewrite failed: {e}")
            return None

    # ========================================================================
    # 2. BULLET POINT REWRITER
    # ========================================================================

    def extract_bullet_points(self, resume_text: str) -> List[str]:
        """
        Extract bullet points from resume text.

        Args:
            resume_text: Full resume text

        Returns:
            List of bullet point strings
        """
        bullets = []

        # Match various bullet point patterns
        patterns = [
            r'^\s*[-•*]\s+(.+)$',  # - or • or * prefix
            r'^\s*\d+\.\s+(.+)$',  # numbered lists
        ]

        for line in resume_text.split('\n'):
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    bullet = match.group(1).strip()
                    if bullet and len(bullet) > 10:
                        bullets.append(bullet)
                    break

        return bullets[:10]  # Top 10 bullets

    def rewrite_bullet_point(
        self,
        bullet: str,
        context: str,
        keyword_report: Dict[str, Any],
    ) -> Optional[str]:
        """
        Rewrite a single bullet point to be stronger and more ATS-friendly.

        Args:
            bullet: Original bullet point
            context: Brief context (role, project, etc.)
            keyword_report: Output from KeywordAnalyzer.generate_keyword_report()

        Returns:
            Rewritten bullet or None if API unavailable
        """
        if not self.model or len(bullet) < 10:
            return None

        # Get relevant keywords
        ranked_keywords = keyword_report["ranked_keywords"]
        relevant_keywords = [
            k["keyword"] for k in ranked_keywords
            if k["priority"] in ["High", "Medium"]
        ][:5]
        keywords_str = ", ".join(relevant_keywords) if relevant_keywords else "job requirements"

        prompt = BULLET_REWRITE_PROMPT_TEMPLATE.format(
            original_bullet=bullet,
            context=context[:200],
            keywords=keywords_str,
        )

        try:
            response = self.model.generate_content(prompt)
            result = response.text.strip()

            # Validate it's not empty and reasonably sized
            if result and len(result) > 15 and len(result) < 400:
                return result
            return None

        except Exception as e:
            logging.exception(f"Bullet point rewrite failed: {e}")
            return None

    def rewrite_bullet_points(
        self,
        resume_text: str,
        keyword_report: Dict[str, Any],
    ) -> List[Dict[str, str]]:
        """
        Rewrite multiple bullet points.

        Args:
            resume_text: Full resume text
            keyword_report: Output from KeywordAnalyzer.generate_keyword_report()

        Returns:
            List of {original, improved} pairs
        """
        rewrites = []

        bullets = self.extract_bullet_points(resume_text)

        # Provide generic context since we don't have section info
        for bullet in bullets:
            improved = self.rewrite_bullet_point(bullet, "Professional experience", keyword_report)

            if improved and improved != bullet:
                rewrites.append({
                    "original": bullet,
                    "improved": improved,
                })

            # Limit to avoid excessive API calls
            if len(rewrites) >= 5:
                break

        return rewrites

    # ========================================================================
    # 3. ACHIEVEMENT ENHANCEMENT
    # ========================================================================

    def suggest_achievement_enhancements(
        self,
        resume_text: str,
    ) -> List[str]:
        """
        Suggest ways to quantify and strengthen achievements.

        Args:
            resume_text: Full resume text

        Returns:
            List of enhancement suggestions
        """
        if not self.model:
            return []

        bullets = self.extract_bullet_points(resume_text)
        suggestions = []

        # Process top 5 bullets
        for bullet in bullets[:5]:
            prompt = ACHIEVEMENT_ENHANCEMENT_PROMPT_TEMPLATE.format(
                original_bullet=bullet,
            )

            try:
                response = self.model.generate_content(prompt)
                result = response.text.strip()

                if result and len(result) > 10:
                    suggestions.append(result)

            except Exception as e:
                logging.exception(f"Achievement enhancement failed: {e}")
                continue

            # Limit to avoid excessive API calls
            if len(suggestions) >= 3:
                break

        return suggestions

    # ========================================================================
    # 4. ATS KEYWORD INJECTION
    # ========================================================================

    def suggest_keyword_insertions(
        self,
        resume_text: str,
        keyword_report: Dict[str, Any],
    ) -> List[Dict[str, str]]:
        """
        Suggest natural ways to incorporate missing keywords.

        Args:
            resume_text: Full resume text
            keyword_report: Output from KeywordAnalyzer.generate_keyword_report()

        Returns:
            List of {location, suggestion} pairs
        """
        if not self.model:
            return []

        gap_analysis = keyword_report["gap_analysis"]
        missing_keywords = gap_analysis.get("missing", [])

        if not missing_keywords:
            return []

        # Get top 5 missing keywords by frequency
        top_missing = sorted(
            missing_keywords,
            key=lambda x: x["jd_count"],
            reverse=True
        )[:5]
        keywords_str = ", ".join([k["keyword"] for k in top_missing])

        # Get relevant sections of resume
        resume_excerpt = resume_text[:800]  # First 800 chars

        prompt = KEYWORD_INJECTION_PROMPT_TEMPLATE.format(
            resume_excerpt=resume_excerpt,
            missing_keywords=keywords_str,
        )

        suggestions = []

        try:
            response = self.model.generate_content(prompt)
            result = response.text.strip()

            # Parse suggestions
            for line in result.split('\n'):
                line = line.strip()
                if line and len(line) > 10:
                    suggestions.append({
                        "location": line.split(':')[0] if ':' in line else "Resume",
                        "suggestion": line,
                    })

            return suggestions[:5]  # Top 5 suggestions

        except Exception as e:
            logging.exception(f"Keyword injection suggestions failed: {e}")
            return []

    # ========================================================================
    # 5. IMPROVEMENT SCORING
    # ========================================================================

    def calculate_improvement_score(
        self,
        bullet_rewrites: List[Dict[str, str]],
        achievement_suggestions: List[str],
        keyword_insertions: List[Dict[str, str]],
    ) -> int:
        """
        Calculate overall improvement potential score (0-100).

        Args:
            bullet_rewrites: Output from rewrite_bullet_points()
            achievement_suggestions: Output from suggest_achievement_enhancements()
            keyword_insertions: Output from suggest_keyword_insertions()

        Returns:
            Improvement score (0-100)
        """
        score = 0

        # Bullet point improvements
        score += min(len(bullet_rewrites) * 15, 40)

        # Achievement quantification opportunities
        score += min(len(achievement_suggestions) * 15, 30)

        # Keyword insertion opportunities
        score += min(len(keyword_insertions) * 10, 30)

        return min(score, 100)

    # ========================================================================
    # 6. PUBLIC API - MAIN ENTRY POINT
    # ========================================================================

    def generate_rewrite_report(
        self,
        resume_text: str,
        jd_text: str,
        keyword_report: Dict[str, Any],
        tailoring_report: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate a complete resume rewrite report.

        This is the main entry point. Call this once per analysis.

        Args:
            resume_text: Full resume text
            jd_text: Job description
            keyword_report: Output from KeywordAnalyzer.generate_keyword_report()
            tailoring_report: Output from ResumeTailor.generate_tailoring_report()

        Returns:
            Comprehensive rewrite report:
            {
                "summary_rewrite": "...",
                "bullet_rewrites": [
                    {"original": "...", "improved": "..."},
                    ...
                ],
                "achievement_suggestions": [...],
                "keyword_insertions": [...],
                "overall_improvement_score": int (0-100),
                "has_api_key": bool,
            }
        """
        # Check if API is available
        has_api = self.model is not None

        # Rewrite professional summary
        summary_rewrite = None
        if has_api:
            summary_rewrite = self.rewrite_professional_summary(
                resume_text, jd_text, tailoring_report, keyword_report
            )

        # Rewrite bullet points
        bullet_rewrites = []
        if has_api:
            bullet_rewrites = self.rewrite_bullet_points(resume_text, keyword_report)

        # Suggest achievement enhancements
        achievement_suggestions = []
        if has_api:
            achievement_suggestions = self.suggest_achievement_enhancements(resume_text)

        # Suggest keyword insertions
        keyword_insertions = []
        if has_api:
            keyword_insertions = self.suggest_keyword_insertions(resume_text, keyword_report)

        # Calculate improvement score
        improvement_score = self.calculate_improvement_score(
            bullet_rewrites, achievement_suggestions, keyword_insertions
        )

        return {
            "summary_rewrite": summary_rewrite,
            "bullet_rewrites": bullet_rewrites,
            "achievement_suggestions": achievement_suggestions,
            "keyword_insertions": keyword_insertions,
            "overall_improvement_score": improvement_score,
            "has_api_key": has_api,
        }
