"""
FastAPI Application Entrypoint for AI Resume Analyzer System.
Exposes endpoints for Authentication, File Uploads, ATS Analysis, Job Description Matching, and History Retrieval.
Includes security controls: JWT authentication, data isolation per user, 10MB file size limits,
MIME magic-bytes validation, filename sanitization, CORS restriction via FRONTEND_URL, and payload size middleware.
"""

from datetime import datetime, timedelta
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure backend directory is in python module search path
backend_dir = str(Path(__file__).parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from dotenv import load_dotenv

# Force-load environment variables, prioritizing backend/.env overrides
load_dotenv(Path(__file__).parent / ".env", override=True)
load_dotenv(Path(__file__).parent.parent / ".env", override=True)

# Add this temporarily to verify the correct key is loaded
print(f"DEBUG KEY: {str(os.getenv('GROQ_API_KEY'))[:8]}...")

from io import BytesIO
import zipfile
from fastapi import APIRouter, Depends, FastAPI, File, HTTPException, Request, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import OAuth2PasswordBearer
import bcrypt
import jwt
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

import slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from ats_scorer import ATSScorer
from database import get_db, init_db
from jd_matcher import JDMatcher
import models
from resume_parser import ResumeParser
from rewriter import ResumeRewriter
from cover_letter_generator import CoverLetterGenerator
from interview_prep_generator import InterviewPrepGenerator

# Security Constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB limit
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "hirewise-ai-secret-jwt-key-2026-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 Hours

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


class LimitUploadSizeMiddleware(BaseHTTPMiddleware):
    """Starlette middleware to reject payload requests exceeding 10MB at the request header level."""

    def __init__(self, app: ASGIApp, max_upload_size: int = MAX_FILE_SIZE):
        super().__init__(app)
        self.max_upload_size = max_upload_size

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > self.max_upload_size:
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={"detail": "Request payload exceeds maximum allowed size limit of 10MB."}
                    )
            except ValueError:
                pass
        return await call_next(request)


# Initialize database tables on startup
init_db()

app = FastAPI(
    title="HireWise AI Resume Analyzer API",
    description="Production ATS Resume Parsing, Scoring, and Job Description Matching Engine with JWT Auth",
    version="1.1.0"
)

# Add Request Size Limit Middleware (DoS protection)
app.add_middleware(LimitUploadSizeMiddleware, max_upload_size=MAX_FILE_SIZE)

# Configurable CORS origins via FRONTEND_URL environment variable
frontend_env = os.getenv("FRONTEND_URL", "https://hirewise-ai-two.vercel.app,http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000")
allowed_origins = [url.strip() for url in frontend_env.split(",") if url.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

parser = ResumeParser()
scorer = ATSScorer()
matcher = JDMatcher()


# Pydantic Schemas
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = ""


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


class JDMatchRequest(BaseModel):
    analysis_id: Optional[int] = Field(None, description="Existing analysis record ID")
    parsed_data: Optional[Dict[str, Any]] = Field(None, description="Direct parsed resume JSON")
    job_description: str = Field(..., description="Target Job Description text")


class AnalysisResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    file_name: str
    file_type: str
    candidate_name: str
    candidate_email: str
    parsed_data: Dict[str, Any]
    ats_score: float
    ats_level: str
    section_scores: Dict[str, Any]
    suggestions: List[Dict[str, Any]]
    jd_match_data: Optional[Dict[str, Any]] = None
    cover_letter_data: Optional[Dict[str, Any]] = None
    interview_prep_data: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None


class GenerateCoverLetterRequest(BaseModel):
    analysis_id: int = Field(..., description="ID of existing resume analysis record")
    job_description: str = Field(..., description="Target Job Description text")
    company_name: Optional[str] = Field("Hiring Team", description="Target Company Name")
    job_title: Optional[str] = Field(None, description="Target Job Title")
    tone: Optional[str] = Field("professional", description="Tone of cover letter")
    api_key: Optional[str] = Field(None, description="Optional Groq API key")


class ExportCoverLetterRequest(BaseModel):
    analysis_id: int = Field(..., description="ID of existing resume analysis record")
    company_name: Optional[str] = Field("Hiring Team", description="Target Company Name")
    job_title: Optional[str] = Field("Target Role", description="Target Job Title")
    cover_letter_text: str = Field(..., description="Full text of the cover letter to export")


class InterviewPrepRequest(BaseModel):
    analysis_id: int = Field(..., description="ID of existing resume analysis record")
    job_description: str = Field(..., description="Target Job Description text")
    api_key: Optional[str] = Field(None, description="Optional Groq API key")


class RewriteResumeRequest(BaseModel):
    analysis_id: int = Field(..., description="ID of existing resume analysis record")
    job_description: str = Field(..., description="Target Job Description text to tailor against")
    api_key: Optional[str] = Field(None, description="Optional Groq API key")


class ExportTailoredResumeRequest(BaseModel):
    analysis_id: int = Field(..., description="ID of existing resume analysis record")
    accepted_rewrites: List[Dict[str, Any]] = Field(..., description="List of accepted bullet point rewrites")

class ExportApplicationBundleRequest(BaseModel):
    analysis_id: int = Field(..., description="ID of existing resume analysis record")
    accepted_rewrites: Optional[List[Dict[str, Any]]] = Field(None, description="Optional accepted rewrites for resume")
    cover_letter_text: Optional[str] = Field(None, description="Custom cover letter text to package")
    company_name: Optional[str] = Field("Hiring Team", description="Target Company Name")
    job_title: Optional[str] = Field("Target Role", description="Target Job Title")



# Helper Auth Functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8')[:72], hashed_password.encode('utf-8'))
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> models.User:
    """FastAPI dependency requiring valid JWT authentication token."""
    auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = auth_header.strip()
    if token.lower().startswith("bearer "):
        token = token[7:].strip()

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_raw = payload.get("sub")
        if user_id_raw is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token payload.",
                headers={"WWW-Authenticate": "Bearer"}
            )
        user_id = int(user_id_raw)
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or token expired.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with token not found.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user


