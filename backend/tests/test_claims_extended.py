"""
Extended Tests for Claims Router
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


class TestClaimsRouterExtended:
    """Extended test cases for Claims Router"""

    def test_get_claim_approved(self):
        """Test retrieving approved claim"""
        response = client.get("/api/v1/claims/CLM001")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "CLM001"
        assert data["status"] == "approved"
        assert data["processed_date"] is not None

    def test_get_claim_pending(self):
        """Test retrieving pending claim"""
        response = client.get("/api/v1/claims/CLM002")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"
        assert data["processed_date"] is None

    def test_get_claim_under_review(self):
        """Test retrieving claim under review"""
        response = client.get("/api/v1/claims/CLM003")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "under_review"
        assert "additional documentation" in data["notes"].lower()

    def test_get_claim_not_found(self):
        """Test claim retrieval with non-existent ID"""
        response = client.get("/api/v1/claims/CLM999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_list_claims_all(self):
        """Test listing all claims"""
        response = client.get("/api/v1/claims")

        assert response.status_code == 200
        data = response.json()
        assert "claims" in data
        assert "count" in data
        assert data["count"] >= 3

    def test_list_claims_by_patient_id(self):
        """Test listing claims filtered by patient ID"""
        response = client.get("/api/v1/claims?patient_id=PAT001")

        assert response.status_code == 200
        data = response.json()
        assert all(c["patient_id"] == "PAT001" for c in data["claims"])

    def test_list_claims_by_patient_id_single_result(self):
        """Test listing claims for patient with single claim"""
        response = client.get("/api/v1/claims?patient_id=PAT002")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["claims"][0]["patient_id"] == "PAT002"

    def test_list_claims_by_patient_id_no_results(self):
        """Test listing claims with patient ID that has no claims"""
        response = client.get("/api/v1/claims?patient_id=PAT999")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["claims"] == []

    def test_claim_response_structure(self):
        """Test claim response has all required fields"""
        response = client.get("/api/v1/claims/CLM001")

        assert response.status_code == 200
        data = response.json()
        required_fields = ["id", "patient_id", "patient_name", "procedure_code", "procedure_name", "date_of_service", "amount", "status", "submitted_date", "processed_date", "insurance_provider", "notes"]
        for field in required_fields:
            assert field in data

    def test_claim_procedure_code_format(self):
        """Test procedure code format is preserved"""
        response = client.get("/api/v1/claims/CLM001")

        assert response.status_code == 200
        data = response.json()
        assert data["procedure_code"] == "99213"

    def test_claim_amount_validation(self):
        """Test claim amount is positive"""
        response = client.get("/api/v1/claims/CLM001")

        assert response.status_code == 200
        data = response.json()
        assert data["amount"] > 0

    def test_claim_insurance_provider(self):
        """Test insurance provider is correctly returned"""
        response = client.get("/api/v1/claims/CLM001")

        assert response.status_code == 200
        data = response.json()
        assert data["insurance_provider"] == "BlueCross"
