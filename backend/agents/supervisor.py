"""
Supervisor Agent
Orchestrates and routes requests to specialized worker agents using LangGraph
"""

from typing import TypedDict, Annotated, Literal, Sequence
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()


class AgentState(TypedDict):
    """State for the supervisor agent workflow"""
    messages: Annotated[Sequence[BaseMessage], "messages"]
    next_agent: Literal["claims", "knowledge", "escalation", "end"]
    session_id: str
    context: dict


class SupervisorAgent:
    """Supervisor agent for routing requests to specialized workers"""
    
    def __init__(self, moss_client):
        self.moss_client = moss_client
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("supervisor", self._route_request)
        workflow.add_node("claims_agent", self._claims_agent)
        workflow.add_node("knowledge_agent", self._knowledge_agent)
        workflow.add_node("escalation_agent", self._escalation_agent)
        
        # Set entry point
        workflow.set_entry_point("supervisor")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "supervisor",
            lambda state: state["next_agent"],
            {
                "claims": "claims_agent",
                "knowledge": "knowledge_agent",
                "escalation": "escalation_agent",
                "end": END
            }
        )
        
        # All agents return to supervisor
        workflow.add_edge("claims_agent", "supervisor")
        workflow.add_edge("knowledge_agent", "supervisor")
        workflow.add_edge("escalation_agent", "supervisor")
        
        return workflow.compile()
    
    def _route_request(self, state: AgentState) -> AgentState:
        """Route the request to the appropriate agent based on intent"""
        messages = state["messages"]
        last_message = messages[-1].content if messages else ""
        
        # Use LLM to classify intent
        intent_prompt = f"""
        Classify the following user request into one of these categories:
        - claims: Questions about claim status, claim submission, payment status
        - knowledge: Questions about policies, procedures, protocols, guidelines
        - escalation: Requests to create tickets, escalate issues, report problems
        - end: Greeting, goodbye, or unclear intent that should end conversation
        
        User request: {last_message}
        
        Respond with only the category name (claims, knowledge, escalation, or end).
        """
        
        response = self.llm.invoke(intent_prompt)
        intent = response.content.strip().lower()
        
        # Map intent to agent
        intent_mapping = {
            "claims": "claims",
            "knowledge": "knowledge",
            "escalation": "escalation",
            "end": "end"
        }
        
        state["next_agent"] = intent_mapping.get(intent, "knowledge")
        return state
    
    def _claims_agent(self, state: AgentState) -> AgentState:
        """Handle claims-related requests"""
        from agents.workers import ClaimsAgent
        
        claims_agent = ClaimsAgent(self.moss_client)
        response = claims_agent.process(state["messages"][-1].content, state["session_id"])
        
        state["messages"].append(AIMessage(content=response))
        state["next_agent"] = "end"
        return state
    
    def _knowledge_agent(self, state: AgentState) -> AgentState:
        """Handle knowledge-related requests"""
        from agents.workers import KnowledgeAgent
        
        knowledge_agent = KnowledgeAgent(self.moss_client)
        response = knowledge_agent.process(state["messages"][-1].content, state["session_id"])
        
        state["messages"].append(AIMessage(content=response))
        state["next_agent"] = "end"
        return state
    
    def _escalation_agent(self, state: AgentState) -> AgentState:
        """Handle escalation requests"""
        from agents.workers import EscalationAgent
        
        escalation_agent = EscalationAgent(self.moss_client)
        response = escalation_agent.process(state["messages"][-1].content, state["session_id"])
        
        state["messages"].append(AIMessage(content=response))
        state["next_agent"] = "end"
        return state
    
    async def process(self, user_message: str, session_id: str) -> str:
        """Process a user message through the supervisor workflow"""
        initial_state: AgentState = {
            "messages": [HumanMessage(content=user_message)],
            "next_agent": "supervisor",
            "session_id": session_id,
            "context": {}
        }
        
        # Store context in Moss
        await self.moss_client.add_session_context(
            session_id=session_id,
            text=user_message,
            metadata={"type": "user_input", "timestamp": str(datetime.now())}
        )
        
        # Run the workflow
        final_state = self.graph.invoke(initial_state)
        
        # Get the last AI response
        ai_messages = [msg for msg in final_state["messages"] if isinstance(msg, AIMessage)]
        if ai_messages:
            response = ai_messages[-1].content
            
            # Store response in Moss
            await self.moss_client.add_session_context(
                session_id=session_id,
                text=response,
                metadata={"type": "agent_response", "timestamp": str(datetime.now())}
            )
            
            return response
        
        return "I apologize, but I couldn't process your request. Please try again."
