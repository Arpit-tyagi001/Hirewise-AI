"""
AI Interview Preparation Suite.
Generates tailored Technical, Skill Gap Strategy, and Behavioral STAR-method interview questions
based on the candidate's parsed resume and the target Job Description.
Supports dual Groq LLM + Smart Offline NLP Engine.
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

# Ensure environment variables are loaded
_backend_env = Path(__file__).parent / ".env"
_root_env = Path(__file__).parent.parent / ".env"
load_dotenv(_backend_env)
load_dotenv(_root_env)

from resume_parser import SKILL_TAXONOMY


class InterviewPrepGenerator:
    """Production Interview Preparation Engine."""

    def __init__(self, api_key: Optional[str] = None):
        self.groq_api_key = api_key or os.getenv("GROQ_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

    def generate(
        self,
        parsed_resume: Dict[str, Any],
        job_description: str
    ) -> Dict[str, Any]:
        """
        Generates structured interview questions and STAR answer frameworks.
        """
        candidate_skills = [s.lower() for s in parsed_resume.get("skills", [])]
        candidate_skills_set = set(candidate_skills)
        experiences = parsed_resume.get("experience", [])
        projects = parsed_resume.get("projects", [])

        # Extract JD skills & identify matching vs missing
        jd_skills = self._extract_jd_skills(job_description)
        matching_skills = sorted(list(jd_skills.intersection(candidate_skills_set)))
        missing_skills = sorted(list(jd_skills - candidate_skills_set))

        # 1. Try Groq or OpenAI LLM if key is available
        if self.groq_api_key or self.openai_api_key:
            llm_result = self._try_llm_interview_prep(
                parsed_resume=parsed_resume,
                job_description=job_description,
                matching_skills=matching_skills,
                missing_skills=missing_skills
            )
            if llm_result and "questions" in llm_result and len(llm_result["questions"]) > 0:
                return {
                    "success": True,
                    "matching_skills": [s.title() for s in matching_skills],
                    "missing_skills": [s.title() for s in missing_skills],
                    "total_questions": len(llm_result["questions"]),
                    "questions": llm_result["questions"],
                    "source": "llm"
                }

        # 2. Smart Offline Rule-Based Generator
        questions = self._generate_rule_based_prep(
            parsed_resume=parsed_resume,
            job_description=job_description,
            matching_skills=matching_skills,
            missing_skills=missing_skills
        )

        return {
            "success": True,
            "matching_skills": [s.title() for s in matching_skills],
            "missing_skills": [s.title() for s in missing_skills],
            "total_questions": len(questions),
            "questions": questions,
            "source": "smart_nlp_engine"
        }

    def _extract_jd_skills(self, jd_text: str) -> set:
        found = set()
        jd_lower = jd_text.lower()
        for skill in SKILL_TAXONOMY:
            if re.search(r'\b' + re.escape(skill) + r'\b', jd_lower):
                found.add(skill.lower())
        return found

    def _try_llm_interview_prep(
        self,
        parsed_resume: Dict[str, Any],
        job_description: str,
        matching_skills: List[str],
        missing_skills: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Call Groq / OpenAI to generate interview questions & STAR framework."""
        system_prompt = """You are an elite Silicon Valley Technical Interviewer & Engineering Hiring Manager.
Your job is to generate a personalized, rigorous interview preparation kit for this candidate based on their actual background and the target Job Description.

Generate 6-8 total questions covering 3 critical categories:
1. "technical": Architecture, system design, and deep technical decisions on technologies they possess.
2. "skill_gap": Specific questions testing missing or unmentioned competencies in the JD, giving strategy on how to pivot.
3. "behavioral": High-stakes situational engineering scenarios (production incidents, technical debates, roadmap pressure) using the STAR framework.

Output strictly valid JSON with this exact schema:
{
  "questions": [
    {
      "id": "q1",
      "category": "technical",
      "question": "...",
      "interviewer_intent": "What the interviewer is really testing",
      "star_framework": {
        "situation": "Context from candidate real profile",
        "task": "The technical objective",
        "action": "Specific engineering decisions and steps",
        "result": "Concrete outcome, metrics, or stability gain"
      },
      "key_talking_points": ["Point 1", "Point 2", "Point 3"]
    }
  ]
}"""

        skills = parsed_resume.get("skills", [])[:15]
        exps = [f"{e.get('title')} at {e.get('company')}: {e.get('description', '')[:180]}" for e in parsed_resume.get("experience", [])[:2]]
        projs = [f"{p.get('title')}: {p.get('description', '')[:150]}" for p in parsed_resume.get("projects", [])[:2]]

        user_prompt = f"""Candidate Skills: {', '.join(skills)}
Recent Roles:
{chr(10).join(exps)}
Key Projects:
{chr(10).join(projs)}
Target Job Description:
{job_description[:500]}
Identified Matching Skills: {', '.join(matching_skills[:8])}
Identified Missing JD Skills: {', '.join(missing_skills[:6])}

Generate the structured interview questions and STAR frameworks in JSON format:"""

        # Try Groq API
        if self.groq_api_key:
            try:
                from groq import Groq
                client = Groq(api_key=self.groq_api_key)
                groq_model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
                completion = client.chat.completions.create(
                    model=groq_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.2,
                    response_format={"type": "json_object"}
                )
                return json.loads(completion.choices[0].message.content)
            except Exception as e:
                print(f"[INTERVIEW PREP LLM] Groq API call failed: {e}")

        # Try OpenAI API
        if self.openai_api_key:
            try:
                import openai
                client = openai.OpenAI(api_key=self.openai_api_key)
                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.2,
                    response_format={"type": "json_object"}
                )
                return json.loads(completion.choices[0].message.content)
            except Exception as e:
                print(f"[INTERVIEW PREP LLM] OpenAI API call failed: {e}")

        return None

    def _generate_rule_based_prep(
        self,
        parsed_resume: Dict[str, Any],
        job_description: str,
        matching_skills: List[str],
        missing_skills: List[str]
    ) -> List[Dict[str, Any]]:
        """Smart deterministic interview prep generator."""
        questions: List[Dict[str, Any]] = []
        skills = parsed_resume.get("skills", [])
        experiences = parsed_resume.get("experience", [])
        projects = parsed_resume.get("projects", [])

        recent_exp = experiences[0] if experiences else None
        role_title = recent_exp.get("title", "Software Engineer") if recent_exp else "Software Engineer"
        role_company = recent_exp.get("company", "your previous organization") if recent_exp else "your previous company"

        q_idx = 1

        # 1. Technical Deep-Dive Questions
        primary_skill = matching_skills[0].title() if matching_skills else (skills[0].title() if skills else "System Architecture")
        secondary_skill = matching_skills[1].title() if len(matching_skills) > 1 else (skills[1].title() if len(skills) > 1 else "Database Design")

        questions.append({
            "id": f"q_{q_idx}",
            "category": "technical",
            "question": f"In your role as {role_title} at {role_company}, how did you design and optimize systems utilizing {primary_skill} to handle scale, latency, and fault tolerance?",
            "interviewer_intent": f"Tests senior technical mastery of {primary_skill}, architectural trade-offs, and practical understanding of distributed resilience.",
            "star_framework": {
                "situation": f"At {role_company}, our core services experienced scaling challenges and growing request throughput requiring {primary_skill} optimization.",
                "task": f"Architect a decoupled, resilient pipeline using {primary_skill} to reduce latency bottlenecks and maintain 99.9% availability.",
                "action": f"Designed modular service boundaries, introduced asynchronous background processing, implemented intelligent caching, and applied profiling to optimize execution hot spots.",
                "result": "Significantly accelerated response times, eliminated single points of failure, and streamlined production release cycles."
            },
            "key_talking_points": [
                f"Explain specific architectural decisions when structuring {primary_skill} components.",
                "Cite concrete metrics on throughput, latency, or query optimization.",
                "Mention automated testing and CI/CD validation to ensure zero regression."
            ]
        })
        q_idx += 1

        questions.append({
            "id": f"q_{q_idx}",
            "category": "technical",
            "question": f"How do you approach database schema design and data access patterns when integrating {secondary_skill} with backend services?",
            "interviewer_intent": "Evaluates data layer proficiency, indexing strategies, concurrency control, and ability to balance normalization against read/write performance.",
            "star_framework": {
                "situation": f"When developing production data layers involving {secondary_skill}, complex queries were beginning to degrade under concurrent user loads.",
                "task": "Restructure data models and access patterns to optimize throughput while guaranteeing strict data consistency.",
                "action": "Applied selective indexing, eliminated N+1 query patterns, restructured relation mappings, and implemented connection pooling.",
                "result": "Reduced database resource utilization by over 40% and improved transactional reliability across high-traffic endpoints."
            },
            "key_talking_points": [
                "Discuss query execution plan analysis (EXPLAIN ANALYZE) and index strategies.",
                "Explain connection pooling, connection limits, and transaction boundaries.",
                "Highlight automated migration practices and zero-downtime schema updates."
            ]
        })
        q_idx += 1

        # 2. Skill Gap Strategy Questions (Focus on Missing JD skills)
        if missing_skills:
            gap_skill = missing_skills[0].title()
            adjacent_skill = primary_skill
            questions.append({
                "id": f"q_{q_idx}",
                "category": "skill_gap",
                "question": f"The job description emphasizes hands-on proficiency with {gap_skill}. While your resume strongly demonstrates {adjacent_skill}, how would you ramp up and apply your experience to {gap_skill}?",
                "interviewer_intent": f"Assesses adaptability, learning velocity, and ability to transfer conceptual knowledge from {adjacent_skill} to {gap_skill}.",
                "star_framework": {
                    "situation": f"Recognizing that {gap_skill} shares core architectural paradigms with {adjacent_skill}, which I have used extensively in production.",
                    "task": f"Rapidly achieve production-level proficiency in {gap_skill} to deliver high-quality features without slowing team velocity.",
                    "action": f"Deconstruct {gap_skill} into underlying architectural principles, build functional prototypes, review idiomatic patterns, and map established concepts from {adjacent_skill}.",
                    "result": f"Confidently translate cross-framework expertise to ship production-ready, maintainable code in {gap_skill} within the first two weeks."
                },
                "key_talking_points": [
                    f"Acknowledge the gap transparently while showing strong conceptual overlap with {adjacent_skill}.",
                    "Highlight past track record of mastering new frameworks and tools on the job quickly.",
                    f"Show you already understand the idioms, ecosystem, and best practices of {gap_skill}."
                ]
            })
            q_idx += 1

        if len(missing_skills) > 1:
            second_gap = missing_skills[1].title()
            questions.append({
                "id": f"q_{q_idx}",
                "category": "skill_gap",
                "question": f"Have you worked with or evaluated {second_gap} in any personal projects or production environments, and how do you evaluate when to adopt it?",
                "interviewer_intent": "Checks technical curiosity, tool evaluation discipline, and whether the candidate understands the problem space solved by this technology.",
                "star_framework": {
                    "situation": f"Evaluating industry adoption trends and technical trade-offs between standard tooling and modern alternatives like {second_gap}.",
                    "task": f"Assess whether introducing {second_gap} provides measurable ROI in developer productivity or system performance.",
                    "action": "Built proof-of-concept implementations, benchmarked performance and developer ergonomics, and analyzed operational maintenance overhead.",
                    "result": "Gained clear perspective on the architectural sweet spot for this tool and how to implement it safely."
                },
                "key_talking_points": [
                    f"Discuss the primary problem {second_gap} was created to solve.",
                    "Demonstrate engineering pragmatism—adopting tools for value, not hype.",
                    "Express enthusiasm for contributing to projects utilizing this stack."
                ]
            })
            q_idx += 1

        # 3. Behavioral STAR-Method Questions
        questions.append({
            "id": f"q_{q_idx}",
            "category": "behavioral",
            "question": "Tell me about a time you encountered an unexpected critical bug or outage in production. How did you triage, resolve, and prevent recurrence?",
            "interviewer_intent": "Assesses composure under fire, systematic root-cause analysis, cross-functional communication, and commitment to post-mortem reliability.",
            "star_framework": {
                "situation": "A production deployment introduced an edge-case memory leak that caused elevated error rates during peak business traffic.",
                "task": "Immediately stabilize the service, communicate incident status to stakeholders, and isolate the root defect.",
                "action": "Rolled back the deployment cleanly, spun up isolated staging telemetry to reproduce the leak, identified the unclosed resource handler, and wrote regression tests.",
                "result": "Restored full service health within 18 minutes and added automated CI/CD static checks preventing similar leaks."
            },
            "key_talking_points": [
                "Maintain customer-first focus during live triage.",
                "Show disciplined debugging over panic or hasty hotfixes.",
                "Emphasize blameless post-mortem analysis and preventive test coverage."
            ]
        })
        q_idx += 1

        questions.append({
            "id": f"q_{q_idx}",
            "category": "behavioral",
            "question": "Describe a scenario where you strongly disagreed with a peer or lead regarding technical architecture or tool selection. How did you handle the situation?",
            "interviewer_intent": "Measures emotional intelligence, collaborative decision making, objective technical advocacy, and 'disagree and commit' maturity.",
            "star_framework": {
                "situation": "Our team debated between two conflicting architectural designs for a new high-throughput event processing service.",
                "task": "Align on an architecture that met performance requirements while respecting delivery deadlines and maintenance feasibility.",
                "action": "Created an objective evaluation matrix based on latency benchmarks, operational complexity, and team ramp-up time rather than personal preferences.",
                "result": "The team aligned consensus around the data-driven proposal, delivering the service two weeks ahead of schedule with zero post-launch disputes."
            },
            "key_talking_points": [
                "Focus on data and proof-of-concepts rather than dogma.",
                "Listen actively and validate the concerns of team members.",
                "Demonstrate total team commitment once a final decision is made."
            ]
        })

        return questions
