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

---

## Start Frontend

```bash
npm run dev
```

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
