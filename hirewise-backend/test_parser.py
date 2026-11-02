"""
Comprehensive test suite for resume_parser.py, ats_scorer.py, and jd_matcher.py.
Includes regression test for kerning artifact PDF name extraction & skill token cleaning.
"""

import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from resume_parser import ResumeParser
from ats_scorer import ATSScorer
from jd_matcher import JDMatcher


def test_arpit_pdf_name_extraction_regression():
    print("=" * 70)
    print("TEST: REGRESSION TEST FOR KERNING ARTIFACT PDF (Arpit Tyagi)")
    print("=" * 70)

    pdf_path = Path(__file__).parent / "test_resumes" / "Arpit_Tyagi_Resume_ATS__3_.pdf"
    assert pdf_path.exists(), f"Test PDF file not found at {pdf_path}!"

    parser = ResumeParser()
    parsed = parser.parse(str(pdf_path))

    name = parsed["name"]
    skills = parsed["skills"]

    print(f"[EXTRACTED CANDIDATE NAME]: {name}")
    print(f"[EXTRACTED SKILLS COUNT]  : {len(skills)}")
    print(f"[EXTRACTED SKILLS LIST]   : {skills}")
    print(f"[SPOKEN LANGUAGES]        : {parsed.get('languages')}")

    # 1. Assert Candidate Name parsed cleanly as "Arpit Tyagi"
    assert name == "Arpit Tyagi", f"Expected candidate name 'Arpit Tyagi', got '{name}'!"

    # 2. Assert spoken languages separated into languages field and excluded from technical skills
    assert parsed.get("languages") == ["English", "German", "Hindi"], f"Unexpected spoken languages: {parsed.get('languages')}"
    for lang in ["English", "German", "Hindi"]:
        assert lang not in skills, f"Spoken language '{lang}' was not excluded from technical skills list!"

    # 3. Assert no leftover header artifacts or un-deduplicated skills exist
    forbidden_artifacts = {"Frame Languages", "Frame", "Tailwind", "Llm", "Rag", "Ar.Js", "Gsap", "Numpy"}
    found_artifacts = set(skills).intersection(forbidden_artifacts)
    assert not found_artifacts, f"Found improper artifacts in skills list: {found_artifacts}"

    # 4. Assert proper canonical display forms
    canonical_checks = {"LLM", "RAG", "AR.js", "GSAP", "NumPy", "A-Frame", "Tailwind CSS", "React", "Next.js", "Node.js", "PostgreSQL"}
    extracted_set = set(skills)
    missing_canonical = canonical_checks - extracted_set
    assert not missing_canonical, f"Missing canonical display skills: {missing_canonical}"

    print("\n[SUCCESS] ARPIT PDF NAME & SKILLS EXTRACTION REGRESSION TEST PASSED!")


def test_full_pipeline_integration():
    print("\n" + "=" * 70)
    print("TEST: FULL PIPELINE INTEGRATION TEST")
    print("=" * 70)

    test_dir = Path(__file__).parent / "test_resumes"
    docx_path = str(test_dir / "sample_resume.docx")

    # 1. Parse Resume
    parser = ResumeParser()
    parsed_resume = parser.parse(docx_path)
    print("\n--- 1. PARSED RESUME ---")
    print(f"Candidate Name: {parsed_resume['name']}")
    print(f"Email: {parsed_resume['email']}")
    print(f"Skills ({len(parsed_resume['skills'])}): {parsed_resume['skills'][:6]}...")

    # 2. ATS Score
    scorer = ATSScorer()
    ats_result = scorer.evaluate(parsed_resume)
    print("\n--- 2. ATS SCORING RESULT ---")
    print(f"Overall ATS Score: {ats_result['overall_score']} / 100 ({ats_result['level']})")
    print(f"Section Scores: {list(ats_result['section_scores'].keys())}")
    print(f"Suggestions Count: {len(ats_result['suggestions'])}")

    # 3. JD Matching
    sample_jd = """
    We are looking for a Senior Full Stack Engineer proficient in Python, FastAPI, React, PostgreSQL, Docker, AWS, and Kubernetes.
    The ideal candidate will architect scalable web microservices, build clean user interfaces with TypeScript and Tailwind,
    and manage CI/CD deployment pipelines on AWS.
    Required Skills: Python, FastAPI, React, TypeScript, PostgreSQL, Docker, Kubernetes, AWS.
    """

    matcher = JDMatcher()
    jd_result = matcher.match(parsed_resume, sample_jd)
    print("\n--- 3. JD MATCHING RESULT ---")
    print(f"Match Percentage: {jd_result['match_percentage']}%")
    print(f"Matching Skills: {jd_result['matching_skills']}")
    print(f"Missing Skills: {jd_result['missing_skills']}")

    assert ats_result['overall_score'] > 60, "ATS Score evaluation failed"
    assert jd_result['match_percentage'] > 50, "JD match evaluation failed"

    print("\n[SUCCESS] PIPELINE INTEGRATION TEST PASSED!")


if __name__ == "__main__":
    test_arpit_pdf_name_extraction_regression()
    test_full_pipeline_integration()
