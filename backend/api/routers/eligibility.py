"""
Eligibility Router
Mock API for insurance eligibility verification
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter()


class EligibilityResponse(BaseModel):
    id: str
    patient_id: str
    patient_name: str
    insurance_provider: str
    policy_number: str
    is_eligible: bool
    coverage_type: str
    effective_date: datetime
    expiration_date: datetime


# Mock eligibility data
MOCK_ELIGIBILITY = {
    "PAT001": {
        "id": "ELG001",
        "patient_id": "PAT001",
        "patient_name": "John Doe",
        "insurance_provider": "BlueCross",
        "policy_number": "BC-123456789",
        "is_eligible": True,
        "coverage_type": "PPO",
        "effective_date": "2024-01-01T00:00:00",
        "expiration_date": "2024-12-31T23:59:59"
    },
    "PAT002": {
        "id": "ELG002",
        "patient_id": "PAT002",
        "patient_name": "Jane Smith",
        "insurance_provider": "Aetna",
        "policy_number": "AE-987654321",
        "is_eligible": True,
        "coverage_type": "HMO",
        "effective_date": "2024-01-01T00:00:00",
        "expiration_date": "2024-12-31T23:59:59"
    },
    "PAT003": {
        "id": "ELG003",
        "patient_id": "PAT003",
        "patient_name": "Robert Johnson",
        "insurance_provider": "United Healthcare",
        "policy_number": "UH-456789123",
        "is_eligible": False,
        "coverage_type": "PPO",
        "effective_date": "2023-01-01T00:00:00",
        "expiration_date": "2023-12-31T23:59:59"
    }
}


@router.get("/eligibility/{patient_id}", response_model=EligibilityResponse)
async def get_eligibility(patient_id: str):
    """Check insurance eligibility status"""
    eligibility = MOCK_ELIGIBILITY.get(patient_id)
    if not eligibility:
        raise HTTPException(status_code=404, detail="Patient eligibility not found")
    
    return EligibilityResponse(**eligibility)


@router.get("/eligibility")
async def list_eligibility():
    """List all eligibility records"""
    eligibility_list = list(MOCK_ELIGIBILITY.values())
    return {"eligibility": eligibility_list, "count": len(eligibility_list)}
