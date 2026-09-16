"""
Tests for claims router
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


def test_get_claim_by_id(client):
    """Test getting a specific claim"""
    response = client.get("/api/v1/claims/CLM001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "CLM001"
    assert data["patient_id"] == "PAT001"
    assert data["patient_name"] == "John Doe"
    assert data["status"] == "approved"


def test_get_claim_not_found(client):
    """Test getting a non-existent claim"""
    response = client.get("/api/v1/claims/CLM999")
    assert response.status_code == 404


def test_list_all_claims(client):
    """Test listing all claims"""
    response = client.get("/api/v1/claims")
    assert response.status_code == 200
    data = response.json()
    assert "claims" in data
    assert "count" in data
    assert len(data["claims"]) == 3


def test_list_claims_by_patient(client):
    """Test listing claims filtered by patient"""
    response = client.get("/api/v1/claims?patient_id=PAT001")
    assert response.status_code == 200
    data = response.json()
    assert "claims" in data
    assert all(claim["patient_id"] == "PAT001" for claim in data["claims"])
