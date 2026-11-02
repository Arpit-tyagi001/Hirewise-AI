"""
SQLAlchemy ORM models for Resume Analysis system, User authentication, and JD-Aware Rewrite sessions.
"""

from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    """User account model for authentication and access control."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True, default="")
    role = Column(String(50), nullable=False, default="recruiter")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    analyses = relationship("ResumeAnalysis", back_populates="user", cascade="all, delete-orphan")
    rewrite_sessions = relationship("ResumeRewriteSession", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class ResumeAnalysis(Base):
    """Stores full analysis history including parsed JSON, ATS score, and JD matching data."""
    __tablename__ = "resume_analyses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    candidate_name = Column(String(255), nullable=True, default="Candidate")
    candidate_email = Column(String(255), nullable=True, default="")
    
    # Structured JSON data
    parsed_data = Column(JSON, nullable=False)
    ats_score = Column(Float, nullable=False)
    ats_level = Column(String(100), nullable=False)
    section_scores = Column(JSON, nullable=False)
    suggestions = Column(JSON, nullable=False)
    
    # Optional JD Match results
    jd_match_data = Column(JSON, nullable=True)
    cover_letter_data = Column(JSON, nullable=True)
    interview_prep_data = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="analyses")
    rewrite_sessions = relationship("ResumeRewriteSession", back_populates="analysis", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "file_name": self.file_name,
            "file_type": self.file_type,
            "candidate_name": self.candidate_name,
            "candidate_email": self.candidate_email,
            "parsed_data": self.parsed_data,
            "ats_score": self.ats_score,
            "ats_level": self.ats_level,
            "section_scores": self.section_scores,
            "suggestions": self.suggestions,
            "jd_match_data": self.jd_match_data,
            "cover_letter_data": self.cover_letter_data,
            "interview_prep_data": self.interview_prep_data,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class ResumeRewriteSession(Base):
    """Stores JD-aware resume rewrite sessions and candidate accepted/rejected edits."""
    __tablename__ = "resume_rewrite_sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    analysis_id = Column(Integer, ForeignKey("resume_analyses.id", ondelete="CASCADE"), nullable=True, index=True)
    job_description = Column(Text, nullable=False)
    rewrites = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="rewrite_sessions")
    analysis = relationship("ResumeAnalysis", back_populates="rewrite_sessions")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "analysis_id": self.analysis_id,
            "job_description": self.job_description,
            "rewrites": self.rewrites,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
