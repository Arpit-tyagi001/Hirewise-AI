# 🚀 HireWise AI — Intelligent Resume Analyzer & ATS Optimization Engine

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React%20%2B%20TypeScript-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Bundler-Vite-646CFF?style=flat&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Database](https://img.shields.io/badge/Database-SQLite%20%2F%20PostgreSQL-4479A1?style=flat&logo=sqlite&logoColor=white)](https://sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**HireWise AI** is a production-ready, full-stack web application designed to help job seekers and talent recruiters optimize resumes for modern Applicant Tracking Systems (ATS). 

By combining rule-based Natural Language Processing (NLP), TF-IDF vector similarity matching, and guarded Large Language Model (LLM) intelligence, HireWise AI objectively scores resumes, pinpoints missing keywords against target job descriptions, and rewrites bullet points to maximize interview callback rates—without ever inventing false qualifications.

---

## 📑 Table of Contents

- [Key Features](#-key-features)
- [How It Works (System Architecture)](#-how-it-works-system-architecture)
- [Tech Stack](#-tech-stack)
- [Project Directory Structure](#-project-directory-structure)
- [Prerequisites](#-prerequisites)
- [Quick Start Guide (Commands to Run)](#-quick-start-guide-commands-to-run)
  - [1. Backend Setup & Run](#1-backend-setup--run-fastapi-server)
  - [2. Frontend Setup & Run](#2-frontend-setup--run-react--vite)
- [Environment Configuration](#-environment-configuration)
- [Running Automated Tests](#-running-automated-tests)
- [API Endpoints Overview](#-api-endpoints-overview)
- [Security & Production Readiness](#-security--production-readiness)
- [Troubleshooting & FAQs](#-troubleshooting--faqs)

---

## ✨ Key Features

### 1. Multi-Format Resume Parsing (PDF & DOCX)
- Extracts structured profile data: Contact Information (email, phone, LinkedIn, GitHub), Skills, Work Experience, Education, Projects, and Certifications.
- Robust against real-world PDF quirks such as character kerning gaps, multiple column layouts, and irregular bullet markers.

### 2. 10-Dimension Objective ATS Scoring Engine
Evaluates resumes across 10 critical dimensions to calculate an overall ATS score (0 to 100) and actionable category ratings:
1. **Contact Information** (Full name, phone, email, professional portfolio links)
2. **Skills Coverage** (Depth and relevance against industry taxonomy)
3. **Work Experience** (Tenure, company presence, chronological consistency)
4. **Education** (Degree level, institution, graduation timelines)
5. **Projects** (Technical artifacts, deliverables, GitHub links)
6. **Certifications** (Industry accreditations and credentials)
7. **Action Verbs** (Presence of strong verbs: *architected, spearheaded, accelerated*)
8. **Keyword Density** (Vocabulary distribution and natural keyword flow)
9. **Formatting & Structure** (File readability, layout, standard section headings)
10. **Section Completeness** (Detection of missing standard resume sections)

### 3. Job Description (JD) Gap Analysis
- Upload a resume alongside a target job description.
- Computes mathematical vector similarity using **TF-IDF + Cosine Similarity** combined with skill taxonomy overlap.
- Generates **Matched Skills**, **Missing Skills**, and **Recommended Keywords** to bridge the gap.

### 4. Anti-Hallucination Resume Bullet Rewriter
- Transforms passive bullets (*"responsible for handling APIs"*) into high-impact accomplishments (*"Engineered and deployed scalable REST APIs..."*).
- **Strict Guardrail Policy**: Refuses to invent skills, metrics, or experiences not genuinely present in the candidate's original resume.
- Review before-and-after diffs, accept or reject changes individually, and **Export a Tailored DOCX Resume** with 1 click.

### 5. Multi-User Authentication & Data Privacy
- Secure JWT-based authentication with bcrypt password hashing.
- **Strict Data Isolation**: Each recruiter or candidate only sees their own uploaded resumes and analysis history.
- Supports **Anonymous Demo Mode** for quick instant scans without signing up.

---

## 🏗 System Architecture

```mermaid
flowchart TD
    User([User / Browser])
    
    subgraph Frontend ["Frontend (React + TypeScript + Vite)"]
        UI["Landing Page / Dashboard / Upload / Results"]
        ApiService["api.ts (REST Service)"]
        UI <--> ApiService
    end

    subgraph Backend ["Backend (FastAPI + Python)"]
        FastAPIApp["FastAPI REST API"]
        SecurityMW["10MB Size Limit & MIME Magic Check"]
        AuthModule["JWT Auth & Bcrypt Passwords"]
        Parser["ResumeParser (pypdf + python-docx)"]
        Scorer["ATSScorer (10-Dimension Weights)"]
        Matcher["JDMatcher (TF-IDF + Cosine Sim)"]
        Rewriter["ResumeRewriter (Guardrails + Groq/OpenAI)"]
    end

    subgraph Storage ["Data Layer"]
        SQLiteDB[("SQLite / PostgreSQL (hirewise.db)")]
        Alembic["Alembic Schema Migrations"]
    end

    User <--> UI
    ApiService <-->|"HTTP JSON / multipart-form"| FastAPIApp
    FastAPIApp --> SecurityMW --> AuthModule
    FastAPIApp --> Parser
    FastAPIApp --> Scorer
    FastAPIApp --> Matcher
    FastAPIApp --> Rewriter
    FastAPIApp <--> SQLiteDB
    Alembic -.-> SQLiteDB
```

---

## 💻 Tech Stack

| Layer | Technologies | Purpose |
|---|---|---|
| **Frontend** | React 18/19, TypeScript, Vite, Recharts, Lucide Icons | Responsive SPA, interactive charts, and dashboards |
| **Backend** | Python 3.10+, FastAPI, Uvicorn, Pydantic | High-performance asynchronous REST API |
| **Parsing** | `pypdf`, `python-docx` | Native text extraction from binary resume formats |
| **NLP & ML** | `scikit-learn`, `numpy`, `pandas` | TF-IDF vectorization, cosine similarity, keyword frequency |
| **AI / LLM** | Groq (`openai/gpt-oss-120b`), OpenAI fallback | Context-aware bullet rewriting with anti-hallucination guardrails |
| **Database** | SQLAlchemy ORM, Alembic, SQLite / PostgreSQL | User accounts, analysis history, rewrite sessions |
| **Security** | PyJWT, Bcrypt, Starlette Middleware | JWT bearer auth, password salting, file size & MIME checking |

---

## 📁 Project Directory Structure

```text
hirewise-ai/
├── backend/                        # FastAPI Backend Application
│   ├── alembic/                    # Database schema migrations
│   │   └── versions/               # Migration revision scripts (at head)
│   ├── test_resumes/               # Sample PDF & DOCX resumes for testing
│   ├── alembic.ini                 # Alembic configuration
│   ├── ats_scorer.py               # 10-dimension ATS scoring engine
│   ├── database.py                 # SQLAlchemy session management & DB connection
│   ├── hirewise.db                 # Active SQLite database file
│   ├── jd_matcher.py               # Job description TF-IDF gap matcher
│   ├── main.py                     # FastAPI routes, auth, middleware & handlers
│   ├── models.py                   # SQLAlchemy ORM models (User, ResumeAnalysis, etc.)
│   ├── resume_parser.py            # PDF/DOCX parser & skill taxonomy engine
│   ├── rewriter.py                 # JD-aware bullet rewriter with guardrails
│   ├── test_api.py                 # API endpoints automated integration test
│   ├── test_auth.py                # JWT authentication & data isolation test
│   ├── test_parser.py              # Multi-column & kerning PDF regression test
│   └── test_security.py            # Magic-byte MIME & DoS payload tests
├── src/                            # React + TypeScript Frontend
│   ├── assets/                     # Project logo and static graphics
│   ├── components/                 # Reusable UI components
│   │   ├── AppShell.tsx            # Recruiter workspace layout & sidebar
│   │   ├── AuthModal.tsx           # Sign-in / Sign-up dialog modal
│   │   ├── BulletDiffCard.tsx      # Before vs after bullet revision card
│   │   ├── Navbar.tsx              # Top sticky navigation bar
│   │   ├── RewriterPanel.tsx       # Live JD bullet rewriting workspace
│   │   ├── ScoreGauge.tsx          # Circular radial ATS score gauge
│   │   └── ...
│   ├── pages/                      # Page views
│   │   ├── Home.tsx                # Public landing page with live demo preview
│   │   ├── Dashboard.tsx           # Recruitment analytics & candidate rankings
│   │   ├── UploadPage.tsx          # Resume upload & JD text input page
│   │   ├── Results.tsx             # Detailed evaluation report & breakdown
│   │   ├── HistoryView.tsx         # User's saved resume analyses history
│   │   └── Pricing.tsx, About.tsx, Contact.tsx
│   ├── services/
│   │   └── api.ts                  # Centralized fetch client for backend endpoints
│   ├── main.tsx                    # React application root
│   └── styles.css, motion.css      # Dark/light theme styles & smooth animations
├── app.html                        # Vite development & production HTML template
├── index.html                      # Offline/static launcher entrypoint
├── main.py                         # Root shortcut runner (python main.py)
├── package.json                    # Node.js dependencies & scripts
├── pyproject.toml                  # Python package configuration
├── requirements.txt                # Complete Python backend dependencies
├── vite.config.ts                  # Vite build & bundle configuration
└── README.md                       # Complete documentation (this file)
```

---

## ⚙️ Prerequisites

Before running the project, make sure you have the following installed on your computer:

1. **Python 3.10 or higher**: [Download Python](https://www.python.org/downloads/)
2. **Node.js (v18 or higher) & npm**: [Download Node.js](https://nodejs.org/)
3. *(Optional)* **uv**: An ultra-fast Python package manager: `pip install uv`

---

## 🚀 Quick Start Guide (Commands to Run)

To run the complete full-stack application, you will open **two terminal windows**: one for the Backend and one for the Frontend.

### 1. Backend Setup & Run (FastAPI Server)

Open your terminal in the project root directory (`hirewise-ai`):

#### Step A: Create and activate a Python virtual environment

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**On macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Step B: Install backend dependencies
```bash
pip install -r requirements.txt
```
*(Or if using uv: `uv pip install -r requirements.txt`)*

#### Step C: Start the backend server
You can start the backend using the root launcher:
```bash
python main.py
```
*Alternatively, you can run directly with Uvicorn:*
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

✅ **Backend will be live at:**
- **Health Check:** `http://127.0.0.1:8000/health`
- **Interactive Swagger API Docs:** `http://127.0.0.1:8000/docs`
- **Alternative Redoc Docs:** `http://127.0.0.1:8000/redoc`

---

### 2. Frontend Setup & Run (React + Vite)

Open a **second terminal window** in the project root directory (`hirewise-ai`):

#### Step A: Install Node dependencies
````markdown
<div align="center">

# 🚀 HireWise AI

### AI-Powered Resume Intelligence Platform

Optimize your resume for ATS, match it against job descriptions, identify missing skills, and enhance existing resume content with AI — **without generating fake experience.**

<p align="center">
  <a href="https://hirewise-ai-two.vercel.app/">
    <img src="https://img.shields.io/badge/Live%20Demo-Visit-success?style=for-the-badge" />
  </a>
  <a href="https://hirewise-ai-backend.onrender.com/docs">
    <img src="https://img.shields.io/badge/API-Swagger-blue?style=for-the-badge" />
  </a>
</p>

<p align="center">
<img src="https://img.shields.io/badge/React-19-blue?logo=react"/>
<img src="https://img.shields.io/badge/TypeScript-5-blue?logo=typescript"/>
<img src="https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi"/>
<img src="https://img.shields.io/badge/Python-3.12-yellow?logo=python"/>
<img src="https://img.shields.io/badge/Vite-Build-purple?logo=vite"/>
<img src="https://img.shields.io/badge/TailwindCSS-4-38B2AC?logo=tailwind-css"/>
<img src="https://img.shields.io/badge/AI-Groq-orange"/>
</p>

</div>

---

# 📖 Overview

Recruiters spend only a few seconds reviewing each resume, while Applicant Tracking Systems (ATS) filter thousands of applications before a recruiter even sees them.

**HireWise AI** is an AI-powered resume intelligence platform designed to help candidates improve their resumes through intelligent analysis instead of blind keyword stuffing.

Unlike many AI resume tools that generate unrealistic achievements, HireWise AI focuses on **improving existing content while preserving authenticity**. Every AI suggestion is designed to enhance clarity, readability, and ATS compatibility without fabricating experience.

---

# ✨ Key Features

## 📄 Resume Analysis

- Upload PDF or DOCX resumes
- Intelligent resume parsing
- ATS compatibility analysis
- Overall resume quality score
- Section-wise feedback

---

## 🎯 Job Description Matching

- Compare resume against any job description
- Skill gap detection
- Keyword coverage analysis
- Match percentage calculation
- Personalized improvement suggestions

---

## 🤖 AI Resume Rewriter

One of HireWise AI's core features.

Instead of creating fake achievements, the AI:

- Rewrites existing bullet points
- Improves readability
- Makes content more impactful
- Preserves factual accuracy
- Prevents fabricated experience using AI guardrails

---

## 📊 Smart Dashboard

- Resume insights
- ATS Score
- Match Percentage
- Skill Analysis
- Improvement Suggestions

---

## 🌙 Modern User Experience

- Responsive UI
- Light & Dark Mode
- Fast and intuitive workflow
- Professional SaaS-inspired design

---

# 💡 Why HireWise AI?

Many resume tools prioritize keyword stuffing or generate content that candidates have never actually done.

HireWise AI takes a different approach.

Our goal is to help candidates present their **real experience in the best possible way**, ensuring resumes remain authentic while significantly improving ATS performance and readability.

---

# 🏗️ System Architecture

```text
                Resume Upload
                      │
                      ▼
             Resume Parser Engine
                      │
                      ▼
             AI Analysis Pipeline
                      │
     ┌────────────────┼─────────────────┐
     │                │                 │
     ▼                ▼                 ▼
 ATS Analysis     JD Matching     Resume Rewriter
     │                │                 │
     └────────────────┼─────────────────┘
                      │
                      ▼
            Smart Recommendation Engine
                      │
                      ▼
                 User Dashboard
```

---

# 🛠 Tech Stack

| Layer | Technology |
|---------|------------|
| Frontend | React, TypeScript, Vite |
| Styling | Tailwind CSS |
| Backend | FastAPI, Python |
| Database | SQLite, SQLAlchemy |
| Authentication | JWT |
| AI | Groq API, LLM |
| Resume Parsing | PyPDF, python-docx |
| Deployment | Vercel + Render |

---

# 📂 Project Structure

```text
HireWise-AI
│
├── backend/
│   ├── Authentication
│   ├── Resume Parser
│   ├── ATS Engine
│   ├── JD Matcher
│   ├── Resume Rewriter
│   ├── AI Integration
│   └── API Routes
│
├── src/
│   ├── Components
│   ├── Pages
│   ├── Hooks
│   ├── Services
│   ├── Context
│   └── Assets
│
├── public/
├── dist/
└── README.md
```

---

# 🚀 Local Development

## Clone Repository

```bash
git clone https://github.com/Arpit-tyagi001/Hirewise-AI.git

cd Hirewise-AI
```

---

## Install Frontend

```bash
npm install
```

#### Step B: Start the Vite development server
```bash
```

---

## Start Frontend

```bash
npm run dev
```

#### Step C: Open the app in your browser
Open your browser and navigate to:
👉 **[http://localhost:5173/app.html](http://localhost:5173/app.html)**

> **Note on URL**: The development entry is `http://localhost:5173/app.html`. Opening `http://localhost:5173` will display the app directly or redirect to the built asset.

---

## 🔒 Environment Configuration

The application works out of the box with default development settings. You can customize behavior using environment files:

### Backend Configuration (`backend/.env`)
Create or edit `backend/.env`:
```env
# Groq Cloud API Key (Optional: for AI bullet rewriting)
GROQ_API_KEY=gsk_your_groq_api_key_here

# OpenAI API Key (Optional fallback if Groq is not used)
OPENAI_API_KEY=sk-your_openai_key_here

# JWT Secret Key for token signing
JWT_SECRET_KEY=hirewise-ai-secret-jwt-key-2026-production

# Database Connection (Default: SQLite; or use PostgreSQL connection string)
DATABASE_URL=sqlite:///backend/hirewise.db
# For PostgreSQL: postgresql://username:password@localhost:5432/hirewise

# Allowed CORS Origins (comma-separated)
FRONTEND_URL=http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000
```

### Frontend Configuration (`.env`)
Create or edit `.env` in the root folder:
```env
# Points frontend API calls to your running backend
VITE_API_URL=http://localhost:8000
```

---

## 🧪 Running Automated Tests

HireWise AI includes 4 automated test suites covering API functionality, JWT security, data isolation, and parsing accuracy.

Run all tests from the root folder:

```bash
# 1. Test All FastAPI Endpoints (Health, Upload, Analyze, JD Match, History)
python backend/test_api.py

# 2. Test JWT Authentication & Per-User Data Access Isolation
python backend/test_auth.py

# 3. Test Security Controls (MIME magic-bytes check, Path traversal, 10MB limit)
python backend/test_security.py

# 4. Test Multi-Column PDF Parsing & Kerning Artifact Correction
python backend/test_parser.py
```

*Expected output: All 4 test suites complete with `[SUCCESS]` and zero failures.*

---

## 📡 API Endpoints Overview

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/health` | Public | System status and API version |
| `POST` | `/auth/register` | Public | Create new recruiter/user account, returns JWT |
| `POST` | `/auth/login` | Public | Authenticate user credentials, returns JWT |
| `GET` | `/auth/me` | Protected | Fetch currently logged-in user profile |
| `POST` | `/upload` | Public | Upload resume and receive extracted structured JSON |
| `POST` | `/analyze` | Public / Auth | Full 10-dimension ATS scoring; links to user if logged in |
| `POST` | `/match-jd` | Public / Auth | Calculate TF-IDF & skill overlap against Job Description |
| `POST` | `/rewrite-resume` | Public / Auth | Generate bullet-by-bullet rewrites tailored to target JD |
| `POST` | `/export-tailored-resume` | Public / Auth | Download customized `.docx` resume with accepted edits |
| `GET` | `/history` | Protected | Retrieve all historical analyses belonging to current user |
| `GET` | `/analysis/{id}` | Protected | Retrieve specific analysis report by ID |
| `DELETE` | `/analysis/{id}` | Protected | Delete analysis record owned by current user |

Explore and test all endpoints interactively in your browser at `http://127.0.0.1:8000/docs`.

---

## 🛡 Security & Production Readiness

1. **Payload Size Guardrails**: Starlette middleware intercepts payloads larger than 10MB before reading into memory, protecting against DoS memory exhaustion.
2. **True File Type Validation**: Validates actual magic-byte file headers (`%PDF-` for PDFs, `PK\x03\x04` for DOCX) rather than trusting client file extensions.
3. **Filename Sanitization**: Cleans file paths using strict regex (`re.sub(r'[^a-zA-Z0-9._-]', '_', filename)`) to prevent path traversal directory attacks.
4. **Data Isolation**: Database queries enforce `user_id == current_user.id`. User A cannot access, view, or delete resumes uploaded by User B.
5. **Safe Database Migrations**: Alembic handles database schema transitions cleanly without dropping user records.
6. **Production Build**: Building with `npm run build` runs TypeScript type checks (`tsc -b`) and generates an optimized production bundle in `dist/`.

---

## ❓ Troubleshooting & FAQs

### Q: Why do I see a blank page or 404 when opening `http://localhost:5173`?
**A:** Navigate directly to **`http://localhost:5173/app.html`**. Vite is configured to use `app.html` as the source template to support both live development and standalone builds.

### Q: Does resume rewriting require a paid OpenAI key?
**A:** No! HireWise AI has an intelligent built-in **Rule-Based NLP Engine** that replaces weak verbs and weaves in candidate skills without needing any external API. If you add a free [Groq Cloud](https://console.groq.com/) API key in `backend/.env`, it will automatically unlock advanced LLM tailoring.

### Q: Can I run this in Docker or deploy to production?
**A:** Yes. The frontend can be deployed statically on Vercel, Netlify, or AWS S3 (see `vercel.json`). The backend can be run in any container or cloud host (Render, Fly.io, AWS EC2, DigitalOcean) using `uvicorn backend.main:app --host 0.0.0.0 --port 8000`.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
---

## Backend

```bash
pip install -r requirements.txt

uvicorn backend.main:app --reload
```

Backend runs on

```
http://localhost:8000
```

Swagger Documentation

```
http://localhost:8000/docs
```

---

# 🌐 Deployment

## Frontend

**Vercel**

https://hirewise-ai-two.vercel.app/

---

## Backend API

**Render**

https://hirewise-ai-backend.onrender.com

---

# 📸 Screenshots

> Replace these placeholders with actual screenshots.

- 🏠 Landing Page
- 📄 Resume Upload
- 📊 ATS Analysis
- 🎯 Job Description Matching
- 🤖 Resume Rewriter
- 📈 Dashboard

---

# 🗺 Roadmap

## Completed

- [x] Resume Parsing
- [x] ATS Analysis
- [x] Job Description Matching
- [x] Resume Rewriter
- [x] AI Guardrails
- [x] REST API
- [x] Responsive UI

## Upcoming

- [ ] User Authentication
- [ ] Resume History
- [ ] Cover Letter Generator
- [ ] AI Interview Preparation
- [ ] Resume Version Control
- [ ] Recruiter Dashboard
- [ ] Portfolio Analyzer
- [ ] Multi-language Resume Support

---

# 🤝 Contributing

Contributions are welcome!

If you'd like to improve HireWise AI:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Open a Pull Request

---

# 👨‍💻 Author

## Arpit Tyagi

Computer Science Engineering Student | Full Stack Developer | AI/ML Enthusiast

- 💼 LinkedIn: https://www.linkedin.com/in/arpit-tyagi1000/
- 💻 GitHub: https://github.com/Arpit-tyagi001

---

# ⭐ Support

If you found this project useful, please consider giving it a **⭐ Star** on GitHub.

It motivates further development and helps others discover the project.

---

## 📜 License

This project is released under the **MIT License**.

Feel free to use, modify, and contribute.
````
