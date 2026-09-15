"""
Database Models
SQLAlchemy models for healthcare data
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, Float, Boolean, Enum
from sqlalchemy.sql import func
from api.database import Base
import enum


class ClaimStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    UNDER_REVIEW = "under_review"


class CheckStatus(str, enum.Enum):
    ISSUED = "issued"
    PENDING = "pending"
    CANCELLED = "cancelled"
    CLEARED = "cleared"


class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Claim(Base):
    __tablename__ = "claims"
    
    id = Column(String, primary_key=True)
    patient_id = Column(String, index=True)
    patient_name = Column(String)
    procedure_code = Column(String)
    procedure_name = Column(String)
    date_of_service = Column(DateTime)
    amount = Column(Float)
    status = Column(Enum(ClaimStatus))
    submitted_date = Column(DateTime, default=func.now())
    processed_date = Column(DateTime, nullable=True)
    insurance_provider = Column(String)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Check(Base):
    __tablename__ = "checks"
    
    id = Column(String, primary_key=True)
    claim_id = Column(String, nullable=True)
    patient_id = Column(String, index=True)
    patient_name = Column(String)
    amount = Column(Float)
    status = Column(Enum(CheckStatus))
    issue_date = Column(DateTime)
    cleared_date = Column(DateTime, nullable=True)
    check_number = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(String, primary_key=True)
    patient_id = Column(String, index=True, nullable=True)
    subject = Column(String)
    description = Column(Text)
    priority = Column(Enum(TicketPriority))
    status = Column(String, default="open")
    category = Column(String)
    created_by = Column(String)
    assigned_to = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    resolved_at = Column(DateTime, nullable=True)


class Eligibility(Base):
    __tablename__ = "eligibility"
    
    id = Column(String, primary_key=True)
    patient_id = Column(String, index=True)
    patient_name = Column(String)
    insurance_provider = Column(String)
    policy_number = Column(String)
    is_eligible = Column(Boolean)
    coverage_type = Column(String)
    effective_date = Column(DateTime)
    expiration_date = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
