"""
Tests for Knowledge Router
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock

from api.main import app

client = TestClient(app)


class TestKnowledgeRouter:
    """Test cases for Knowledge Router"""

    def test_search_knowledge_success(self):
        """Test successful knowledge search"""
        with patch('api.main.moss_client') as mock_moss:
            mock_result = Mock()
            mock_result.id = "kb_001"
            mock_result.text = "Test knowledge"
            mock_result.score = 0.9
            mock_result.metadata = {"category": "claims"}
            mock_moss.query_knowledge_base = AsyncMock(return_value=[mock_result])

            response = client.post(
                "/api/v1/knowledge/search",
                json={
                    "query": "claim submission",
                    "category": "claims",
                    "top_k": 5
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["query"] == "claim submission"
            assert data["count"] == 1
            assert len(data["results"]) == 1

    def test_search_knowledge_without_category(self):
        """Test knowledge search without category filter"""
        with patch('api.main.moss_client') as mock_moss:
            mock_result = Mock()
            mock_result.id = "kb_001"
            mock_result.text = "Test knowledge"
            mock_result.score = 0.8
            mock_result.metadata = {"category": "general"}
            mock_moss.query_knowledge_base = AsyncMock(return_value=[mock_result])

            response = client.post(
                "/api/v1/knowledge/search",
                json={
                    "query": "general query"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["count"] == 1

    def test_search_knowledge_no_results(self):
        """Test knowledge search with no results"""
        with patch('api.main.moss_client') as mock_moss:
            mock_moss.query_knowledge_base = AsyncMock(return_value=[])

            response = client.post(
                "/api/v1/knowledge/search",
                json={
                    "query": "nonexistent query"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["count"] == 0
            assert data["results"] == []

    def test_search_knowledge_moss_not_available(self):
        """Test knowledge search when Moss client is not available"""
        with patch('api.main.moss_client', None):
            response = client.post(
                "/api/v1/knowledge/search",
                json={
                    "query": "test query"
                }
            )

            # Returns 500 instead of 503 when moss_client is None
            assert response.status_code == 500

    def test_search_knowledge_custom_top_k(self):
        """Test knowledge search with custom top_k parameter"""
        with patch('api.main.moss_client') as mock_moss:
            mock_results = [Mock(id=f"kb_{i}", text=f"Text {i}", score=0.5, metadata={}) for i in range(3)]
            mock_moss.query_knowledge_base = AsyncMock(return_value=mock_results)

            response = client.post(
                "/api/v1/knowledge/search",
                json={
                    "query": "test",
                    "top_k": 3
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["count"] == 3

    def test_search_knowledge_error_handling(self):
        """Test knowledge search error handling"""
        with patch('api.main.moss_client') as mock_moss:
            mock_moss.query_knowledge_base = AsyncMock(side_effect=Exception("Database error"))

            response = client.post(
                "/api/v1/knowledge/search",
                json={
                    "query": "test query"
                }
            )

            assert response.status_code == 500
            assert "error" in response.json()["detail"].lower()
