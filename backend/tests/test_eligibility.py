"""
Tests for Eligibility Router
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


class TestEligibilityRouter:
    """Test cases for Eligibility Router"""

    def test_get_eligibility_eligible(self):
        """Test retrieving eligible patient"""
        response = client.get("/api/v1/eligibility/PAT001")

        assert response.status_code == 200
        data = response.json()
        assert data["patient_id"] == "PAT001"
        assert data["is_eligible"] is True
        assert data["insurance_provider"] == "BlueCross"
        assert data["coverage_type"] == "PPO"

    def test_get_eligibility_eligible_hmo(self):
        """Test retrieving eligible patient with HMO"""
        response = client.get("/api/v1/eligibility/PAT002")

        assert response.status_code == 200
        data = response.json()
        assert data["is_eligible"] is True
        assert data["coverage_type"] == "HMO"
        assert data["insurance_provider"] == "Aetna"

    def test_get_eligibility_not_eligible(self):
        """Test retrieving ineligible patient"""
        response = client.get("/api/v1/eligibility/PAT003")

        assert response.status_code == 200
        data = response.json()
        assert data["is_eligible"] is False
        assert data["insurance_provider"] == "United Healthcare"

    def test_get_eligibility_not_found(self):
        """Test eligibility retrieval with non-existent patient"""
        response = client.get("/api/v1/eligibility/PAT999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_list_eligibility_all(self):
        """Test listing all eligibility records"""
        response = client.get("/api/v1/eligibility")

        assert response.status_code == 200
        data = response.json()
        assert "eligibility" in data
        assert "count" in data
        assert data["count"] >= 3

    def test_eligibility_response_structure(self):
        """Test eligibility response has all required fields"""
        response = client.get("/api/v1/eligibility/PAT001")

        assert response.status_code == 200
        data = response.json()
        required_fields = ["id", "patient_id", "patient_name", "insurance_provider", "policy_number", "is_eligible", "coverage_type", "effective_date", "expiration_date"]
        for field in required_fields:
            assert field in data

    def test_eligibility_policy_number_format(self):
        """Test policy number format is preserved"""
        response = client.get("/api/v1/eligibility/PAT001")

        assert response.status_code == 200
        data = response.json()
        assert data["policy_number"] == "BC-123456789"
