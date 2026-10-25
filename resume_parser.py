"""
HireWise AI - Resume Parser Module Forwarder.
Re-exports the production parser from backend/resume_parser.py to maintain backward compatibility.
"""

import sys
from pathlib import Path

backend_dir = str(Path(__file__).parent / "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from backend.resume_parser import ResumeParser, SKILL_TAXONOMY, SECTION_HEADERS

__all__ = ["ResumeParser", "SKILL_TAXONOMY", "SECTION_HEADERS"]
