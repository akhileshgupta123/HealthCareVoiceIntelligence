"""
Tests for Worker Agents
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import datetime

from agents.workers import BaseWorkerAgent, ClaimsAgent, KnowledgeAgent, EscalationAgent


@pytest.fixture
def mock_moss_client():
    """Mock Moss client"""
    client = Mock()
    client.query_knowledge_base = AsyncMock(return_value=[])
    return client


class TestBaseWorkerAgent:
    """Test cases for BaseWorkerAgent"""

    def test_initialization(self, mock_moss_client):
        """Test base agent initialization"""
        with patch('agents.workers.ChatOpenAI') as mock_chat_openai:
            mock_chat_openai.return_value = Mock()
            
            agent = BaseWorkerAgent(mock_moss_client)
            
            assert agent.moss_client == mock_moss_client
            assert agent.api_base_url == "http://localhost:8000/api/v1"

    def test_initialization_custom_api_url(self, mock_moss_client):
        """Test base agent initialization with custom API URL"""
        with patch.dict('os.environ', {'API_BASE_URL': 'http://custom:8000/api/v1'}):
            with patch('agents.workers.ChatOpenAI') as mock_chat_openai:
                mock_chat_openai.return_value = Mock()
                
                agent = BaseWorkerAgent(mock_moss_client)
                
                assert agent.api_base_url == "http://custom:8000/api/v1"

    @pytest.mark.asyncio
    async def test_query_moss_knowledge_with_results(self, mock_moss_client):
        """Test Moss knowledge query with results"""
        mock_result = Mock()
        mock_result.text = "Test knowledge"
        mock_moss_client.query_knowledge_base = AsyncMock(return_value=[mock_result])
        
        with patch('agents.workers.ChatOpenAI') as mock_chat_openai:
            mock_chat_openai.return_value = Mock()
            agent = BaseWorkerAgent(mock_moss_client)
            
            result = await agent._query_moss_knowledge("test query")
            
            assert "Test knowledge" in result
            mock_moss_client.query_knowledge_base.assert_called_once()

    @pytest.mark.asyncio
    async def test_query_moss_knowledge_no_results(self, mock_moss_client):
        """Test Moss knowledge query with no results"""
        mock_moss_client.query_knowledge_base = AsyncMock(return_value=[])
        
        with patch('agents.workers.ChatOpenAI') as mock_chat_openai:
            mock_chat_openai.return_value = Mock()
            agent = BaseWorkerAgent(mock_moss_client)
            
            result = await agent._query_moss_knowledge("test query")
            
            assert result == ""


class TestClaimsAgent:
    """Test cases for ClaimsAgent"""

    def test_process_claim_status_request(self, mock_moss_client):
        """Test processing claim status request"""
        with patch('agents.workers.ChatOpenAI') as mock_chat_openai:
            mock_chat_openai.return_value = Mock()
            agent = ClaimsAgent(mock_moss_client)
            
            response = agent.process("Check the status of claim CLM001", "session-123")
            
            assert "CLM001" in response
            assert "APPROVED" in response

    def test_process_check_status_request(self, mock_moss_client):
        """Test processing check status request"""
        with patch('agents.workers.ChatOpenAI') as mock_chat_openai:
            mock_chat_openai.return_value = Mock()
            agent = ClaimsAgent(mock_moss_client)
            
            response = agent.process("What's the status of check CHK001?", "session-123")
            
            assert "CHK001" in response
            assert "CLEARED" in response

    def test_process_claim_not_found(self, mock_moss_client):
        """Test processing claim with unknown ID"""
        with patch('agents.workers.ChatOpenAI') as mock_chat_openai:
            mock_chat_openai.return_value = Mock()
            mock_llm_response = Mock()
            mock_llm_response.content = "I don't have information about that claim"
            mock_chat_openai.return_value.invoke = Mock(return_value=mock_llm_response)
            agent = ClaimsAgent(mock_moss_client)
            
            response = agent.process("Check claim CLM999", "session-123")
            
            # When claim not found, it falls back to LLM response
            assert isinstance(response, str)

    def test_process_check_not_found(self, mock_moss_client):
        """Test processing check with unknown ID"""
        with patch('agents.workers.ChatOpenAI') as mock_chat_openai:
            mock_chat_openai.return_value = Mock()
            mock_llm_response = Mock()
            mock_llm_response.content = "I don't have information about that check"
            mock_chat_openai.return_value.invoke = Mock(return_value=mock_llm_response)
            agent = ClaimsAgent(mock_moss_client)
            
            response = agent.process("Check check CHK999", "session-123")
            
            # When check not found, it falls back to LLM response
            assert isinstance(response, str)

    def test_extract_claim_id(self, mock_moss_client):
        """Test claim ID extraction"""
        with patch('agents.workers.ChatOpenAI') as mock_chat_openai:
            mock_chat_openai.return_value = Mock()
            agent = ClaimsAgent(mock_moss_client)
            
            assert agent._extract_claim_id("Check claim CLM001") == "CLM001"
            assert agent._extract_claim_id("CLM002 status") == "CLM002"
            assert agent._extract_claim_id("No claim here") is None

    def test_extract_check_id(self, mock_moss_client):
        """Test check ID extraction"""
        with patch('agents.workers.ChatOpenAI') as mock_chat_openai:
            mock_chat_openai.return_value = Mock()
            agent = ClaimsAgent(mock_moss_client)
            
            assert agent._extract_check_id("Check CHK001") == "CHK001"
            assert agent._extract_check_id("CHK002 status") == "CHK002"
            assert agent._extract_check_id("No check here") is None


class TestKnowledgeAgent:
    """Test cases for KnowledgeAgent"""

    def test_process_with_knowledge(self, mock_moss_client):
        """Test processing with knowledge base results"""
        mock_result = Mock()
        mock_result.text = "Test policy information"
        mock_moss_client.query_knowledge_base = AsyncMock(return_value=[mock_result])
        
        with patch('agents.workers.ChatOpenAI') as mock_chat_openai:
            mock_llm_response = Mock()
            mock_llm_response.content = "Here is the answer based on knowledge"
            mock_chat_openai.return_value = Mock()
            mock_chat_openai.return_value.invoke = Mock(return_value=mock_llm_response)
            
            agent = KnowledgeAgent(mock_moss_client)
            response = agent.process("What is the claim policy?", "session-123")
            
            # Should return LLM response which contains knowledge
            assert isinstance(response, str)

    def test_process_without_knowledge(self, mock_moss_client):
        """Test processing without knowledge base results"""
        mock_moss_client.query_knowledge_base = AsyncMock(return_value=[])
        
        with patch('agents.workers.ChatOpenAI') as mock_chat_openai:
            mock_chat_openai.return_value = Mock()
            agent = KnowledgeAgent(mock_moss_client)
            response = agent.process("What is the claim policy?", "session-123")
            
            assert "escalate" in response.lower()


class TestEscalationAgent:
    """Test cases for EscalationAgent"""

    def test_process_escalation_request(self, mock_moss_client):
        """Test processing escalation request"""
        with patch('agents.workers.ChatOpenAI') as mock_chat_openai:
            mock_chat_openai.return_value = Mock()
            agent = EscalationAgent(mock_moss_client)
            
            response = agent.process("Create a ticket for billing issue", "session-123")
            
            assert "Ticket ID:" in response
            assert "Priority:" in response

    def test_extract_patient_id(self, mock_moss_client):
        """Test patient ID extraction"""
        with patch('agents.workers.ChatOpenAI') as mock_chat_openai:
            mock_chat_openai.return_value = Mock()
            agent = EscalationAgent(mock_moss_client)
            
            assert agent._extract_patient_id("Patient PAT001 has issue") == "PAT001"
            assert agent._extract_patient_id("PAT002 billing") == "PAT002"
            assert agent._extract_patient_id("No patient here") is None

    def test_extract_subject(self, mock_moss_client):
        """Test subject extraction"""
        with patch('agents.workers.ChatOpenAI') as mock_chat_openai:
            mock_chat_openai.return_value = Mock()
            agent = EscalationAgent(mock_moss_client)
            
            short_subject = agent._extract_subject("Short issue")
            assert short_subject == "Short issue"
            
            long_subject = agent._extract_subject("This is a very long subject that should be truncated to 100 characters for the ticket system")
            assert len(long_subject) <= 100

    def test_determine_priority_critical(self, mock_moss_client):
        """Test critical priority determination"""
        with patch('agents.workers.ChatOpenAI') as mock_chat_openai:
            mock_chat_openai.return_value = Mock()
            agent = EscalationAgent(mock_moss_client)
            
            assert agent._determine_priority("This is urgent emergency") == "critical"
            assert agent._determine_priority("Critical issue immediate") == "critical"

    def test_determine_priority_high(self, mock_moss_client):
        """Test high priority determination"""
        with patch('agents.workers.ChatOpenAI') as mock_chat_openai:
            mock_chat_openai.return_value = Mock()
            agent = EscalationAgent(mock_moss_client)
            
            assert agent._determine_priority("This is important asap") == "high"
            assert agent._determine_priority("Need this soon") == "high"

    def test_determine_priority_medium(self, mock_moss_client):
        """Test medium priority determination"""
        with patch('agents.workers.ChatOpenAI') as mock_chat_openai:
            mock_chat_openai.return_value = Mock()
            agent = EscalationAgent(mock_moss_client)
            
            assert agent._determine_priority("Regular issue") == "medium"
            assert agent._determine_priority("General question") == "medium"