def get_optional_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[models.User]:
    """FastAPI dependency for optional auth (supports anonymous demo mode)."""
    auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
    if not auth_header:
        return None

    token = auth_header.strip()
    if token.lower().startswith("bearer "):
        token = token[7:].strip()

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_raw = payload.get("sub")
        if user_id_raw is None:
            return None
        user_id = int(user_id_raw)
        return db.query(models.User).filter(models.User.id == user_id).first()
    except Exception as e:
        print("DEBUG optional auth exc:", e)
        return None


def sanitize_filename(filename: str) -> str:
    """Sanitize uploaded file name to prevent path traversal and unsafe characters."""
    clean_name = Path(filename).name
    clean_name = re.sub(r'[^a-zA-Z0-9._-]', '_', clean_name)
    return clean_name or "uploaded_resume"


def validate_file_security(filename: str, content: bytes) -> str:
    """Validates file size (max 10MB), extension, and real magic-byte signature."""
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds maximum allowed limit of 10MB."
        )

    fname_lower = filename.lower()
    if not (fname_lower.endswith(".pdf") or fname_lower.endswith(".docx") or fname_lower.endswith(".doc")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file extension. Please upload a PDF (.pdf) or Word document (.docx)."
        )

    file_type = "pdf" if fname_lower.endswith(".pdf") else "docx"
    header = content[:10]

    if file_type == "pdf":
        if not header.startswith(b"%PDF-"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MIME type validation failed: File content is not a valid PDF document."
            )
    elif file_type == "docx":
        if not (header.startswith(b"PK\x03\x04") or header.startswith(b"\xd0\xcf\11\xe0")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MIME type validation failed: File content is not a valid Word (.docx) document."
            )

    return file_type


# Routes: Health & Auth
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "HireWise AI Resume Analyzer API", "version": "1.1.0"}

