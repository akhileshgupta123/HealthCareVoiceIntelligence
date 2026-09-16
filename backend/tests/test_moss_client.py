"""
Tests for Moss Client
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import asyncio

from api.moss_client import MossClientWrapper


@pytest.fixture
def mock_moss_client():
    """Mock Moss client wrapper"""
    wrapper = MossClientWrapper(
        project_id="test_project",
        project_key="test_key"
    )
    return wrapper


class TestMossClientWrapper:
    """Test cases for MossClientWrapper"""

    def test_initialization(self, mock_moss_client):
        """Test Moss client wrapper initialization"""
        assert mock_moss_client.project_id == "test_project"
        assert mock_moss_client.project_key == "test_key"
        assert mock_moss_client.client is None
        assert mock_moss_client.session_index is None

    @pytest.mark.asyncio
    async def test_initialize_success(self, mock_moss_client):
        """Test successful Moss client initialization"""
        with patch('api.moss_client.MossClient') as mock_moss, \
             patch('api.moss_client.SessionIndex') as mock_session_index:
            
            mock_moss.return_value = Mock()
            mock_session_index.return_value = Mock()
            
            await mock_moss_client.initialize()
            
            assert mock_moss_client.client is not None
            assert mock_moss_client.session_index is not None
            assert hasattr(mock_moss_client, '_knowledge_store')

    @pytest.mark.asyncio
    async def test_initialize_failure(self, mock_moss_client):
        """Test Moss client initialization failure"""
        with patch('api.moss_client.MossClient') as mock_moss:
            mock_moss.side_effect = Exception("Connection failed")
            
            await mock_moss_client.initialize()
            
            assert mock_moss_client.client is None

    @pytest.mark.asyncio
    async def test_query_session_context_with_client(self, mock_moss_client):
        """Test querying session context with active client"""
        mock_moss_client.client = Mock()
        mock_moss_client.session_index = Mock()
        
        mock_result = Mock()
        mock_result.text = "Test context"
        mock_result.score = 0.9
        mock_result.metadata = {"session_id": "test"}
        mock_moss_client.session_index.search = Mock(return_value=[mock_result])
        
        results = await mock_moss_client.query_session_context(
            query="test query",
            session_id="session-123",
            top_k=5
        )
        
        assert len(results) == 1
        assert results[0]["text"] == "Test context"

    @pytest.mark.asyncio
    async def test_query_session_context_without_client(self, mock_moss_client):
        """Test querying session context without client"""
        mock_moss_client.client = None
        
        results = await mock_moss_client.query_session_context(
            query="test query",
            session_id="session-123"
        )
        
        assert results == []

    @pytest.mark.asyncio
    async def test_query_knowledge_base_with_category(self, mock_moss_client):
        """Test querying knowledge base with category filter"""
        await mock_moss_client._index_sample_knowledge()
        
        results = await mock_moss_client.query_knowledge_base(
            query="claim submission",
            category="claims",
            top_k=5
        )
        
        assert len(results) > 0
        assert all(r["metadata"].get("category") == "claims" for r in results)

    @pytest.mark.asyncio
    async def test_query_knowledge_base_without_category(self, mock_moss_client):
        """Test querying knowledge base without category filter"""
        await mock_moss_client._index_sample_knowledge()
        
        results = await mock_moss_client.query_knowledge_base(
            query="patient",
            top_k=5
        )
        
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_query_knowledge_base_no_store(self, mock_moss_client):
        """Test querying knowledge base without initialized store"""
        results = await mock_moss_client.query_knowledge_base(
            query="test query"
        )
        
        assert results == []

    @pytest.mark.asyncio
    async def test_query_knowledge_base_no_matches(self, mock_moss_client):
        """Test querying knowledge base with no matches"""
        await mock_moss_client._index_sample_knowledge()
        
        results = await mock_moss_client.query_knowledge_base(
            query="xyz123nonexistent",
            top_k=5
        )
        
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_add_session_context_with_client(self, mock_moss_client):
        """Test adding session context with active client"""
        mock_moss_client.client = Mock()
        mock_moss_client.session_index = Mock()
        mock_moss_client.session_index.add = Mock()
        
        await mock_moss_client.add_session_context(
            session_id="session-123",
            text="Test context",
            metadata={"type": "user_input"}
        )
        
        mock_moss_client.session_index.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_session_context_without_client(self, mock_moss_client):
        """Test adding session context without client"""
        mock_moss_client.client = None
        
        await mock_moss_client.add_session_context(
            session_id="session-123",
            text="Test context",
            metadata={"type": "user_input"}
        )
        
        # Should not raise error, just return silently

    @pytest.mark.asyncio
    async def test_clear_session_with_client(self, mock_moss_client):
        """Test clearing session with active client"""
        mock_moss_client.client = Mock()
        mock_moss_client.session_index = Mock()
        mock_moss_client.session_index.clear = Mock()
        
        await mock_moss_client.clear_session("session-123")
        
        mock_moss_client.session_index.clear.assert_called_once()

    @pytest.mark.asyncio
    async def test_clear_session_without_client(self, mock_moss_client):
        """Test clearing session without client"""
        mock_moss_client.client = None
        
        await mock_moss_client.clear_session("session-123")
        
        # Should not raise error, just return silently

    @pytest.mark.asyncio
    async def test_close_with_client(self, mock_moss_client):
        """Test closing Moss client with active client"""
        mock_moss_client.client = Mock()
        mock_moss_client.client.close = Mock()
        
        await mock_moss_client.close()
        
        mock_moss_client.client.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_without_client(self, mock_moss_client):
        """Test closing Moss client without active client"""
        mock_moss_client.client = None
        
        await mock_moss_client.close()
        
        # Should not raise error

    @pytest.mark.asyncio
    async def test_index_sample_knowledge(self, mock_moss_client):
        """Test indexing sample knowledge base"""
        await mock_moss_client._index_sample_knowledge()
        
        assert hasattr(mock_moss_client, '_knowledge_store')
        assert len(mock_moss_client._knowledge_store) == 5
        assert all("id" in doc and "text" in doc for doc in mock_moss_client._knowledge_store)
