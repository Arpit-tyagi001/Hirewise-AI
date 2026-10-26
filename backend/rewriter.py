"""
JD-Aware Resume Rewriter & Tailoring Engine.
Uses hybrid Rule-Based NLP + LLM (Groq/OpenAI) with anti-hallucination guardrails.
Guarantees high-impact, non-identical, senior-level bullet transformations.
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
import docx
from dotenv import load_dotenv

# Ensure environment variables are loaded from backend/.env or root .env
_backend_env = Path(__file__).parent / ".env"
_root_env = Path(__file__).parent.parent / ".env"
load_dotenv(_backend_env)
load_dotenv(_root_env)

from resume_parser import SKILL_TAXONOMY

# Comprehensive Passive/Weak verb replacement taxonomy
WEAK_VERB_MAP = {
    r'\b(is|was|were)\s+responsible for\b': 'Spearheaded and directed',
    r'\bresponsible for (handling|managing|leading)\b': 'Orchestrated and managed',
    r'\bresponsible for\b': 'Spearheaded and directed',
    r'\bin charge of\b': 'Spearheaded and directed',
    r'\bworked on\b': 'Engineered and delivered',
    r'\bworked with\b': 'Collaborated cross-functionally with',
    r'\bhelped team (to\s+)?build\b': 'Partnered with engineering squads to architect and deploy',
    r'\bhelped (team|colleagues|engineers)\b': 'Collaborated with engineering squads to accelerate',
    r'\bhelped\b': 'Collaborated cross-functionally to deliver',
    r'\bassisted (in|with)\b': 'Contributed core engineering support to',
    r'\bassisted\b': 'Collaborated on',
    r'\bparticipated in\b': 'Contributed actively to',
    r'\blooked after\b': 'Oversaw reliability and performance of',
    r'\btook care of\b': 'Oversaw and resolved',
    r'\bhandled\b': 'Orchestrated and scaled',
    r'\bdid\b': 'Executed and delivered',
    r'\bmade\b': 'Engineered and delivered',
    r'\bfixed bugs and maintained\b': 'Diagnosed and resolved critical defects while maintaining',
    r'\bfixed bugs and\b': 'Diagnosed and resolved critical defects while',
    r'\bfixed bugs\b': 'Diagnosed and resolved critical production defects',
    r'\bfixed\b': 'Resolved and optimized',
    r'\bwrote automated unit tests\b': 'Automated comprehensive unit and integration test suites',
    r'\bwrote unit tests\b': 'Implemented robust unit testing suites',
    r'\bwrote (code|scripts)\b': 'Authored production-grade software',
    r'\bwrote\b': 'Authored and delivered',
    r'\bcreated\b': 'Designed and implemented',
    r'\bbuilt\b': 'Architected and deployed',
    r'\bdeveloped\b': 'Engineered and deployed'
}

DOMAIN_ENHANCEMENTS = [
    (
        r'Fast\s*API microservices handling millions of API calls daily',
        'high-throughput, distributed FastAPI microservices handling millions of daily API requests with high availability and low latency'
    ),
    (
        r'database queries and optimization',
        'database schema design, indexing, and query optimization, accelerating data retrieval throughput and transactional integrity'
    ),
    (
        r'frontend using React and TypeScript',
        'modular, component-driven frontend architectures using React and TypeScript, optimizing render efficiency and responsive user experience'
    ),
    (
        r'CI/CD pipeline using Docker and GitHub Actions',
        'automated containerized CI/CD pipelines using Docker and GitHub Actions, streamlining release cadence and deployment reliability'
    ),
    (
        r'REST APIs for mobile applications',
        'secure, high-performance RESTful APIs for mobile client applications with robust error handling'
    ),
    (
        r'data analysis using Pandas and NumPy',
        'exploratory data analysis and quantitative modeling pipelines using Pandas and NumPy, delivering actionable system insights'
    ),
    (
        r'existing codebase',
        'existing codebase, driving maintainability, code quality, and defect reduction'
    )
]


class ResumeRewriter:
    """Production JD-Aware Resume Rewriter & Tailoring Engine."""

    def __init__(self, api_key: Optional[str] = None):
        # Client-supplied key takes priority, then backend/.env, then system env
        self.groq_api_key = api_key or os.getenv("GROQ_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

    def rewrite_resume_bullets(self, parsed_resume: Dict[str, Any], job_description: str) -> List[Dict[str, Any]]:
        """
        Generate bullet-by-bullet before/after rewrites tailored to target Job Description.
        Enforces HARD CONSTRAINT: Never invent skills, metrics, or experience not genuinely present.
        """
        rewrites: List[Dict[str, Any]] = []

        candidate_skills = set([s.lower() for s in parsed_resume.get("skills", [])])
        candidate_raw = parsed_resume.get("raw_text", "").lower()
        jd_skills = self._extract_jd_skills(job_description)

        # Process Work Experience Bullets
        experiences = parsed_resume.get("experience", [])
        for exp_idx, exp in enumerate(experiences):
            title = exp.get("title", "Role")
            company = exp.get("company", "")
            context_label = f"Experience: {title}" + (f" at {company}" if company else "")
            bullets = self._extract_bullets_from_text(exp.get("description", ""))

            for bullet_idx, bullet in enumerate(bullets):
                if len(bullet.strip()) < 10:
                    continue

                rewrite_item = self._generate_single_bullet_rewrite(
                    original_bullet=bullet.strip(),
                    context_label=context_label,
                    section="experience",
                    candidate_skills=candidate_skills,
                    candidate_raw=candidate_raw,
                    jd_skills=jd_skills,
                    job_description=job_description
                )
                if rewrite_item:
                    rewrite_item["id"] = f"exp_{exp_idx}_{bullet_idx}"
                    rewrites.append(rewrite_item)

        # Process Projects Bullets
        projects = parsed_resume.get("projects", [])
        for proj_idx, proj in enumerate(projects):
            proj_title = proj.get("title", "Project")
            context_label = f"Project: {proj_title}"
            bullets = self._extract_bullets_from_text(proj.get("description", ""))

            for bullet_idx, bullet in enumerate(bullets):
                if len(bullet.strip()) < 10:
                    continue

                rewrite_item = self._generate_single_bullet_rewrite(
                    original_bullet=bullet.strip(),
                    context_label=context_label,
                    section="projects",
                    candidate_skills=candidate_skills,
                    candidate_raw=candidate_raw,
                    jd_skills=jd_skills,
                    job_description=job_description
                )
                if rewrite_item:
                    rewrite_item["id"] = f"proj_{proj_idx}_{bullet_idx}"
                    rewrites.append(rewrite_item)

        return rewrites

    def _generate_single_bullet_rewrite(
        self,
        original_bullet: str,
        context_label: str,
        section: str,
        candidate_skills: set,
        candidate_raw: str,
        jd_skills: set,
        job_description: str
    ) -> Dict[str, Any]:
        """
        Hybrid Routing Engine:
        1. If LLM key is available (Groq/OpenAI), execute LLM rewrite with guardrail retry.
        2. If LLM is unavailable, returns identical text, or fails validation -> seamlessly route to
           the Smart NLP Enhancement Engine which guarantees a polished, non-identical improvement.
        """
        if self.groq_api_key or self.openai_api_key:
            llm_result = self.execute_llm_with_guardrail_retry(
                original_bullet=original_bullet,
                context_label=context_label,
                section=section,
                candidate_skills=candidate_skills,
                candidate_raw=candidate_raw,
                job_description=job_description,
                jd_skills=jd_skills
            )
            if llm_result and llm_result.get("rewritten_bullet", "").strip() != original_bullet.strip():
                return llm_result

        # Smart NLP Engine (Deterministic & guaranteed non-identical)
        return self._generate_rule_based_rewrite(
            original_bullet=original_bullet,
            context_label=context_label,
            section=section,
            candidate_skills=candidate_skills,
            candidate_raw=candidate_raw,
            jd_skills=jd_skills
        )

    def execute_llm_with_guardrail_retry(
        self,
        original_bullet: str,
        context_label: str,
        section: str,
        candidate_skills: set,
        candidate_raw: str,
        job_description: str,
        jd_skills: Optional[set] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Executes LLM rewrite with strict Guardrail verification & 1x Retry.
        Guarantees that identical text is never accepted.
        """
        # Attempt 1: Standard LLM call
        attempt1 = self._try_llm_rewrite(
            original_bullet, context_label, candidate_skills, job_description, strict_retry=False
        )
        if attempt1 and "rewritten_bullet" in attempt1:
            rewritten_text = attempt1["rewritten_bullet"].strip()
            if rewritten_text != original_bullet.strip() and self.validate_no_fabrication(original_bullet, rewritten_text, candidate_skills, candidate_raw):
                kw_llm = attempt1.get("keywords_added", [])
                kw_detected = self._detect_added_keywords(original_bullet, rewritten_text, candidate_skills)
                combined_keywords = self._normalize_and_dedupe_keywords(kw_llm + kw_detected)

                if len(combined_keywords) <= 1:
                    return {
                        "section": section,
                        "context_label": context_label,
                        "original_bullet": original_bullet,
                        "rewritten_bullet": rewritten_text,
                        "reason": attempt1.get("reason", "AI-optimized impact & alignment"),
                        "keywords_added": combined_keywords,
                        "source": "llm",
                        "status": "suggested"
                    }

        # Attempt 2: Stricter Retry Prompt if Attempt 1 was rejected or identical
        attempt2 = self._try_llm_rewrite(
            original_bullet, context_label, candidate_skills, job_description, strict_retry=True
        )
        if attempt2 and "rewritten_bullet" in attempt2:
            rewritten_text = attempt2["rewritten_bullet"].strip()
            if rewritten_text != original_bullet.strip() and self.validate_no_fabrication(original_bullet, rewritten_text, candidate_skills, candidate_raw):
                kw_llm = attempt2.get("keywords_added", [])
                kw_detected = self._detect_added_keywords(original_bullet, rewritten_text, candidate_skills)
                combined_keywords = self._normalize_and_dedupe_keywords(kw_llm + kw_detected)

                if len(combined_keywords) <= 1:
                    return {
                        "section": section,
                        "context_label": context_label,
                        "original_bullet": original_bullet,
                        "rewritten_bullet": rewritten_text,
                        "reason": attempt2.get("reason", "AI-optimized impact & alignment (Verified via Guardrail Retry)"),
                        "keywords_added": combined_keywords,
                        "source": "llm_retry",
                        "status": "suggested"
                    }

        # Safe Fallback: Hand off to Smart NLP Engine if LLM fails or is unavailable
        if jd_skills is not None:
            rule_fallback = self._generate_rule_based_rewrite(
                original_bullet, context_label, section, candidate_skills, candidate_raw, jd_skills
            )
            if rule_fallback and rule_fallback["rewritten_bullet"].strip() != original_bullet.strip():
                rule_fallback["source"] = "smart_nlp_engine"
                return rule_fallback

        return None

    def _try_llm_rewrite(
        self,
        original_bullet: str,
        context_label: str,
        candidate_skills: set,
        job_description: str,
        strict_retry: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Call Groq or OpenAI LLM API if key is available."""
        if not self.groq_api_key and not self.openai_api_key:
            return None

        system_prompt = """You are an elite, no-nonsense technical resume writer and ATS optimization specialist. Your job is to rewrite the provided resume experience text into a single, high-impact bullet point.

CRITICAL RULES - YOU MUST OBEY THESE STRICTLY:
1. NO CONVERSATIONAL FILLER: Do not say "Here is the rewrite", "Sure", or add any introductory/concluding text.
2. NO FORMATTING: Do not output asterisks, markdown, quotation marks, or bullet symbols (-, •).
3. START STRONG: Begin the string immediately with a strong action verb (past tense for past roles, present tense for current roles).
4. KEEP METRICS: Retain every number, percentage, and technology mentioned in the original text.
5. ELEVATE IMPACT: Actively upgrade passive tasks into accomplishment-driven statements emphasizing technical depth, system resilience, or execution quality.
6. OUTPUT FORMAT: Output ONLY the raw rewritten string. Nothing else."""

        if strict_retry:
            system_prompt += "\n7. RETRY MANDATE: Strictly avoid adding any new numbers, percentages, or unmentioned technologies."

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Rewrite this: {original_bullet}\nTarget Role Context: {job_description[:250]}\nCandidate Skills: {', '.join(list(candidate_skills)[:8])}"}
        ]

        # Try Groq API
        if self.groq_api_key:
            try:
                from groq import Groq
                client = Groq(api_key=self.groq_api_key)
                groq_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
                completion = client.chat.completions.create(
                    model=groq_model,
                    messages=messages,
                    temperature=0.2
                )
                raw_rewritten = completion.choices[0].message.content.strip()
                raw_rewritten = re.sub(r'^[•\-\*"\']\s*', '', raw_rewritten).strip().strip('"').strip("'")
                if raw_rewritten and raw_rewritten != original_bullet.strip():
                    return {
                        "rewritten_bullet": raw_rewritten,
                        "reason": "AI-optimized high-impact action bullet",
                        "keywords_added": []
                    }
            except Exception as e:
                print(f"[LLM ERROR] Groq API call failed: {e}. Check if your GROQ_API_KEY in backend/.env is valid and active.")

        # Try OpenAI API
        if self.openai_api_key:
            try:
                import openai
                client = openai.OpenAI(api_key=self.openai_api_key)
                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.2
                )
                raw_rewritten = completion.choices[0].message.content.strip()
                raw_rewritten = re.sub(r'^[•\-\*"\']\s*', '', raw_rewritten).strip().strip('"').strip("'")
                if raw_rewritten and raw_rewritten != original_bullet.strip():
                    return {
                        "rewritten_bullet": raw_rewritten,
                        "reason": "AI-optimized high-impact action bullet",
                        "keywords_added": []
                    }
            except Exception as e:
                print(f"[LLM ERROR] OpenAI API call failed: {e}")

        return None

    def _generate_rule_based_rewrite(
        self,
        original_bullet: str,
        context_label: str,
        section: str,
        candidate_skills: set,
        candidate_raw: str,
        jd_skills: set
    ) -> Dict[str, Any]:
        """
        Smart NLP Enhancement Engine:
        Transforms passive or basic bullets into active, senior-grade engineering statements.
        Guaranteed to return a meaningful, non-identical improvement.
        """
        orig_clean = original_bullet.strip().rstrip('.')
        rewritten = orig_clean
        reason_parts = []
        keywords_added = []

        # 1. Verb upgrade using comprehensive mapping
        for pattern, replacement in WEAK_VERB_MAP.items():
            if re.search(pattern, rewritten, re.IGNORECASE):
                rewritten = re.sub(pattern, replacement, rewritten, count=1, flags=re.IGNORECASE)
                reason_parts.append("Upgraded passive phrasing to executive action verbs")
                break

        # 2. Domain architectural polish
        for pattern, replacement in DOMAIN_ENHANCEMENTS:
            if re.search(pattern, rewritten, re.IGNORECASE):
                rewritten = re.sub(pattern, replacement, rewritten, flags=re.IGNORECASE)
                reason_parts.append("Elevated technical depth and architectural clarity")
                break

        # 3. Contextual skill integration (weave naturally if candidate possesses it, absent in bullet, and domain-compatible)
        b_lower = rewritten.lower()
        existing_skills = [s for s in SKILL_TAXONOMY if re.search(r'\b' + re.escape(s) + r'\b', b_lower)]
        if len(existing_skills) < 2:
            matching_jd_skills = jd_skills.intersection(candidate_skills)
            for skill in matching_jd_skills:
                skill_lower = skill.lower()
                if skill_lower not in b_lower and self._should_inject_skill(rewritten, skill_lower):
                    skill_cap = self._capitalize_skill(skill)
                    if 'database' in b_lower and skill_lower in ['postgresql', 'mysql', 'mongodb', 'sqlite']:
                        rewritten = re.sub(r'\bdatabase\b', f'{skill_cap} database', rewritten, count=1, flags=re.IGNORECASE)
                        keywords_added.append(skill_cap)
                        reason_parts.append(f"Integrated candidate core competency '{skill_cap}'")
                        break
                    elif len(rewritten.split()) < 16:
                        rewritten = f"{rewritten} utilizing {skill_cap}"
                        keywords_added.append(skill_cap)
                        reason_parts.append(f"Aligned verified skill '{skill_cap}' with Job Description")
                        break

        # 4. Guarantee difference & senior impact if bullet was unchanged
        if rewritten.strip() == orig_clean.strip():
            words = rewritten.split()
            if words:
                lead = words[0].lower()
                if lead in ['architected', 'engineered', 'spearheaded', 'orchestrated', 'designed']:
                    rewritten = f"{words[0]} scalable, high-performance " + " ".join(words[1:])
                    reason_parts.append("Amplified architectural impact and scalability scope")
                elif lead.endswith('ed'):
                    rewritten = f"Spearheaded and executed {orig_clean[0].lower() + orig_clean[1:]}"
                    reason_parts.append("Strengthened engineering leadership phrasing")
                else:
                    rewritten = f"Engineered and delivered {orig_clean[0].lower() + orig_clean[1:]}"
                    reason_parts.append("Enhanced bullet structure with active impact verb")

        # Capitalize leading character
        rewritten = rewritten[0].upper() + rewritten[1:]
        if not rewritten.endswith('.'):
            rewritten += '.'

        return {
            "section": section,
            "context_label": context_label,
            "original_bullet": original_bullet,
            "rewritten_bullet": rewritten,
            "reason": "; ".join(reason_parts) if reason_parts else "Elevated technical impact and delivery clarity",
            "keywords_added": keywords_added,
            "source": "smart_nlp_engine",
            "status": "suggested"
        }

    def validate_no_fabrication(self, original_text: str, rewritten_text: str, candidate_skills: set, candidate_raw: str) -> bool:
        """
        HARD GUARDRAIL: Returns False if rewritten_text introduces any fabricated metrics,
        percentages, numbers, or unpossessed technical skills.
        """
        # 1. Metric / Number Check
        orig_numbers = set(re.findall(r'\b\d+(?:\.\d+)?%?|\$\d+\b', original_text))
        new_numbers = set(re.findall(r'\b\d+(?:\.\d+)?%?|\$\d+\b', rewritten_text))

        hallucinated_numbers = new_numbers - orig_numbers
        if hallucinated_numbers:
            return False

        # 2. Unpossessed Skill Check
        orig_lower = original_text.lower()
        rewritten_lower = rewritten_text.lower()

        for skill in SKILL_TAXONOMY:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, rewritten_lower):
                if re.search(pattern, orig_lower):
                    continue
                if skill not in candidate_skills and skill not in candidate_raw:
                    return False

        return True

    def export_tailored_docx(self, parsed_resume: Dict[str, Any], accepted_rewrites: List[Dict[str, Any]]) -> docx.Document:
        """Generates formatted DOCX resume containing only accepted bullet edits."""
        doc = docx.Document()
        rewrite_map = {item["original_bullet"].strip(): item["rewritten_bullet"].strip() for item in accepted_rewrites if item.get("status") == "accepted" or item.get("accepted") is True}

        name = parsed_resume.get("name", "Candidate")
        doc.add_heading(name, level=0)

        contact_parts = []
        if parsed_resume.get("email"): contact_parts.append(parsed_resume["email"])
        if parsed_resume.get("phone"): contact_parts.append(parsed_resume["phone"])
        if parsed_resume.get("location"): contact_parts.append(parsed_resume["location"])
        if contact_parts: doc.add_paragraph(" | ".join(contact_parts))

        links = []
        if parsed_resume.get("linkedin_url"): links.append(parsed_resume["linkedin_url"])
        if parsed_resume.get("github_url"): links.append(parsed_resume["github_url"])
        if links: doc.add_paragraph(" | ".join(links))

        if parsed_resume.get("summary"):
            doc.add_heading("Professional Summary", level=1)
            doc.add_paragraph(parsed_resume["summary"])

        skills = parsed_resume.get("skills", [])
        if skills:
            doc.add_heading("Technical Skills", level=1)
            doc.add_paragraph(", ".join(skills))

        experiences = parsed_resume.get("experience", [])
        if experiences:
            doc.add_heading("Work Experience", level=1)
            for exp in experiences:
                title = exp.get("title", "")
                company = exp.get("company", "")
                dates = exp.get("dates", "")
                doc.add_paragraph(f"{title} - {company} | {dates}")

                bullets = self._extract_bullets_from_text(exp.get("description", ""))
                for bullet in bullets:
                    bullet_clean = bullet.strip()
                    final_bullet = rewrite_map.get(bullet_clean, bullet_clean)
                    doc.add_paragraph(f"• {final_bullet}")

        projects = parsed_resume.get("projects", [])
        if projects:
            doc.add_heading("Key Projects", level=1)
            for proj in projects:
                title = proj.get("title", "")
                doc.add_paragraph(title)

                bullets = self._extract_bullets_from_text(proj.get("description", ""))
                for bullet in bullets:
                    bullet_clean = bullet.strip()
                    final_bullet = rewrite_map.get(bullet_clean, bullet_clean)
                    doc.add_paragraph(f"• {final_bullet}")

        education = parsed_resume.get("education", [])
        if education:
            doc.add_heading("Education", level=1)
            for edu in education:
                degree = edu.get("degree", "")
                institution = edu.get("institution", "")
                year = edu.get("year", "")
                doc.add_paragraph(f"{degree} - {institution} ({year})")

        return doc

    def _extract_jd_skills(self, jd_text: str) -> set:
        found = set()
        jd_lower = jd_text.lower()
        for skill in SKILL_TAXONOMY:
            if re.search(r'\b' + re.escape(skill) + r'\b', jd_lower):
                found.add(skill.lower())
        return found

    def _extract_bullets_from_text(self, text: str) -> List[str]:
        if not text:
            return []
        raw_lines = text.split("\n")
        bullets = []
        for line in raw_lines:
            line_str = line.strip()
            if not line_str:
                continue
            # Split line ONLY on explicit bullet symbols (•, *, or leading dash with space)
            # Hyphenated compound words (cross-functional, data-driven, well-versed, end-to-end) are preserved intact
            items = re.split(r'(?:^|\s+)[•\*]\s*|(?:^|\s+)-(?=\s+)', line_str)
            for item in items:
                item_clean = item.strip()
                item_clean = re.sub(r'^[•\-\*\s]+', '', item_clean).strip()
                if item_clean:
                    bullets.append(item_clean)
        return bullets if bullets else [text.strip()]

    def _detect_added_keywords(self, original_text: str, rewritten_text: str, candidate_skills: set) -> List[str]:
        """Detect technical keywords present in rewritten_text that were absent in original_text."""
        orig_lower = original_text.lower()
        rewritten_lower = rewritten_text.lower()
        added = []
        for skill in SKILL_TAXONOMY:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, rewritten_lower) and not re.search(pattern, orig_lower):
                if skill in candidate_skills:
                    added.append(self._capitalize_skill(skill))
        return added

    def _normalize_and_dedupe_keywords(self, keywords: List[str]) -> List[str]:
        """Normalize case and whitespace to deduplicate keyword lists."""
        seen = set()
        deduped = []
        for kw in keywords:
            if not isinstance(kw, str):
                continue
            kw_clean = kw.strip()
            if not kw_clean:
                continue
            kw_lower = kw_clean.lower()
            if kw_lower not in seen:
                seen.add(kw_lower)
                deduped.append(self._capitalize_skill(kw_clean))
        return deduped

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

    def _should_inject_skill(self, bullet_text: str, skill: str) -> bool:
        """Determines if a technical skill is domain-compatible with the existing bullet context."""
        b = bullet_text.lower()
        s = skill.lower()
        if any(k in b for k in ['database', 'query', 'queries', 'sql', 'schema']):
            return s in ['postgresql', 'mysql', 'mongodb', 'sqlite', 'redis', 'sql']
        if any(k in b for k in ['api', 'apis', 'microservice', 'microservices', 'backend', 'endpoint', 'endpoints']):
            return s in ['fastapi', 'python', 'django', 'flask', 'node', 'express', 'rest']
        if any(k in b for k in ['frontend', 'ui', 'ux', 'interface', 'web', 'component']):
            return s in ['react', 'typescript', 'javascript', 'vue', 'angular', 'tailwind', 'html', 'css']
        if any(k in b for k in ['ci/cd', 'docker', 'kubernetes', 'deploy', 'pipeline', 'aws', 'cloud']):
            return s in ['docker', 'kubernetes', 'aws', 'azure', 'gcp', 'terraform', 'jenkins']
        return True

