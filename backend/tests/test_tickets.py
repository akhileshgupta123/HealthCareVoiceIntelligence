"""
Tests for Tickets Router
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import uuid

from api.main import app
from api.routers.tickets import MOCK_TICKETS

client = TestClient(app)


class TestTicketsRouter:
    """Test cases for Tickets Router"""

    def test_create_ticket_success(self):
        """Test successful ticket creation"""
        ticket_data = {
            "patient_id": "PAT001",
            "subject": "Test ticket",
            "description": "Test description",
            "priority": "high",
            "category": "claims",
            "created_by": "test_user"
        }

        response = client.post("/api/v1/tickets", json=ticket_data)

        assert response.status_code == 200
        data = response.json()
        assert data["subject"] == "Test ticket"
        assert data["status"] == "open"
        assert data["patient_id"] == "PAT001"
        assert "id" in data

    def test_create_ticket_without_patient_id(self):
        """Test ticket creation without patient ID"""
        ticket_data = {
            "patient_id": None,
            "subject": "Test ticket",
            "description": "Test description",
            "priority": "medium",
            "category": "general",
            "created_by": "test_user"
        }

        response = client.post("/api/v1/tickets", json=ticket_data)

        assert response.status_code == 200
        data = response.json()
        assert data["patient_id"] is None

    def test_get_ticket_success(self):
        """Test successful ticket retrieval"""
        response = client.get("/api/v1/tickets/TKT001")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "TKT001"
        assert data["subject"] == "Claim CLM003 requires additional documentation"

    def test_get_ticket_not_found(self):
        """Test ticket retrieval with non-existent ID"""
        response = client.get("/api/v1/tickets/TKT999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_list_tickets_all(self):
        """Test listing all tickets"""
        response = client.get("/api/v1/tickets")

        assert response.status_code == 200
        data = response.json()
        assert "tickets" in data
        assert "count" in data
        assert data["count"] >= 1

    def test_list_tickets_by_patient_id(self):
        """Test listing tickets filtered by patient ID"""
        response = client.get("/api/v1/tickets?patient_id=PAT001")

        assert response.status_code == 200
        data = response.json()
        assert all(t["patient_id"] == "PAT001" for t in data["tickets"])

    def test_list_tickets_by_status(self):
        """Test listing tickets filtered by status"""
        response = client.get("/api/v1/tickets?status=open")

        assert response.status_code == 200
        data = response.json()
        assert all(t["status"] == "open" for t in data["tickets"])

    def test_list_tickets_by_both_filters(self):
        """Test listing tickets with both filters"""
        response = client.get("/api/v1/tickets?patient_id=PAT001&status=open")

        assert response.status_code == 200
        data = response.json()
        assert all(t["patient_id"] == "PAT001" and t["status"] == "open" for t in data["tickets"])

    def test_update_ticket_status(self):
        """Test updating ticket status"""
        # First create a ticket
        create_data = {
            "patient_id": "PAT002",
            "subject": "Test update",
            "description": "Test",
            "priority": "medium",
            "category": "general",
            "created_by": "test_user"
        }
        create_response = client.post("/api/v1/tickets", json=create_data)
        ticket_id = create_response.json()["id"]

        # Update the ticket
        update_response = client.put(
            f"/api/v1/tickets/{ticket_id}",
            params={"status": "in_progress", "assigned_to": "support_team"}
        )

        assert update_response.status_code == 200
        data = update_response.json()
        assert data["status"] == "in_progress"
        assert data["assigned_to"] == "support_team"

    def test_update_ticket_to_resolved(self):
        """Test updating ticket to resolved status"""
        # First create a ticket
        create_data = {
            "patient_id": "PAT003",
            "subject": "Test resolve",
            "description": "Test",
            "priority": "low",
            "category": "general",
            "created_by": "test_user"
        }
        create_response = client.post("/api/v1/tickets", json=create_data)
        ticket_id = create_response.json()["id"]

        # Update to resolved
        update_response = client.put(
            f"/api/v1/tickets/{ticket_id}",
            params={"status": "resolved"}
        )

        assert update_response.status_code == 200
        data = update_response.json()
        assert data["status"] == "resolved"
        assert data["resolved_at"] is not None

    def test_update_ticket_not_found(self):
        """Test updating non-existent ticket"""
        response = client.put(
            "/api/v1/tickets/TKT999",
            params={"status": "resolved"}
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_ticket_preserves_assigned_to(self):
        """Test that update preserves assigned_to if not provided"""
        # First create a ticket with assignment
        create_data = {
            "patient_id": "PAT004",
            "subject": "Test preserve",
            "description": "Test",
            "priority": "medium",
            "category": "general",
            "created_by": "test_user"
        }
        create_response = client.post("/api/v1/tickets", json=create_data)
        ticket_id = create_response.json()["id"]

        # Update with assignment
        client.put(
            f"/api/v1/tickets/{ticket_id}",
            params={"status": "in_progress", "assigned_to": "team1"}
        )

        # Update without new assignment
        update_response = client.put(
            f"/api/v1/tickets/{ticket_id}",
            params={"status": "resolved"}
        )

        assert update_response.status_code == 200
        data = update_response.json()
        assert data["assigned_to"] == "team1"
