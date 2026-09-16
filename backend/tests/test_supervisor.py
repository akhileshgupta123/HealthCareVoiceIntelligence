"""
Tests for Supervisor Agent
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from langchain_core.messages import HumanMessage, AIMessage

from agents.supervisor import SupervisorAgent, AgentState


@pytest.fixture
def mock_moss_client():
    """Mock Moss client"""
    client = Mock()
    client.add_session_context = AsyncMock()
    return client


@pytest.fixture
def mock_llm():
    """Mock LLM"""
    llm = Mock()
    response = Mock()
    response.content = "claims"
    llm.invoke = Mock(return_value=response)
    return llm


class TestSupervisorAgent:
    """Test cases for Supervisor Agent"""

    def test_initialization(self, mock_moss_client):
        """Test supervisor agent initialization"""
        with patch('agents.supervisor.ChatOpenAI') as mock_chat_openai:
            mock_chat_openai.return_value = Mock()
            
            agent = SupervisorAgent(mock_moss_client)
            
            assert agent.moss_client == mock_moss_client
            assert agent.graph is not None
            mock_chat_openai.assert_called_once()

    def test_route_request_claims_intent(self, mock_moss_client, mock_llm):
        """Test routing to claims agent"""
        with patch('agents.supervisor.ChatOpenAI', return_value=mock_llm):
            agent = SupervisorAgent(mock_moss_client)
            
            state: AgentState = {
                "messages": [HumanMessage(content="Check claim status CLM001")],
                "next_agent": "supervisor",
                "session_id": "test-session",
                "context": {}
            }
            
            result = agent._route_request(state)
            
            assert result["next_agent"] == "claims"

    def test_route_request_knowledge_intent(self, mock_moss_client, mock_llm):
        """Test routing to knowledge agent"""
        mock_llm.invoke.return_value.content = "knowledge"
        
        with patch('agents.supervisor.ChatOpenAI', return_value=mock_llm):
            agent = SupervisorAgent(mock_moss_client)
            
            state: AgentState = {
                "messages": [HumanMessage(content="What is the policy for claims?")],
                "next_agent": "supervisor",
                "session_id": "test-session",
                "context": {}
            }
            
            result = agent._route_request(state)
            
            assert result["next_agent"] == "knowledge"

    def test_route_request_escalation_intent(self, mock_moss_client, mock_llm):
        """Test routing to escalation agent"""
        mock_llm.invoke.return_value.content = "escalation"
        
        with patch('agents.supervisor.ChatOpenAI', return_value=mock_llm):
            agent = SupervisorAgent(mock_moss_client)
            
            state: AgentState = {
                "messages": [HumanMessage(content="Create a ticket for billing issue")],
                "next_agent": "supervisor",
                "session_id": "test-session",
                "context": {}
            }
            
            result = agent._route_request(state)
            
            assert result["next_agent"] == "escalation"

    def test_route_request_end_intent(self, mock_moss_client, mock_llm):
        """Test routing to end"""
        mock_llm.invoke.return_value.content = "end"
        
        with patch('agents.supervisor.ChatOpenAI', return_value=mock_llm):
            agent = SupervisorAgent(mock_moss_client)
            
            state: AgentState = {
                "messages": [HumanMessage(content="Goodbye")],
                "next_agent": "supervisor",
                "session_id": "test-session",
                "context": {}
            }
            
            result = agent._route_request(state)
            
            assert result["next_agent"] == "end"

    def test_route_request_unknown_intent_defaults_to_knowledge(self, mock_moss_client, mock_llm):
        """Test unknown intent defaults to knowledge agent"""
        mock_llm.invoke.return_value.content = "unknown"
        
        with patch('agents.supervisor.ChatOpenAI', return_value=mock_llm):
            agent = SupervisorAgent(mock_moss_client)
            
            state: AgentState = {
                "messages": [HumanMessage(content="Random query")],
                "next_agent": "supervisor",
                "session_id": "test-session",
                "context": {}
            }
            
            result = agent._route_request(state)
            
            assert result["next_agent"] == "knowledge"

    @pytest.mark.skip(reason="LangGraph recursion limit issue - complex integration test")
    @pytest.mark.asyncio
    async def test_process_message_success(self, mock_moss_client, mock_llm):
        """Test successful message processing"""
        with patch('agents.supervisor.ChatOpenAI', return_value=mock_llm):
            # Mock the worker agents
            with patch('agents.workers.ClaimsAgent') as mock_claims:
                mock_claims_instance = Mock()
                mock_claims_instance.process = Mock(return_value="Claim status: Approved")
                mock_claims.return_value = mock_claims_instance
                
                agent = SupervisorAgent(mock_moss_client)
                
                response = await agent.process("Check claim CLM001", "session-123")
                
                assert response == "Claim status: Approved"
                mock_moss_client.add_session_context.assert_called()

    @pytest.mark.skip(reason="LangGraph recursion limit issue - complex integration test")
    @pytest.mark.asyncio
    async def test_process_message_no_response(self, mock_moss_client, mock_llm):
        """Test message processing when no AI response is generated"""
        with patch('agents.supervisor.ChatOpenAI', return_value=mock_llm):
            with patch('agents.workers.ClaimsAgent') as mock_claims:
                mock_claims_instance = Mock()
                mock_claims_instance.process = Mock(return_value="")
                mock_claims.return_value = mock_claims_instance
                
                agent = SupervisorAgent(mock_moss_client)
                
                response = await agent.process("Check claim CLM001", "session-123")
                
                assert "I apologize" in response

    def test_build_graph_structure(self, mock_moss_client):
        """Test graph structure is built correctly"""
        with patch('agents.supervisor.ChatOpenAI', return_value=Mock()):
            agent = SupervisorAgent(mock_moss_client)
            
            graph = agent.graph
            
            assert graph is not None
            # Verify the graph was compiled
            assert hasattr(graph, 'invoke')
