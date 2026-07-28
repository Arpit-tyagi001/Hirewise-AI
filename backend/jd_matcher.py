"""
Job Description Matching Engine.
Compares candidate resume text and parsed skills against a Target Job Description
using TF-IDF vector similarity and skill taxonomy overlap algorithms.
"""

import re
from typing import Any, Dict, List, Set
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from resume_parser import SKILL_TAXONOMY


class JDMatcher:
    """Job Description matching and gap analysis engine."""

    def match(self, parsed_resume: Dict[str, Any], job_description: str) -> Dict[str, Any]:
        """
        Compare parsed resume data with target job description string.
        """
        resume_text = parsed_resume.get("raw_text", "")
        resume_skills = set([s.lower() for s in parsed_resume.get("skills", [])])

        if not job_description.strip():
            return {
                "match_percentage": 0.0,
                "matching_skills": [],
                "missing_skills": [],
                "recommended_keywords": [],
                "strengths": [],
                "weaknesses": ["Empty Job Description provided."],
                "suggestions": ["Please input a non-empty job description."]
            }

        # 1. Skill Taxonomy Extraction from JD
        jd_skills = self._extract_skills_from_jd(job_description)

        # 2. Skill Overlap Analysis
        matching_skills_lower = resume_skills.intersection(jd_skills)
        missing_skills_lower = jd_skills - resume_skills

        matching_skills = [self._capitalize_skill(s) for s in sorted(list(matching_skills_lower))]
        missing_skills = [self._capitalize_skill(s) for s in sorted(list(missing_skills_lower))]

        # 3. Vector Similarity (TF-IDF + Cosine Similarity)
        tfidf_sim = self._calculate_tfidf_similarity(resume_text, job_description)

        # 4. Composite Match Percentage Calculation
        skill_match_ratio = len(matching_skills_lower) / len(jd_skills) if jd_skills else 0.5
        composite_score = (skill_match_ratio * 0.6) + (tfidf_sim * 0.4)
        match_percentage = min(100.0, max(0.0, round(composite_score * 100, 1)))

        # 5. Extract Recommended Keywords (High TF-IDF terms in JD not in resume)
        recommended_keywords = self._extract_recommended_keywords(job_description, resume_text, missing_skills)

        # 6. Generate Strengths & Weaknesses
        strengths = []
        weaknesses = []
        suggestions = []

        if match_percentage >= 80:
            strengths.append("High overall keyword alignment and strong coverage of primary core skills.")
        elif match_percentage >= 60:
            strengths.append("Moderate skill alignment with key job requirements.")
        else:
            weaknesses.append("Low overall keyword match. Significant resume tailoring recommended.")

        if matching_skills:
            strengths.append(f"Direct match on key skills: {', '.join(matching_skills[:5])}.")

        if missing_skills:
            weaknesses.append(f"Missing required technical competencies: {', '.join(missing_skills[:5])}.")
            suggestions.append(f"Incorporate missing core skills ({', '.join(missing_skills[:3])}) into your Skills or Experience bullet points if you possess relevant experience.")

        if recommended_keywords:
            suggestions.append(f"Incorporate high-frequency job keywords: {', '.join(recommended_keywords[:4])}.")

        if len(parsed_resume.get("projects", [])) == 0 and "project" in job_description.lower():
            suggestions.append("The Job Description emphasizes project deliverables; add a Projects section highlighting concrete outcomes.")

        return {
            "match_percentage": match_percentage,
            "matching_skills": matching_skills,
            "missing_skills": missing_skills,
            "recommended_keywords": recommended_keywords,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "suggestions": suggestions
        }

    def _extract_skills_from_jd(self, jd_text: str) -> Set[str]:
        found = set()
        jd_lower = jd_text.lower()
        for skill in SKILL_TAXONOMY:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, jd_lower):
                found.add(skill.lower())
        return found

    def _calculate_tfidf_similarity(self, resume_text: str, jd_text: str) -> float:
        try:
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
            sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(sim)
        except Exception:
            return 0.5

    def _extract_recommended_keywords(self, jd_text: str, resume_text: str, missing_skills: List[str]) -> List[str]:
        keywords = set(missing_skills)
        try:
            vectorizer = TfidfVectorizer(stop_words='english', max_features=25)
            vectorizer.fit([jd_text])
            feature_names = vectorizer.get_feature_names_out()
            resume_lower = resume_text.lower()

            for kw in feature_names:
                if len(kw) > 3 and kw not in resume_lower and not kw.isdigit():
                    keywords.add(kw.title())
        except Exception:
            pass

        return sorted(list(keywords))[:8]

    def _capitalize_skill(self, skill: str) -> str:
        specials = {
            "javascript": "JavaScript", "typescript": "TypeScript", "python": "Python",
            "c++": "C++", "c#": "C#", "html": "HTML", "css": "CSS", "sql": "SQL",
            "react": "React", "fastapi": "FastAPI", "django": "Django", "flask": "Flask",
            "postgresql": "PostgreSQL", "mysql": "MySQL", "mongodb": "MongoDB",
            "aws": "AWS", "azure": "Azure", "gcp": "GCP", "docker": "Docker",
            "kubernetes": "Kubernetes", "git": "Git", "github": "GitHub"
        }
        return specials.get(skill.lower(), skill.title())
