"""
Tests for database models
"""

import pytest
from api.models import Claim, Check, Ticket, Eligibility, ClaimStatus, CheckStatus, TicketPriority


def test_claim_status_enum():
    """Test ClaimStatus enum values"""
    assert ClaimStatus.PENDING.value == "pending"
    assert ClaimStatus.APPROVED.value == "approved"
    assert ClaimStatus.DENIED.value == "denied"
    assert ClaimStatus.UNDER_REVIEW.value == "under_review"


def test_check_status_enum():
    """Test CheckStatus enum values"""
    assert CheckStatus.ISSUED.value == "issued"
    assert CheckStatus.PENDING.value == "pending"
    assert CheckStatus.CANCELLED.value == "cancelled"
    assert CheckStatus.CLEARED.value == "cleared"


def test_ticket_priority_enum():
    """Test TicketPriority enum values"""
    assert TicketPriority.LOW.value == "low"
    assert TicketPriority.MEDIUM.value == "medium"
    assert TicketPriority.HIGH.value == "high"
    assert TicketPriority.CRITICAL.value == "critical"


def test_claim_model():
    """Test Claim model structure"""
    claim = Claim(
        id="CLM001",
        patient_id="PAT001",
        patient_name="John Doe",
        procedure_code="99213",
        procedure_name="Office Visit",
        amount=150.00,
        status=ClaimStatus.APPROVED,
        insurance_provider="BlueCross"
    )
    assert claim.id == "CLM001"
    assert claim.patient_id == "PAT001"
    assert claim.status == ClaimStatus.APPROVED


def test_check_model():
    """Test Check model structure"""
    check = Check(
        id="CHK001",
        patient_id="PAT001",
        patient_name="John Doe",
        amount=150.00,
        status=CheckStatus.CLEARED,
        issue_date="2024-01-25T00:00:00",
        check_number="12345"
    )
    assert check.id == "CHK001"
    assert check.status == CheckStatus.CLEARED


def test_ticket_model():
    """Test Ticket model structure"""
    ticket = Ticket(
        id="TKT001",
        patient_id="PAT001",
        subject="Billing Issue",
        description="Incorrect charge on invoice",
        priority=TicketPriority.HIGH,
        category="billing",
        created_by="admin",
        status="open"
    )
    assert ticket.id == "TKT001"
    assert ticket.priority == TicketPriority.HIGH
    assert ticket.status == "open"


def test_eligibility_model():
    """Test Eligibility model structure"""
    eligibility = Eligibility(
        id="ELG001",
        patient_id="PAT001",
        patient_name="John Doe",
        insurance_provider="BlueCross",
        policy_number="POL12345",
        is_eligible=True,
        coverage_type="full",
        effective_date="2024-01-01T00:00:00",
        expiration_date="2024-12-31T23:59:59"
    )
    assert eligibility.id == "ELG001"
    assert eligibility.is_eligible is True
