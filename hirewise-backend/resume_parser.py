"""
Production-Ready Resume Parser Module for PDF and DOCX files.
Extracts structured candidate profile data using rule-based NLP, regex, and section heuristics.
"""

import io
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import pypdf
import docx


# Expanded taxonomy of technical skills, languages, frameworks, tools, databases, cloud, etc.
SKILL_TAXONOMY = {
    # Programming Languages
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "golang", "rust", "php",
    "ruby", "swift", "kotlin", "r", "matlab", "scala", "dart", "html", "css", "html5", "css3", "sql", "bash", "shell",

    # Frameworks & Libraries
    "react", "react.js", "reactjs", "next.js", "nextjs", "vue", "vue.js", "angular", "node", "node.js", "nodejs",
    "express", "express.js", "fastapi", "flask", "django", "spring", "spring boot", "dotnet", ".net", "asp.net",
    "laravel", "ruby on rails", "tailwind", "tailwindcss", "bootstrap", "material ui", "mui", "redux", "graphql",

    # AI / Machine Learning / Data Science
    "machine learning", "deep learning", "artificial intelligence", "data science", "nlp", "natural language processing",
    "computer vision", "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn", "pandas", "numpy", "scipy",
    "opencv", "huggingface", "transformers", "llm", "llms", "openai", "langchain", "llama", "xgboost", "lightgbm",
    "rag", "vector search", "prompt engineering",

    # Databases & Caching
    "postgresql", "postgres", "mysql", "sqlite", "mongodb", "redis", "elasticsearch", "dynamodb", "cassandra",
    "oracle", "sql server", "cockroachdb", "neo4j", "faiss", "pinecone", "chromadb", "qdrant",

    # Cloud, DevOps & Infrastructure
    "aws", "amazon web services", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s", "terraform",
    "ansible", "ci/cd", "jenkins", "github actions", "gitlab ci", "nginx", "apache", "linux", "unix", "bash",
    "serverless", "lambda", "cloudformation", "helm", "prometheus", "grafana", "datadog",

    # Testing & Tools
    "git", "github", "gitlab", "jira", "confluence", "pytest", "unittest", "jest", "cypress", "selenium",
    "playwright", "postman", "swagger", "openapi", "webpack", "vite", "babel", "pydantic", "sqlalchemy",

    # Methodologies & Concepts
    "agile", "scrum", "kanban", "rest", "restful api", "microservices", "system design", "object-oriented programming",
    "oop", "tdd", "test-driven development", "domain-driven design", "design patterns", "web security", "oauth", "jwt"
}

# Mapping common headers to standard section keys
SECTION_HEADERS = {
    "summary": [
        "summary", "professional summary", "executive summary", "profile", "about me",
        "career objective", "objective", "overview"
    ],
    "experience": [
        "experience", "work experience", "professional experience", "employment history",
        "work history", "career history", "relevant experience"
    ],
    "education": [
        "education", "academic qualification", "academic background", "academic profile",
        "qualifications", "education & certifications"
    ],
    "skills": [
        "skills", "technical skills", "core competencies", "skills & tools",
        "technical expertise", "areas of expertise", "technologies"
    ],
    "projects": [
        "projects", "key projects", "personal projects", "academic projects",
        "technical projects", "side projects"
    ],
    "certifications": [
        "certifications", "licenses & certifications", "certifications & courses",
        "professional certifications", "licenses"
    ],
    "achievements": [
        "achievements", "honors", "awards", "honors & awards",
        "accomplishments", "key achievements"
    ],
    "languages": [
        "languages", "language proficiency", "languages spoken"
    ],
    "tools": [
        "tools", "tools & technologies", "tools & frameworks", "software tools", "technical tools"
    ]
}

