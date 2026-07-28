"""
JD-Aware Resume Rewriter & Tailoring Engine.
Uses hybrid Rule-Based NLP + LLM Fallback (Groq/OpenAI) with HARD CONSTRAINTS,
Guardrail 1x Retry + Safe Fallback to prevent content fabrication.
"""

import json
import os
import re
from typing import Any, Dict, List, Optional
import docx

from resume_parser import SKILL_TAXONOMY

# Weak/Passive verb replacement taxonomy
WEAK_VERB_MAP = {
    r'\bresponsible for\b': 'Led and executed',
    r'\bin charge of\b': 'Spearheaded and directed',
    r'\bworked on\b': 'Engineered and delivered',
    r'\bassisted with\b': 'Contributed to',
    r'\bassisted in\b': 'Contributed to',
    r'\bhelped with\b': 'Collaborated on',
    r'\bparticipated in\b': 'Contributed actively to',
    r'\blooked after\b': 'Supervised and maintained',
    r'\bworked with\b': 'Leveraged',
    r'\bhandled\b': 'Orchestrated and managed',
    r'\bdid\b': 'Executed',
    r'\bmade\b': 'Architected'
}


class ResumeRewriter:
    """Production JD-Aware Resume Rewriter & Tailoring Engine."""

    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
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
    ) -> Optional[Dict[str, Any]]:
        """
        Hybrid Routing Engine:
        1. If bullet contains known weak verb patterns, attempt deterministic Rule Engine.
        2. If bullet has no weak verbs or rule engine makes no changes, AND LLM API key is present:
           -> Route to LLM Engine for nuanced rewriting.
        3. Enforce strict Guardrail with Retry + Fallback.
        """
        has_weak_verb = any(re.search(pat, original_bullet, re.IGNORECASE) for pat in WEAK_VERB_MAP.keys())

        # 1. Route to Rule Engine if explicit weak verb patterns exist
        if has_weak_verb:
            rule_result = self._generate_rule_based_rewrite(
                original_bullet, context_label, section, candidate_skills, candidate_raw, jd_skills
            )
            if rule_result and rule_result["rewritten_bullet"].strip() != original_bullet.strip():
                return rule_result

        # 2. Route to LLM Fallback for bullets with no weak verbs (nuanced/complex phrasing)
        if self.groq_api_key or self.openai_api_key:
            llm_result = self.execute_llm_with_guardrail_retry(
                original_bullet=original_bullet,
                context_label=context_label,
                section=section,
                candidate_skills=candidate_skills,
                candidate_raw=candidate_raw,
                job_description=job_description
            )
            if llm_result:
                return llm_result

        # 3. Fallback to Rule Engine or original bullet if no LLM key available
        return self._generate_rule_based_rewrite(
            original_bullet, context_label, section, candidate_skills, candidate_raw, jd_skills
        )

    def execute_llm_with_guardrail_retry(
        self,
        original_bullet: str,
        context_label: str,
        section: str,
        candidate_skills: set,
        candidate_raw: str,
        job_description: str
    ) -> Dict[str, Any]:
        """
        Executes LLM rewrite with strict Guardrail verification & 1x Retry + Safe Fallback.
        Protocol:
        1. Attempt 1: Call LLM with standard system prompt.
        2. Validate Attempt 1 using `validate_no_fabrication`.
           - IF SAFE -> Return LLM result (`source="llm"`).
           - IF UNSAFE / REJECTED -> Proceed to Attempt 2.
        3. Attempt 2 (Retry): Call LLM with ULTRA-STRICT system prompt explicitly warning against extra metrics/skills.
        4. Validate Attempt 2.
           - IF SAFE -> Return LLM result (`source="llm_retry"`).
           - IF UNSAFE -> Fall back to original bullet unedited (`source="llm_rejected_fallback"`), NEVER returning a hallucinated/unsafe bullet!
        """
        # Attempt 1: Standard LLM call
        attempt1 = self._try_llm_rewrite(
            original_bullet, context_label, candidate_skills, job_description, strict_retry=False
        )
        if attempt1 and "rewritten_bullet" in attempt1:
            rewritten_text = attempt1["rewritten_bullet"]
            if self.validate_no_fabrication(original_bullet, rewritten_text, candidate_skills, candidate_raw):
                kw_llm = attempt1.get("keywords_added", [])
                kw_detected = self._detect_added_keywords(original_bullet, rewritten_text, candidate_skills)
                combined_keywords = self._normalize_and_dedupe_keywords(kw_llm + kw_detected)

                # Over-stuffing Guardrail: Reject if more than 1 keyword was added to a single bullet
                if len(combined_keywords) <= 1:
                    return {
                        "section": section,
                        "context_label": context_label,
                        "original_bullet": original_bullet,
                        "rewritten_bullet": rewritten_text,
                        "reason": attempt1.get("reason", "AI-optimized impact & JD alignment"),
                        "keywords_added": combined_keywords,
                        "source": "llm",
                        "status": "suggested"
                    }
                else:
                    print(f"[REWRITER GUARDRAIL] LLM Attempt 1 rejected for keyword-stuffing ({len(combined_keywords)} skills added: {combined_keywords}). Retrying...")

        # Attempt 2: Stricter Retry Prompt if Attempt 1 was rejected or failed
        print(f"[REWRITER GUARDRAIL] LLM Attempt 1 rejected for: '{original_bullet}'. Retrying with strict prompt...")
        attempt2 = self._try_llm_rewrite(
            original_bullet, context_label, candidate_skills, job_description, strict_retry=True
        )
        if attempt2 and "rewritten_bullet" in attempt2:
            rewritten_text = attempt2["rewritten_bullet"]
            if self.validate_no_fabrication(original_bullet, rewritten_text, candidate_skills, candidate_raw):
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
                else:
                    print(f"[REWRITER GUARDRAIL] LLM Attempt 2 rejected for keyword-stuffing ({len(combined_keywords)} skills added: {combined_keywords}). Falling back to original bullet.")

        # Final Safe Fallback: Return original bullet unedited if LLM output fails safety guardrails twice
        print(f"[REWRITER GUARDRAIL] LLM Attempt 2 rejected for: '{original_bullet}'. Falling back to original bullet unedited.")
        return {
            "section": section,
            "context_label": context_label,
            "original_bullet": original_bullet,
            "rewritten_bullet": original_bullet,
            "reason": "LLM rewrite output rejected by safety guardrail (reverted to original unedited text)",
            "keywords_added": [],
            "source": "llm_rejected_fallback",
            "status": "suggested"
        }

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

        system_prompt = (
            "You are an expert ATS Resume Rewriter. Your job is to rewrite bullet points from a candidate's resume to improve impact and alignment with a Job Description.\n"
            "STRICT HARD CONSTRAINTS:\n"
            "1. NEVER invent or fabricate fake metrics, numbers, percentages, dollar amounts, or work experience not in the original bullet.\n"
            "2. NEVER introduce technical skills not listed in candidate verified skills.\n"
            "3. MAXIMUM 1 KEYWORD INSERTION PER BULLET. Do NOT stuff multiple technologies into one sentence. Only insert a skill if the bullet's existing context explicitly supports it.\n"
            "4. If no single skill fits naturally, do NOT insert any skills; simply refine the action verbs and clarity."
        )

        if strict_retry:
            system_prompt += (
                "\n\nCRITICAL MANDATE: Your previous attempt was REJECTED for introducing unverified metrics or keyword-stuffing! "
                "In this attempt, do NOT add ANY numbers, percentages, or more than ONE technical skill! "
                "Only rephrase the action verbs and sentence structure."
            )

        prompt = f"""
Candidate Verified Skills: {', '.join(list(candidate_skills)[:15])}
Context: {context_label}
Original Bullet Point: "{original_bullet}"
Target Job Description: "{job_description[:300]}"

Output JSON format:
{{"rewritten_bullet": "...", "reason": "...", "keywords_added": ["Skill1", "Skill2"]}}
"""

        # Try Groq API
        if self.groq_api_key:
            try:
                from groq import Groq
                client = Groq(api_key=self.groq_api_key)
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                return json.loads(completion.choices[0].message.content)
            except Exception as e:
                print(f"[LLM ERROR] Groq API call failed: {e}")

        # Try OpenAI API
        if self.openai_api_key:
            try:
                import openai
                client = openai.OpenAI(api_key=self.openai_api_key)
                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                return json.loads(completion.choices[0].message.content)
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
    ) -> Optional[Dict[str, Any]]:
        """Rule-based NLP rewriter for weak verb replacement & contextual keyword alignment."""
        rewritten = original_bullet
        reason_parts = []
        keywords_added = []

        # 1. Weak verb replacement - scan and replace ALL matching patterns in the bullet
        replaced_any = False
        for pattern, replacement in WEAK_VERB_MAP.items():
            if re.search(pattern, rewritten, re.IGNORECASE):
                rewritten = re.sub(pattern, replacement, rewritten, flags=re.IGNORECASE)
                replaced_any = True

        if replaced_any:
            reason_parts.append("Upgraded passive phrasing to strong action verbs")

        # 2. Ensure proper capitalization for all sentences
        rewritten = self._capitalize_sentences(rewritten)

        # 3. Contextual keyword integration (ONLY if candidate possesses the skill)
        matching_jd_skills = jd_skills.intersection(candidate_skills)
        for skill in matching_jd_skills:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if not re.search(pattern, rewritten, re.IGNORECASE):
                skill_cap = self._capitalize_skill(skill)
                if len(rewritten.split()) < 30:
                    rewritten_clean = rewritten.rstrip('.')
                    rewritten = f"{rewritten_clean} utilizing {skill_cap}."
                    keywords_added.append(skill_cap)
                    reason_parts.append(f"Aligned possessed skill '{skill_cap}' with Job Description")
                    break

        # Ensure trailing period
        if not rewritten.endswith('.'):
            rewritten += '.'

        if rewritten.strip() == original_bullet.strip():
            words = original_bullet.split()
            if words and not any(words[0].lower().endswith(e) for e in ["ed", "ed.", "ing"]):
                rewritten = f"Engineered and executed {original_bullet[0].lower() + original_bullet[1:]}"
                if not rewritten.endswith('.'):
                    rewritten += '.'
                reason_parts.append("Enhanced bullet structure with active impact verb")

        # Hard guardrail check
        if not self.validate_no_fabrication(original_bullet, rewritten, candidate_skills, candidate_raw):
            return None

        return {
            "section": section,
            "context_label": context_label,
            "original_bullet": original_bullet,
            "rewritten_bullet": rewritten,
            "reason": "; ".join(reason_parts) if reason_parts else "Refined impact phrasing",
            "keywords_added": keywords_added,
            "source": "rule_engine",
            "status": "suggested"
        }

    def _capitalize_sentences(self, text: str) -> str:
        """Helper to ensure sentences start with a capital letter."""
        if not text:
            return text
        parts = text.split('. ')
        cap_parts = []
        for p in parts:
            p_strip = p.strip()
            if p_strip:
                cap_parts.append(p_strip[0].upper() + p_strip[1:])
        return '. '.join(cap_parts)

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
