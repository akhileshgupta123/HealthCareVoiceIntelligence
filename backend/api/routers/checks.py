"""
Checks Router
Mock API for check status
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter()


class CheckResponse(BaseModel):
    id: str
    claim_id: Optional[str]
    patient_id: str
    patient_name: str
    amount: float
    status: str
    issue_date: datetime
    cleared_date: Optional[datetime]
    check_number: str


# Mock check data
MOCK_CHECKS = {
    "CHK001": {
        "id": "CHK001",
        "claim_id": "CLM001",
        "patient_id": "PAT001",
        "patient_name": "John Doe",
        "amount": 150.00,
        "status": "cleared",
        "issue_date": "2024-01-22T00:00:00",
        "cleared_date": "2024-01-25T00:00:00",
        "check_number": "CHK-2024-001234"
    },
    "CHK002": {
        "id": "CHK002",
        "claim_id": None,
        "patient_id": "PAT003",
        "patient_name": "Robert Johnson",
        "amount": 500.00,
        "status": "issued",
        "issue_date": "2024-01-25T00:00:00",
        "cleared_date": None,
        "check_number": "CHK-2024-001235"
    },
    "CHK003": {
        "id": "CHK003",
        "claim_id": "CLM002",
        "patient_id": "PAT002",
        "patient_name": "Jane Smith",
        "amount": 75.00,
        "status": "pending",
        "issue_date": None,
        "cleared_date": None,
        "check_number": "CHK-2024-001236"
    }
}


@router.get("/checks/{check_id}", response_model=CheckResponse)
async def get_check(check_id: str):
    """Retrieve check status"""
    check = MOCK_CHECKS.get(check_id)
    if not check:
        raise HTTPException(status_code=404, detail="Check not found")
    
    return CheckResponse(**check)


@router.get("/checks")
async def list_checks(patient_id: Optional[str] = None):
    """List all checks, optionally filtered by patient"""
    checks = list(MOCK_CHECKS.values())
    
    if patient_id:
        checks = [c for c in checks if c["patient_id"] == patient_id]
    
    return {"checks": checks, "count": len(checks)}