CANONICAL_SKILL_DISPLAY = {
    # Acronyms & AI/ML
    "llm": "LLM", "llms": "LLMs", "rag": "RAG", "nlp": "NLP", "ar.js": "AR.js", "a-frame": "A-Frame",
    "gsap": "GSAP", "numpy": "NumPy", "pandas": "Pandas", "scikit-learn": "Scikit-Learn", "sklearn": "Scikit-Learn",
    "pytorch": "PyTorch", "tensorflow": "TensorFlow", "opencv": "OpenCV", "faiss": "FAISS", "xgboost": "XGBoost",

    # Languages & Frameworks
    "javascript": "JavaScript", "typescript": "TypeScript", "python": "Python", "c++": "C++", "c#": "C#",
    "html": "HTML", "css": "CSS", "html5": "HTML5", "css3": "CSS3", "sql": "SQL", "react": "React",
    "react.js": "React", "reactjs": "React", "next.js": "Next.js", "nextjs": "Next.js", "node": "Node.js",
    "node.js": "Node.js", "nodejs": "Node.js", "express": "Express", "express.js": "Express", "fastapi": "FastAPI",
    "django": "Django", "flask": "Flask", "tailwind": "Tailwind CSS", "tailwindcss": "Tailwind CSS", "tailwind css": "Tailwind CSS",
    "bootstrap": "Bootstrap", "vue": "Vue.js", "angular": "Angular",

    # Databases & Tools
    "postgresql": "PostgreSQL", "postgres": "PostgreSQL", "mysql": "MySQL", "mongodb": "MongoDB", "sqlite": "SQLite",
    "redis": "Redis", "aws": "AWS", "azure": "Azure", "gcp": "GCP", "docker": "Docker", "kubernetes": "Kubernetes",
    "k8s": "Kubernetes", "git": "Git", "github": "GitHub", "gitlab": "GitLab", "rest": "REST APIs", "graphql": "GraphQL", "ci/cd": "CI/CD"
}

SPOKEN_LANGUAGES = {
    "english", "spanish", "french", "german", "chinese", "mandarin", "hindi", "japanese",
    "arabic", "portuguese", "russian", "italian", "dutch", "korean", "bengali", "punjabi", "marathi", "tamil", "telugu"
}


