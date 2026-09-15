"""
Claims Router
Mock API for claim status and details
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import random

router = APIRouter()


class ClaimResponse(BaseModel):
    id: str
    patient_id: str
    patient_name: str
    procedure_code: str
    procedure_name: str
    date_of_service: datetime
    amount: float
    status: str
    submitted_date: datetime
    processed_date: Optional[datetime]
    insurance_provider: str
    notes: Optional[str]


# Mock claim data
MOCK_CLAIMS = {
    "CLM001": {
        "id": "CLM001",
        "patient_id": "PAT001",
        "patient_name": "John Doe",
        "procedure_code": "99213",
        "procedure_name": "Office Visit",
        "date_of_service": "2024-01-15T10:00:00",
        "amount": 150.00,
        "status": "approved",
        "submitted_date": "2024-01-15T10:00:00",
        "processed_date": "2024-01-20T14:30:00",
        "insurance_provider": "BlueCross",
        "notes": "Standard office visit for routine checkup"
    },
    "CLM002": {
        "id": "CLM002",
        "patient_id": "PAT002",
        "patient_name": "Jane Smith",
        "procedure_code": "80061",
        "procedure_name": "CBC Blood Test",
        "date_of_service": "2024-01-18T09:00:00",
        "amount": 75.00,
        "status": "pending",
        "submitted_date": "2024-01-18T09:00:00",
        "processed_date": None,
        "insurance_provider": "Aetna",
        "notes": "Routine blood work ordered by Dr. Johnson"
    },
    "CLM003": {
        "id": "CLM003",
        "patient_id": "PAT001",
        "patient_name": "John Doe",
        "procedure_code": "71020",
        "procedure_name": "Chest X-Ray",
        "date_of_service": "2024-01-20T11:00:00",
        "amount": 250.00,
        "status": "under_review",
        "submitted_date": "2024-01-20T11:00:00",
        "processed_date": None,
        "insurance_provider": "BlueCross",
        "notes": "Preventive screening - requires additional documentation"
    }
}


@router.get("/claims/{claim_id}", response_model=ClaimResponse)
async def get_claim(claim_id: str):
    """Retrieve claim status and details"""
    claim = MOCK_CLAIMS.get(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    return ClaimResponse(**claim)


@router.get("/claims")
async def list_claims(patient_id: Optional[str] = None):
    """List all claims, optionally filtered by patient"""
    claims = list(MOCK_CLAIMS.values())
    
    if patient_id:
        claims = [c for c in claims if c["patient_id"] == patient_id]
    
    return {"claims": claims, "count": len(claims)}
