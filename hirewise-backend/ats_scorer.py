"""
ATS Scoring Engine.
Evaluates resume parsed data across 10 critical dimensions to calculate an overall ATS score,
section-by-section breakdown, and actionable improvement recommendations.
"""

import re
from typing import Any, Dict, List

# List of strong action verbs expected in impactful resume bullet points
ACTION_VERBS = {
    "achieved", "architected", "accelerated", "built", "created", "designed", "developed",
    "engineered", "established", "implemented", "improved", "increased", "launched",
    "led", "managed", "maximized", "optimized", "orchestrated", "overhauled", "pioneered",
    "reduced", "restructured", "scaled", "spearheaded", "standardized", "streamlined",
    "transformed", "automated", "boosted", "deployed", "executed", "formulated"
}


class ATSScorer:
    """Production ATS scoring engine evaluating 10 key criteria."""

    def evaluate(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a parsed resume dictionary and produce ATS scores & suggestions.
        """
        suggestions: List[Dict[str, str]] = []

        # 1. Contact Info Score (max 10)
        contact_score, contact_suggestions = self._score_contact_info(parsed_data)
        suggestions.extend(contact_suggestions)

        # 2. Skills Score (max 20)
        skills_score, skill_suggestions = self._score_skills(parsed_data)
        suggestions.extend(skill_suggestions)

        # 3. Experience Score (max 15)
        experience_score, exp_suggestions = self._score_experience(parsed_data)
        suggestions.extend(exp_suggestions)

        # 4. Education Score (max 10)
        education_score, edu_suggestions = self._score_education(parsed_data)
        suggestions.extend(edu_suggestions)

        # 5. Projects Score (max 10)
        projects_score, proj_suggestions = self._score_projects(parsed_data)
        suggestions.extend(proj_suggestions)

        # 6. Certifications Score (max 10)
        cert_score, cert_suggestions = self._score_certifications(parsed_data)
        suggestions.extend(cert_suggestions)

        # 7. Action Verbs Score (max 10)
        action_verb_score, verb_suggestions = self._score_action_verbs(parsed_data)
        suggestions.extend(verb_suggestions)

        # 8. Keyword Density / Industry Vocabulary (max 5)
        keyword_score, kw_suggestions = self._score_keyword_density(parsed_data)
        suggestions.extend(kw_suggestions)

        # 9. Formatting & Structure (max 5)
        formatting_score, format_suggestions = self._score_formatting(parsed_data)
        suggestions.extend(format_suggestions)

        # 10. Missing Sections Check (max 5)
        section_score, sec_suggestions = self._score_section_completeness(parsed_data)
        suggestions.extend(sec_suggestions)

        # Calculate overall weighted ATS score out of 100
        overall_score = min(
            100.0,
            round(
                contact_score + skills_score + experience_score + education_score +
                projects_score + cert_score + action_verb_score + keyword_score +
                formatting_score + section_score,
                1
            )
        )

        # Determine level label
        if overall_score >= 85:
            level = "Excellent (ATS Ready)"
        elif overall_score >= 70:
            level = "Good (Minor Optimization Needed)"
        elif overall_score >= 50:
            level = "Average (Requires Improvements)"
        else:
            level = "Needs Significant Optimization"

        section_scores = {
            "contact_info": {"score": contact_score, "max": 10},
            "skills": {"score": skills_score, "max": 20},
            "experience": {"score": experience_score, "max": 15},
            "education": {"score": education_score, "max": 10},
            "projects": {"score": projects_score, "max": 10},
            "certifications": {"score": cert_score, "max": 10},
            "action_verbs": {"score": action_verb_score, "max": 10},
            "keyword_density": {"score": keyword_score, "max": 5},
            "formatting": {"score": formatting_score, "max": 5},
            "section_completeness": {"score": section_score, "max": 5}
        }

        return {
            "overall_score": overall_score,
            "level": level,
            "section_scores": section_scores,
            "suggestions": suggestions
        }

    def _score_contact_info(self, data: Dict[str, Any]) -> tuple[float, List[Dict[str, str]]]:
        score = 0.0
        suggestions = []

        if data.get("name") and data["name"] != "Candidate":
            score += 2.5
        else:
            suggestions.append({
                "type": "warning",
                "priority": "High",
                "category": "Contact Info",
                "title": "Missing Candidate Name",
                "message": "Ensure your full name is formatted prominently at the top of your resume."
            })

        if data.get("email"):
            score += 2.5
        else:
            suggestions.append({
                "type": "error",
                "priority": "High",
                "category": "Contact Info",
                "title": "Missing Email Address",
                "message": "Include a clear, professional email address."
            })

        if data.get("phone"):
            score += 2.0
        else:
            suggestions.append({
                "type": "warning",
                "priority": "Medium",
                "category": "Contact Info",
                "title": "Missing Phone Number",
                "message": "Provide a phone number with country/area code."
            })

        if data.get("linkedin_url"):
            score += 1.5
        else:
            suggestions.append({
                "type": "info",
                "priority": "Medium",
                "category": "Contact Info",
                "title": "Add LinkedIn Profile",
                "message": "Including a LinkedIn URL increases recruiter response rates by up to 40%."
            })

        if data.get("github_url") or data.get("portfolio_url"):
            score += 1.5
        else:
            suggestions.append({
                "type": "info",
                "priority": "Low",
                "category": "Contact Info",
                "title": "Add Portfolio or GitHub Link",
                "message": "Add a link to your GitHub or personal portfolio site to showcase your projects."
            })

        return min(10.0, score), suggestions

    def _score_skills(self, data: Dict[str, Any]) -> tuple[float, List[Dict[str, str]]]:
        skills = data.get("skills", [])
        num_skills = len(skills)
        suggestions = []

        if num_skills >= 12:
            score = 20.0
        elif num_skills >= 8:
            score = 16.0
        elif num_skills >= 4:
            score = 10.0
            suggestions.append({
                "type": "warning",
                "priority": "Medium",
                "category": "Skills",
                "title": "Add More Technical & Soft Skills",
                "message": f"Only {num_skills} skills detected. Aim for at least 10–15 relevant skills to improve ATS keyword matching."
            })
        else:
            score = 4.0
            suggestions.append({
                "type": "error",
                "priority": "High",
                "category": "Skills",
                "title": "Low Skill Density",
                "message": "Fewer than 4 skills detected. Group your technical skills into clear categories."
            })

        return score, suggestions

    def _score_experience(self, data: Dict[str, Any]) -> tuple[float, List[Dict[str, str]]]:
        exp = data.get("experience", [])
        num_exp = len(exp)
        suggestions = []

        if num_exp >= 2:
            score = 15.0
        elif num_exp == 1:
            score = 10.0
            suggestions.append({
                "type": "info",
                "priority": "Medium",
                "category": "Experience",
                "title": "Detail Multiple Experiences",
                "message": "If applicable, include internships, research projects, or contract work to flesh out your timeline."
            })
        else:
            score = 3.0
            suggestions.append({
                "type": "warning",
                "priority": "High",
                "category": "Experience",
                "title": "No Work Experience Found",
                "message": "Add a dedicated Work Experience section with job titles, dates, and bulleted achievements."
            })

        return score, suggestions

    def _score_education(self, data: Dict[str, Any]) -> tuple[float, List[Dict[str, str]]]:
        edu = data.get("education", [])
        suggestions = []

        if edu:
            score = 10.0
        else:
            score = 2.0
            suggestions.append({
                "type": "warning",
                "priority": "High",
                "category": "Education",
                "title": "Missing Education Section",
                "message": "Add your degree name, university, and graduation year under an Education section."
            })

        return score, suggestions

    def _score_projects(self, data: Dict[str, Any]) -> tuple[float, List[Dict[str, str]]]:
        proj = data.get("projects", [])
        suggestions = []

        if len(proj) >= 2:
            score = 10.0
        elif len(proj) == 1:
            score = 7.0
            suggestions.append({
                "type": "info",
                "priority": "Low",
                "category": "Projects",
                "title": "Add Additional Projects",
                "message": "Highlighting 2-3 technical projects demonstrates hands-on implementation capabilities."
            })
        else:
            score = 4.0
            suggestions.append({
                "type": "info",
                "priority": "Medium",
                "category": "Projects",
                "title": "No Projects Section Detected",
                "message": "Include 2 key technical projects with technologies used and bullet points outlining achievements."
            })

        return score, suggestions

    def _score_certifications(self, data: Dict[str, Any]) -> tuple[float, List[Dict[str, str]]]:
        certs = data.get("certifications", [])
        suggestions = []

        if certs:
            score = 10.0
        else:
            score = 5.0
            suggestions.append({
                "type": "info",
                "priority": "Low",
                "category": "Certifications",
                "title": "Add Relevant Certifications",
                "message": "Cloud, AI, or industry certifications (e.g. AWS, Azure, GCP, CKA) help boost recruiter confidence."
            })

        return score, suggestions

    def _score_action_verbs(self, data: Dict[str, Any]) -> tuple[float, List[Dict[str, str]]]:
        raw_text = data.get("raw_text", "").lower()
        words = re.findall(r'\b[a-z]+\b', raw_text)
        suggestions = []

        found_verbs = set(words).intersection(ACTION_VERBS)
        num_verbs = len(found_verbs)

        if num_verbs >= 8:
            score = 10.0
        elif num_verbs >= 4:
            score = 7.0
            suggestions.append({
                "type": "info",
                "priority": "Medium",
                "category": "Action Verbs",
                "title": "Use Strong Action Verbs",
                "message": f"Found {num_verbs} strong action verbs. Replace passive phrasing with verbs like 'Spearheaded', 'Engineered', 'Optimized'."
            })
        else:
            score = 3.0
            suggestions.append({
                "type": "warning",
                "priority": "High",
                "category": "Action Verbs",
                "title": "Lack of Impact Action Verbs",
                "message": "Begin bullet points in Experience and Projects with active, quantitative action verbs."
            })

        return score, suggestions

    def _score_keyword_density(self, data: Dict[str, Any]) -> tuple[float, List[Dict[str, str]]]:
        text_length = len(data.get("raw_text", "").split())
        suggestions = []

        if 250 <= text_length <= 800:
            score = 5.0
        elif text_length < 250:
            score = 2.5
            suggestions.append({
                "type": "warning",
                "priority": "Medium",
                "category": "Keyword Density",
                "title": "Resume Too Short",
                "message": "Your resume contains under 250 words. Expand on responsibilities and project details."
            })
        else:
            score = 3.5
            suggestions.append({
                "type": "info",
                "priority": "Low",
                "category": "Keyword Density",
                "title": "Resume May Be Too Lengthy",
                "message": "Resumes over 800 words may be harder for hiring managers to scan quickly."
            })

        return score, suggestions

    def _score_formatting(self, data: Dict[str, Any]) -> tuple[float, List[Dict[str, str]]]:
        raw_text = data.get("raw_text", "")
        suggestions = []
        score = 5.0

        # Check for bad characters or tables/special symbols
        if raw_text.count("?") > 25:
            score -= 1.5
            suggestions.append({
                "type": "warning",
                "priority": "Medium",
                "category": "Formatting",
                "title": "Special Symbol Artifacts Detected",
                "message": "Avoid non-standard bullet symbols or complex tables that cause text extraction artifacts."
            })

        return max(1.0, score), suggestions

    def _score_section_completeness(self, data: Dict[str, Any]) -> tuple[float, List[Dict[str, str]]]:
        required_sections = ["summary", "skills", "experience", "education", "projects"]
        present_count = 0
        suggestions = []

        for sec in required_sections:
            if data.get(sec):
                present_count += 1
            else:
                suggestions.append({
                    "type": "warning",
                    "priority": "Medium",
                    "category": "Section Check",
                    "title": f"Missing Section: {sec.title()}",
                    "message": f"Ensure a distinct '{sec.title()}' header exists for proper ATS parsing."
                })

        score = (present_count / len(required_sections)) * 5.0
        return round(score, 1), suggestions