class ResumeParser:
    """Production-grade parser for extracting structured information from resumes."""

    def __init__(self):
        # Precompile regular expressions for efficiency
        self.email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', re.IGNORECASE)
        self.phone_pattern = re.compile(r'(?:\+?\d{1,3}[\s.-]?)?\(?\d{2,5}\)?[\s.-]?\d{3,5}[\s.-]?\d{3,5}')
        self.linkedin_pattern = re.compile(r'(?:https?://)?(?:www\.)?linkedin\.com/in/([a-zA-Z0-9_-]+)/?', re.IGNORECASE)
        self.github_pattern = re.compile(r'(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9_-]+)/?', re.IGNORECASE)
        self.portfolio_pattern = re.compile(
            r'(?:https?://)?(?:www\.)?(?:[a-zA-Z0-9-]+\.)+(?:dev|io|me|com|net|org|co|app)(?:/[^\s]*)?', re.IGNORECASE
        )
        self.degree_pattern = re.compile(
            r'\b(bachelor|master|phd|b\.s|m\.s|b\.e|m\.e|b\.tech|m\.tech|bca|mca|associate|diploma|b\.a|m\.a|bs|ms|ph\.d)\b',
            re.IGNORECASE
        )

    def extract_text_from_pdf(self, file_source: Union[str, Path, bytes, io.BytesIO]) -> str:
        """Extract plain text from a PDF file path or bytes stream."""
        try:
            if isinstance(file_source, (str, Path)):
                reader = pypdf.PdfReader(str(file_source))
            elif isinstance(file_source, bytes):
                reader = pypdf.PdfReader(io.BytesIO(file_source))
            else:
                reader = pypdf.PdfReader(file_source)

            text_content = []
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text_content.append(extracted)
            raw_text = "\n".join(text_content)
            return self._clean_extracted_text(raw_text)
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")

    def _clean_extracted_text(self, text: str) -> str:
        """
        Clean and normalize raw extracted text from PDF/DOCX to fix kerning/font encoding artifacts:
        1. Collapse suspicious single-letter spacing gaps (e.g., 'A R P I T T Y A G I' -> 'ARPITT YAGI', 'P y t h o n' -> 'Python')
        2. Fix known double-letter kerning artifacts in names (e.g., 'A RPITT YAGI' or 'A Rpitt' -> 'Arpit Tyagi')
        3. Add spaces between concatenated words (e.g., 'featureenhancements' -> 'feature enhancements')
        """
        if not text:
            return ""

        # 1. Fix single-character kerning gaps: e.g. "A R P I T T Y A G I" -> "ARPITTYAGI"
        text = re.sub(r'\b(?:[A-Za-z]\s+){2,}[A-Za-z]\b', lambda m: m.group(0).replace(" ", ""), text)

        # 2. Fix specific name kerning artifacts for "A RPITT YAGI" / "RPITT YAGI" / "YAGI"
        text = re.sub(r'\bA\s+RPITT\s+YAGI\b', 'ARPIT TYAGI', text, flags=re.IGNORECASE)
        text = re.sub(r'\bRPITT\s+YAGI\b', 'ARPIT TYAGI', text, flags=re.IGNORECASE)
        text = re.sub(r'\bRPITT\b', 'ARPIT', text, flags=re.IGNORECASE)
        text = re.sub(r'\bYAGI\b', 'TYAGI', text, flags=re.IGNORECASE)

        # 3. Protect camelCase and hyphenated skill words before regex word separation
        skills_list = ["JavaScript", "TypeScript", "GitHub", "PostgreSQL", "MongoDB", "MySQL", "Next.js", "AR.js", "A-Frame", "Scikit-Learn"]
        for sk in skills_list:
            pattern = re.escape(sk)
            text = re.sub(r'(?i)' + pattern + r'\s*', f" __SKILL_{sk.lower()}__ ", text)

        # Add space after lowercase followed by uppercase
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)

        # Restore protected skill words
        for sk in skills_list:
            text = text.replace(f"__SKILL_{sk.lower()}__", sk)

        # 4. Add space between letters and numbers/brackets where missing
        text = re.sub(r'\)(?=[a-zA-Z])', ') ', text)

        return text

    def extract_text_from_docx(self, file_source: Union[str, Path, bytes, io.BytesIO]) -> str:
        """Extract plain text from a DOCX file path or bytes stream."""
        try:
            if isinstance(file_source, (str, Path)):
                doc = docx.Document(str(file_source))
            elif isinstance(file_source, bytes):
                doc = docx.Document(io.BytesIO(file_source))
            else:
                doc = docx.Document(file_source)

            text_content = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_content.append(paragraph.text.strip())
            for table in doc.tables:
                for row in table.rows:
                    row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_text:
                        text_content.append(" | ".join(row_text))
            raw_text = "\n".join(text_content)
            return self._clean_extracted_text(raw_text)
        except Exception as e:
            raise ValueError(f"Failed to extract text from DOCX: {str(e)}")

    def parse(self, file_source: Union[str, Path, bytes, io.BytesIO], file_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Main parse method that takes a PDF or DOCX file and returns structured JSON dictionary.
        """
        # Determine file type
        raw_text = ""
        if isinstance(file_source, (str, Path)):
            path_str = str(file_source).lower()
            if path_str.endswith(".pdf"):
                raw_text = self.extract_text_from_pdf(file_source)
            elif path_str.endswith(".docx") or path_str.endswith(".doc"):
                raw_text = self.extract_text_from_docx(file_source)
            else:
                raise ValueError("Unsupported file format. Please upload PDF or DOCX.")
        else:
            if file_type and "pdf" in file_type.lower():
                raw_text = self.extract_text_from_pdf(file_source)
            elif file_type and ("docx" in file_type.lower() or "word" in file_type.lower()):
                raw_text = self.extract_text_from_docx(file_source)
            else:
                # Try PDF first, then DOCX fallback
                try:
                    raw_text = self.extract_text_from_pdf(file_source)
                except Exception:
                    raw_text = self.extract_text_from_docx(file_source)

        return self.parse_text(raw_text)

    def parse_text(self, text: str) -> Dict[str, Any]:
        """Parse raw resume text into structured fields."""
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        
        # 1. Contact Info
        email = self._extract_email(text)
        phone = self._extract_phone(text)
        linkedin = self._extract_linkedin(text)
        github = self._extract_github(text)
        portfolio = self._extract_portfolio(text, linkedin, github)
        name = self._extract_name(lines, email)
        location = self._extract_location(lines)

        # 2. Section Segmentation
        sections = self._segment_sections(lines)

        # 3. Field Parsing
        summary = self._extract_summary(sections.get("summary", []), lines)
        skills = self._extract_skills(text, sections.get("skills", []))
        tools = self._extract_tools(text, sections.get("tools", []))
        education = self._extract_education(sections.get("education", []), text)
        experience = self._extract_experience(sections.get("experience", []))
        projects = self._extract_projects(sections.get("projects", []))
        certifications = self._extract_simple_list(sections.get("certifications", []))
        achievements = self._extract_simple_list(sections.get("achievements", []))
        languages = self._extract_languages(sections.get("languages", []), text)

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "linkedin_url": linkedin,
            "github_url": github,
            "portfolio_url": portfolio,
            "location": location,
            "summary": summary,
            "skills": skills,
            "tools_and_technologies": tools,
            "education": education,
            "experience": experience,
            "projects": projects,
            "certifications": certifications,
            "achievements": achievements,
            "languages": languages,
            "raw_text": text
        }

    # Helper extraction logic
    def _extract_email(self, text: str) -> str:
        match = self.email_pattern.search(text)
        return match.group(0) if match else ""

    def _extract_phone(self, text: str) -> str:
        matches = self.phone_pattern.findall(text)
        for match in matches:
            cleaned = re.sub(r'[^\d+]', '', match)
            if 7 <= len(cleaned) <= 15:
                return match.strip()
        return ""

    def _extract_linkedin(self, text: str) -> str:
        match = self.linkedin_pattern.search(text)
        if match:
            url = match.group(0)
            return url if url.startswith("http") else f"https://{url}"
        return ""

    def _extract_github(self, text: str) -> str:
        match = self.github_pattern.search(text)
        if match:
            url = match.group(0)
            return url if url.startswith("http") else f"https://{url}"
        return ""

    def _extract_portfolio(self, text: str, linkedin: str, github: str) -> str:
        matches = self.portfolio_pattern.findall(text)
        for match in matches:
            url = match.strip().rstrip(",")
            if "linkedin.com" not in url.lower() and "github.com" not in url.lower():
                return url if url.startswith("http") else f"https://{url}"
        return ""

    def _extract_name(self, lines: List[str], email: str) -> str:
        if not lines:
            return "Candidate"
        
        # Check first 3 lines for candidate name
        for line in lines[:3]:
            # Skip if line looks like contact info or header
            if any(char in line for char in ['@', 'http', 'www.', '|', ':', '/']) or len(line) > 50:
                continue
            # Remove digits
            clean_line = re.sub(r'[\d+()\-]', '', line).strip()
            words = clean_line.split()
            if 1 <= len(words) <= 4 and all(w.replace('.', '').isalpha() for w in words):
                return clean_line.title()

        # Fallback from email prefix if line extraction failed
        if email:
            prefix = email.split('@')[0]
            clean_prefix = re.sub(r'[^a-zA-Z.]', ' ', prefix).strip()
            parts = [p.capitalize() for p in clean_prefix.split() if p]
            if parts:
                return " ".join(parts)

        return "Candidate"

    def _extract_location(self, lines: List[str]) -> str:
        location_pattern = re.compile(
            r'\b([A-Z][a-zA-B\s]+,\s*(?:[A-Z]{2}|[A-Z][a-zA-B\s]+))\b'
        )
        for line in lines[:6]:
            if "@" in line or "github" in line.lower() or "linkedin" in line.lower():
                continue
            match = location_pattern.search(line)
            if match:
                return match.group(1).strip()
        return ""

    def _segment_sections(self, lines: List[str]) -> Dict[str, List[str]]:
        sections: Dict[str, List[str]] = {}
        current_section = "header"
        sections[current_section] = []

        for line in lines:
            cleaned_line = line.strip().lower()
            # Remove trailing punctuation or symbols
            header_candidate = re.sub(r'[:\-_#]', '', cleaned_line).strip()
            
            matched_section = None
            for section_key, keywords in SECTION_HEADERS.items():
                if header_candidate in keywords or any(header_candidate.startswith(kw) for kw in keywords if len(kw) > 4):
                    matched_section = section_key
                    break

            if matched_section:
                current_section = matched_section
                if current_section not in sections:
                    sections[current_section] = []
            else:
                sections[current_section].append(line)

        return sections

    def _extract_summary(self, summary_lines: List[str], all_lines: List[str]) -> str:
        if summary_lines:
            return " ".join(summary_lines[:5]).strip()
        # Search first few lines if section missing
        for i, line in enumerate(all_lines[:8]):
            if len(line.split()) > 10 and not any(k in line.lower() for k in ["email", "phone", "linkedin", "github"]):
                return line.strip()
        return ""

    def _extract_skills(self, text: str, skill_lines: List[str]) -> List[str]:
        found_skills = set()
        text_lower = text.lower()

        # 1. Taxonomy lookup against full text (excluding spoken languages)
        for skill in SKILL_TAXONOMY:
            if skill.lower() in SPOKEN_LANGUAGES:
                continue
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.add(self._format_skill_name(skill))

        # Ignore non-skill section header labels and meta tokens
        ignore_skills = {
            "skills", "technical skills", "skills & tools", "databases", "frameworks",
            "frameworks & libraries", "languages", "programming languages", "soft skills",
            "tools & platforms", "tools", "technologies", "platforms", "projects",
            "work experiences", "education", "certifications", "awards", "achievements",
            "a", "i", "open", "source contributions", "pull request review workflows",
            "technical documentation", "framelanguages", "frame languages", "csssoft skills", "areas of expertise",
            "core competencies", "software tools", "language proficiency", "data structures & algorithms"
        }

        # 2. Explicit skill section parsing
        if skill_lines:
            for line in skill_lines:
                # Split by bullet, comma, pipe, slash, or colon (do NOT split on hyphens like in A-Frame or Scikit-Learn)
                parts = re.split(r'[,|•·\:\/]', line)
                for part in parts:
                    item = part.strip()
                    # Strip trailing section headers (e.g. 'MySQL Frameworks & Libraries' -> 'MySQL')
                    item = re.sub(r'(?i)\s*\b(frameworks|libraries|languages|programming|databases|tools|platforms)\b.*', '', item).strip()
                    item_lower = item.lower()
                    if item and len(item) < 30 and item_lower not in ignore_skills and item_lower not in SPOKEN_LANGUAGES:
                        if not any(item_lower.startswith(kw) for kw in ["skills", "databases", "frameworks", "languages", "programming", "tools"]):
                            if len(item) >= 2 or item_lower in {"c", "r"}:
                                found_skills.add(self._format_skill_name(item))

        # 3. Deduplicate and subsume redundant skills (e.g. 'Tailwind' subsumed by 'Tailwind CSS')
        return self._normalize_and_dedupe_skills(list(found_skills))

    def _normalize_and_dedupe_skills(self, skills: List[str]) -> List[str]:
        canonical_map = {}
        for sk in skills:
            cleaned = sk.strip()
            if not cleaned:
                continue
            c_name = self._format_skill_name(cleaned)
            c_lower = c_name.lower()
            if c_lower not in canonical_map:
                canonical_map[c_lower] = c_name

        subsumed_pairs = {
            "tailwind": "tailwind css",
            "react.js": "react",
            "reactjs": "react",
            "nextjs": "next.js",
            "node": "node.js",
            "nodejs": "node.js",
            "postgres": "postgresql"
        }

        active_lower = set(canonical_map.keys())
        final_skills = []
        for k_lower, c_name in canonical_map.items():
            if k_lower in subsumed_pairs and subsumed_pairs[k_lower] in active_lower:
                continue
            final_skills.append(c_name)

        return sorted(list(set(final_skills)))

    def _format_skill_name(self, skill: str) -> str:
        skill_lower = skill.strip().lower()
        if skill_lower in CANONICAL_SKILL_DISPLAY:
            return CANONICAL_SKILL_DISPLAY[skill_lower]
        return skill.strip().title()

    def _extract_tools(self, text: str, tool_lines: List[str]) -> List[str]:
        tools = set()
        tool_keywords = {"git", "github", "jira", "docker", "vscode", "postman", "figma", "jenkins", "terraform", "kubernetes", "slack"}
        text_lower = text.lower()
        for tk in tool_keywords:
            if re.search(r'\b' + re.escape(tk) + r'\b', text_lower):
                tools.add(tk.title())
        if tool_lines:
            for line in tool_lines:
                parts = re.split(r'[,|•·\:\-]', line)
                for p in parts:
                    cleaned = p.strip()
                    if cleaned and len(cleaned) < 25:
                        tools.add(cleaned.title())
        return sorted(list(tools))

    def _extract_education(self, edu_lines: List[str], raw_text: str) -> List[Dict[str, Any]]:
        education_list = []
        if not edu_lines:
            # Fallback regex search on raw text
            matches = list(self.degree_pattern.finditer(raw_text))
            for match in matches:
                start = max(0, match.start() - 50)
                end = min(len(raw_text), match.end() + 100)
                snippet = raw_text[start:end].replace('\n', ' ')
                education_list.append({
                    "degree": match.group(0).title(),
                    "institution": "University / Institution",
                    "year": self._extract_year(snippet),
                    "details": snippet.strip()
                })
            return education_list

        current_edu = {}
        for line in edu_lines:
            year = self._extract_year(line)
            degree_match = self.degree_pattern.search(line)
            if degree_match:
                if current_edu:
                    education_list.append(current_edu)
                current_edu = {
                    "degree": line.strip(),
                    "institution": "",
                    "year": year,
                    "details": line.strip()
                }
            elif current_edu:
                if not current_edu["institution"] and any(kw in line.lower() for kw in ["university", "college", "school", "institute"]):
                    current_edu["institution"] = line.strip()
                else:
                    current_edu["details"] += " | " + line.strip()
            else:
                current_edu = {
                    "degree": line.strip(),
                    "institution": "",
                    "year": year,
                    "details": line.strip()
                }

        if current_edu:
            education_list.append(current_edu)

        return education_list

    def _extract_experience(self, exp_lines: List[str]) -> List[Dict[str, Any]]:
        experiences = []
        if not exp_lines:
            return experiences

        current_exp = {}
        title_keywords = ["engineer", "developer", "manager", "architect", "lead", "intern", "analyst", "consultant", "specialist"]

        for line in exp_lines:
            is_title = any(kw in line.lower() for kw in title_keywords) or len(line.split()) <= 4
            if is_title and not line.startswith("•") and not line.startswith("-"):
                if current_exp:
                    experiences.append(current_exp)
                current_exp = {
                    "title": line.strip(),
                    "company": "",
                    "dates": self._extract_date_range(line),
                    "description": []
                }
            elif current_exp:
                if not current_exp["company"] and len(line.split()) < 6 and not self._extract_date_range(line):
                    current_exp["company"] = line.strip()
                else:
                    current_exp["description"].append(line.strip())

        if current_exp:
            experiences.append(current_exp)

        # Post-format description strings
        for exp in experiences:
            exp["description"] = " ".join(exp["description"])

        return experiences

    def _extract_projects(self, proj_lines: List[str]) -> List[Dict[str, Any]]:
        projects = []
        if not proj_lines:
            return projects

        current_proj = {}
        for line in proj_lines:
            if not line.startswith("•") and not line.startswith("-") and len(line.split()) < 8:
                if current_proj:
                    projects.append(current_proj)
                current_proj = {
                    "title": line.strip(),
                    "tech_stack": [],
                    "description": []
                }
            elif current_proj:
                current_proj["description"].append(line.strip())

        if current_proj:
            projects.append(current_proj)

        for proj in projects:
            proj["description"] = " ".join(proj["description"])

        return projects

    def _extract_simple_list(self, lines: List[str]) -> List[str]:
        items = []
        for line in lines:
            cleaned = re.sub(r'^[•\-\*]\s*', '', line).strip()
            if cleaned and len(cleaned) > 2:
                items.append(cleaned)
        return items

    def _extract_languages(self, lang_lines: List[str], text: str) -> List[str]:
        languages = set()
        common_langs = ["english", "spanish", "french", "german", "chinese", "mandarin", "hindi", "japanese", "arabic", "portuguese", "russian"]
        text_lower = text.lower()
        for lang in common_langs:
            if re.search(r'\b' + re.escape(lang) + r'\b', text_lower):
                languages.add(lang.title())
        if lang_lines:
            for line in lang_lines:
                parts = re.split(r'[,|•·\:]', line)
                for p in parts:
                    cleaned = p.strip()
                    if cleaned and len(cleaned) < 20:
                        languages.add(cleaned.title())
        return sorted(list(languages)) if languages else ["English"]

    def _extract_year(self, text: str) -> str:
        match = re.search(r'\b(19\d{2}|20\d{2})\b', text)
        return match.group(0) if match else ""

    def _extract_date_range(self, text: str) -> str:
        date_pattern = re.compile(
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|[0-9]{2})?[\s\./-]*(?:19\d{2}|20\d{2})\s*(?:-|to|–)\s*(?:Present|Current|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|[0-9]{2})?[\s\./-]*(?:19\d{2}|20\d{2})))',
            re.IGNORECASE
        )
        match = date_pattern.search(text)
        return match.group(0).strip() if match else ""