@app.post("/auth/register", response_model=AuthTokenResponse, tags=["Authentication"])
def register_user(payload: UserRegisterRequest, db: Session = Depends(get_db)):
    """Register a new user account and return JWT access token."""
    existing_user = db.query(models.User).filter(models.User.email == payload.email.lower().strip()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    hashed_pw = get_password_hash(payload.password)
    new_user = models.User(
        email=payload.email.lower().strip(),
        hashed_password=hashed_pw,
        full_name=payload.full_name or payload.email.split("@")[0].title(),
        role="recruiter"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token({"sub": str(new_user.id), "email": new_user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": new_user.to_dict()
    }


@app.post("/auth/login", response_model=AuthTokenResponse, tags=["Authentication"])
def login_user(payload: UserLoginRequest, db: Session = Depends(get_db)):
    """Authenticate user credentials and return JWT access token."""
    user = db.query(models.User).filter(models.User.email == payload.email.lower().strip()).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token({"sub": str(user.id), "email": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.to_dict()
    }


@app.get("/auth/me", tags=["Authentication"])
def get_authenticated_user_profile(current_user: models.User = Depends(get_current_user)):
    """Return profile details for currently authenticated user."""
    return current_user.to_dict()


# Routes: Resume Analysis
@app.post("/upload", tags=["Resume Analysis"])
async def upload_resume(file: UploadFile = File(...)):
    """POST /upload: Unauthenticated upload and parse endpoint."""
    file_name = sanitize_filename(file.filename or "uploaded_resume")

    try:
        content = await file.read()
        file_type = validate_file_security(file_name, content)
        parsed_data = parser.parse(content, file_type=file_type)

        extracted_text = parsed_data.get("raw_text", "")
        if len(extracted_text.strip()) < 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No readable text detected. Please ensure this document contains selectable text and is not a scanned image."
            )

        return {
            "success": True,
            "file_name": file_name,
            "file_type": file_type,
            "parsed_data": parsed_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse resume: {str(e)}"
        )


@app.post("/analyze", response_model=AnalysisResponse, tags=["Resume Analysis"])
async def analyze_resume(
    file: UploadFile = File(...),
    current_user: Optional[models.User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    POST /analyze: Parses resume, scores ATS compliance, and saves record.
    Supports anonymous demo mode (user_id=None) or authenticated user mode (user_id=current_user.id).
    """
    file_name = sanitize_filename(file.filename or "uploaded_resume")

    try:
        content = await file.read()
        file_type = validate_file_security(file_name, content)

        # 1. Parse
        parsed_data = parser.parse(content, file_type=file_type)

        extracted_text = parsed_data.get("raw_text", "")
        if len(extracted_text.strip()) < 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No readable text detected. Please ensure this document contains selectable text and is not a scanned image."
            )

        # 2. ATS Score
        ats_result = scorer.evaluate(parsed_data)

        # 3. Store in Database (linking user_id if logged in)
        user_id = current_user.id if current_user else None
        analysis = models.ResumeAnalysis(
            user_id=user_id,
            file_name=file_name,
            file_type=file_type,
            candidate_name=parsed_data.get("name", "Candidate"),
            candidate_email=parsed_data.get("email", ""),
            parsed_data=parsed_data,
            ats_score=ats_result["overall_score"],
            ats_level=ats_result["level"],
            section_scores=ats_result["section_scores"],
            suggestions=ats_result["suggestions"],
            jd_match_data=None
        )

        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        return analysis.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process analysis: {str(e)}"
        )


@app.post("/match-jd", tags=["Job Description Matching"])
def match_job_description(
    payload: JDMatchRequest,
    current_user: Optional[models.User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """POST /match-jd: Compares parsed resume against target Job Description."""
    parsed_data = payload.parsed_data
    analysis_record = None

    if payload.analysis_id:
        query = db.query(models.ResumeAnalysis).filter(models.ResumeAnalysis.id == payload.analysis_id)
        if current_user:
            query = query.filter(models.ResumeAnalysis.user_id == current_user.id)
        analysis_record = query.first()
        if analysis_record and not parsed_data:
            parsed_data = analysis_record.parsed_data

    if not parsed_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either analysis_id or valid parsed_data must be provided."
        )

    jd_result = matcher.match(parsed_data, payload.job_description)

    # Save to DB record if analysis_id exists
    if analysis_record:
        analysis_record.jd_match_data = jd_result
        db.commit()

    return {
        "success": True,
        "analysis_id": payload.analysis_id,
        "match_result": jd_result
    }


# Protected Routes (User Data Isolated)
@app.get("/history", response_model=List[AnalysisResponse], tags=["History"])
def get_analysis_history(
    skip: int = 0,
    limit: int = 50,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """GET /history: Protected. Retrieves previous resume analyses belonging exclusively to current user."""
    records = db.query(models.ResumeAnalysis).filter(
        models.ResumeAnalysis.user_id == current_user.id
    ).order_by(models.ResumeAnalysis.created_at.desc()).offset(skip).limit(limit).all()
    return [r.to_dict() for r in records]


@app.get("/analysis/{analysis_id}", response_model=AnalysisResponse, tags=["History"])
def get_analysis_by_id(
    analysis_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """GET /analysis/{id}: Protected. Retrieves specific analysis record if owned by current user."""
    record = db.query(models.ResumeAnalysis).filter(
        models.ResumeAnalysis.id == analysis_id,
        models.ResumeAnalysis.user_id == current_user.id
    ).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis with ID {analysis_id} not found."
        )
    return record.to_dict()


@app.delete("/analysis/{analysis_id}", tags=["History"])
def delete_analysis_by_id(
    analysis_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """DELETE /analysis/{id}: Protected. Deletes analysis record if owned by current user."""
    record = db.query(models.ResumeAnalysis).filter(
        models.ResumeAnalysis.id == analysis_id,
        models.ResumeAnalysis.user_id == current_user.id
    ).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis with ID {analysis_id} not found."
        )
    db.delete(record)
    db.commit()
    return {"success": True, "message": f"Analysis {analysis_id} deleted successfully."}

# Initialize the limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/rewrite-resume", tags=["Resume Rewriter"])
@limiter.limit("10/minute")
async def rewrite_resume(request: Request,
    payload: RewriteResumeRequest,
    current_user: Optional[models.User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)):
    """
    POST /rewrite-resume: Bullet-by-bullet JD-aware resume tailoring engine.
    Uses rule-based NLP + LLM with HARD CONSTRAINTS against inventing candidate content.
    """
    query = db.query(models.ResumeAnalysis).filter(models.ResumeAnalysis.id == payload.analysis_id)
    if current_user:
        query = query.filter(
            (models.ResumeAnalysis.user_id == current_user.id) | (models.ResumeAnalysis.user_id.is_(None))
        )
    analysis = query.first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume analysis record #{payload.analysis_id} not found."
        )

    rewriter = ResumeRewriter(api_key=payload.api_key)
    rewrites = rewriter.rewrite_resume_bullets(
        parsed_resume=analysis.parsed_data,
        job_description=payload.job_description
    )

    session_record = models.ResumeRewriteSession(
        user_id=current_user.id if current_user else None,
        analysis_id=analysis.id,
        job_description=payload.job_description,
        rewrites=rewrites
    )
    db.add(session_record)
    db.commit()
    db.refresh(session_record)

    return {
        "session_id": session_record.id,
        "analysis_id": analysis.id,
        "user_id": session_record.user_id,
        "total_bullets_rewritten": len(rewrites),
        "rewrites": rewrites
    }


@app.post("/export-tailored-resume", tags=["Resume Rewriter"])
def export_tailored_resume(
    payload: ExportTailoredResumeRequest,
    current_user: Optional[models.User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    POST /export-tailored-resume: Generates and streams tailored DOCX resume containing only accepted bullet edits.
    """
    query = db.query(models.ResumeAnalysis).filter(models.ResumeAnalysis.id == payload.analysis_id)
    if current_user:
        query = query.filter(
            (models.ResumeAnalysis.user_id == current_user.id) | (models.ResumeAnalysis.user_id.is_(None))
        )
    analysis = query.first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume analysis record #{payload.analysis_id} not found."
        )

    rewriter = ResumeRewriter()
    docx_doc = rewriter.export_tailored_docx(
        parsed_resume=analysis.parsed_data,
        accepted_rewrites=payload.accepted_rewrites
    )

    buffer = BytesIO()
    docx_doc.save(buffer)
    buffer.seek(0)

    filename = f"Tailored_Resume_{analysis.candidate_name.replace(' ', '_') if analysis.candidate_name else 'Candidate'}.docx"
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@app.get("/rewrite-sessions", tags=["Resume Rewriter"])
def get_rewrite_sessions(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """GET /rewrite-sessions: Returns all saved rewrite sessions belonging to current user."""
    sessions = db.query(models.ResumeRewriteSession).filter(
        models.ResumeRewriteSession.user_id == current_user.id
    ).order_by(models.ResumeRewriteSession.created_at.desc()).all()
    return [s.to_dict() for s in sessions]


@app.post("/generate-cover-letter", tags=["Cover Letter Generator"])
def generate_cover_letter(
    payload: GenerateCoverLetterRequest,
    current_user: Optional[models.User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """POST /generate-cover-letter: Generates an authentic, tailored cover letter citing candidate background."""
    query = db.query(models.ResumeAnalysis).filter(models.ResumeAnalysis.id == payload.analysis_id)
    if current_user:
        query = query.filter((models.ResumeAnalysis.user_id == current_user.id) | (models.ResumeAnalysis.user_id.is_(None)))
    analysis = query.first()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Analysis record #{payload.analysis_id} not found.")

    generator = CoverLetterGenerator(api_key=payload.api_key)
    result = generator.generate(
        parsed_resume=analysis.parsed_data,
        job_description=payload.job_description,
        company_name=payload.company_name,
        job_title=payload.job_title,
        tone=payload.tone or "professional"
    )

    analysis.cover_letter_data = result
    db.commit()

    return {
        "success": True,
        "analysis_id": analysis.id,
        "cover_letter": result
    }


@app.post("/export-cover-letter", tags=["Cover Letter Generator"])
def export_cover_letter(
    payload: ExportCoverLetterRequest,
    current_user: Optional[models.User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """POST /export-cover-letter: Generates and streams a formatted DOCX cover letter document."""
    query = db.query(models.ResumeAnalysis).filter(models.ResumeAnalysis.id == payload.analysis_id)
    if current_user:
        query = query.filter((models.ResumeAnalysis.user_id == current_user.id) | (models.ResumeAnalysis.user_id.is_(None)))
    analysis = query.first()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Analysis record #{payload.analysis_id} not found.")

    generator = CoverLetterGenerator()
    doc = generator.export_docx(
        candidate_name=analysis.candidate_name or "Candidate",
        candidate_email=analysis.candidate_email or "",
        candidate_phone=analysis.parsed_data.get("phone", ""),
        candidate_location=analysis.parsed_data.get("location", ""),
        company_name=payload.company_name or "Hiring Organization",
        job_title=payload.job_title or "Target Role",
        cover_letter_text=payload.cover_letter_text
    )

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    safe_candidate = re.sub(r'[^a-zA-Z0-9_-]', '_', analysis.candidate_name or 'Candidate')
    safe_company = re.sub(r'[^a-zA-Z0-9_-]', '_', payload.company_name or 'Company')
    filename = f"Cover_Letter_{safe_candidate}_{safe_company}.docx"

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@app.post("/interview-prep", tags=["AI Interview Prep"])
def generate_interview_prep(
    payload: InterviewPrepRequest,
    current_user: Optional[models.User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """POST /interview-prep: Generates structured Technical, Skill Gap, and Behavioral STAR questions."""
    query = db.query(models.ResumeAnalysis).filter(models.ResumeAnalysis.id == payload.analysis_id)
    if current_user:
        query = query.filter((models.ResumeAnalysis.user_id == current_user.id) | (models.ResumeAnalysis.user_id.is_(None)))
    analysis = query.first()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Analysis record #{payload.analysis_id} not found.")

    generator = InterviewPrepGenerator(api_key=payload.api_key)
    result = generator.generate(
        parsed_resume=analysis.parsed_data,
        job_description=payload.job_description
    )

    analysis.interview_prep_data = result
    db.commit()

    return {
        "success": True,
        "analysis_id": analysis.id,
        "interview_prep": result
    }


@app.post("/export-application-bundle", tags=["Application Bundle"])
def export_application_bundle(
    payload: ExportApplicationBundleRequest,
    current_user: Optional[models.User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    POST /export-application-bundle:
    Dynamically packages in-memory:
    1. Tailored Resume (.docx)
    2. Cover Letter (.docx)
    3. AI Interview Preparation Guide (.md)
    into a compressed ZIP archive and streams it directly to the client.
    """
    query = db.query(models.ResumeAnalysis).filter(models.ResumeAnalysis.id == payload.analysis_id)
    if current_user:
        query = query.filter((models.ResumeAnalysis.user_id == current_user.id) | (models.ResumeAnalysis.user_id.is_(None)))
    analysis = query.first()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Analysis record #{payload.analysis_id} not found.")

    safe_candidate = re.sub(r'[^a-zA-Z0-9_-]', '_', analysis.candidate_name or 'Candidate')
    safe_company = re.sub(r'[^a-zA-Z0-9_-]', '_', payload.company_name or 'Company')

    # 1. Build Tailored Resume DOCX in-memory
    rewriter = ResumeRewriter()
    resume_doc = rewriter.export_tailored_docx(
        parsed_resume=analysis.parsed_data,
        accepted_rewrites=payload.accepted_rewrites or []
    )
    resume_buffer = BytesIO()
    resume_doc.save(resume_buffer)
    resume_bytes = resume_buffer.getvalue()

    # 2. Build Cover Letter DOCX in-memory
    cl_generator = CoverLetterGenerator()
    cl_text = payload.cover_letter_text
    if not cl_text:
        if analysis.cover_letter_data and analysis.cover_letter_data.get("cover_letter_text"):
            cl_text = analysis.cover_letter_data["cover_letter_text"]
        else:
            cl_res = cl_generator.generate(
                parsed_resume=analysis.parsed_data,
                job_description="Target Role",
                company_name=payload.company_name,
                job_title=payload.job_title
            )
            cl_text = cl_res.get("cover_letter_text", "")

    cl_doc = cl_generator.export_docx(
        candidate_name=analysis.candidate_name or "Candidate",
        candidate_email=analysis.candidate_email or "",
        candidate_phone=analysis.parsed_data.get("phone", ""),
        candidate_location=analysis.parsed_data.get("location", ""),
        company_name=payload.company_name or "Hiring Organization",
        job_title=payload.job_title or "Target Role",
        cover_letter_text=cl_text
    )
    cl_buffer = BytesIO()
    cl_doc.save(cl_buffer)
    cl_bytes = cl_buffer.getvalue()

    # 3. Build Interview Preparation Guide Markdown in-memory
    prep_data = analysis.interview_prep_data
    if not prep_data or not prep_data.get("questions"):
        ip_gen = InterviewPrepGenerator()
        prep_data = ip_gen.generate(
            parsed_resume=analysis.parsed_data,
            job_description="Target Role"
        )

    questions = prep_data.get("questions", [])
    md_lines = [
        f"# AI Interview Preparation Guide",
        f"**Candidate:** {analysis.candidate_name or 'Candidate'}",
        f"**Target Role:** {payload.job_title or 'Software Engineer'} at {payload.company_name or 'Company'}",
        f"**Generated On:** {datetime.now().strftime('%B %d, %Y')}",
        "",
        "---",
        ""
    ]
    if prep_data.get("summary"):
        md_lines.extend([
            "## Strategy Brief",
            prep_data["summary"],
            "",
            "---",
            ""
        ])

    md_lines.append("## Tailored Interview Questions & STAR Frameworks\n")
    for idx, q in enumerate(questions):
        cat = q.get("category", "General").title()
        q_text = q.get("question", "")
        intent = q.get("intent") or q.get("interviewer_intent", "")
        star = q.get("star_breakdown") or q.get("star_framework") or {}
        pts = q.get("talking_points") or q.get("key_talking_points") or []

        md_lines.append(f"### #{idx + 1} [{cat}] {q_text}\n")
        if intent:
            md_lines.append(f"> **🎯 Interviewer Intent:** {intent}\n")
        if star:
            md_lines.append("#### STAR Method Breakdown:")
            md_lines.append(f"- **Situation:** {star.get('situation', 'N/A')}")
            md_lines.append(f"- **Task:** {star.get('task', 'N/A')}")
            md_lines.append(f"- **Action:** {star.get('action', 'N/A')}")
            md_lines.append(f"- **Result:** {star.get('result', 'N/A')}\n")
        if pts:
            md_lines.append(f"**Key Talking Points:** {', '.join(pts)}\n")
        md_lines.append("---\n")

    prep_markdown = "\n".join(md_lines)
    prep_bytes = prep_markdown.encode("utf-8")

    # 4. Package all 3 in-memory streams into a ZIP archive
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"1_Tailored_Resume_{safe_candidate}.docx", resume_bytes)
        zf.writestr(f"2_Cover_Letter_{safe_candidate}_{safe_company}.docx", cl_bytes)
        zf.writestr(f"3_Interview_Prep_Guide_{safe_candidate}.md", prep_bytes)
        readme_content = f"""HireWise AI - Job Application Kit
Candidate: {analysis.candidate_name or 'Candidate'}
Target Role: {payload.job_title} at {payload.company_name}
ATS Match Score: {analysis.ats_score}% ({analysis.ats_level})

Contents of this bundle:
1. 1_Tailored_Resume_{safe_candidate}.docx - Formatted DOCX resume incorporating your accepted bullet optimizations.
2. 2_Cover_Letter_{safe_candidate}_{safe_company}.docx - Professional tailored cover letter mapped to company specifications.
3. 3_Interview_Prep_Guide_{safe_candidate}.md - Custom interview guide featuring technical and behavioral STAR frameworks.

Generated with HireWise AI. Good luck with your application!
"""
        zf.writestr("README.txt", readme_content)

    zip_buffer.seek(0)
    bundle_filename = f"HireWise_JobKit_{safe_candidate}_{safe_company}.zip"

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{bundle_filename}"'}
    )
