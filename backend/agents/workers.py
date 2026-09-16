"""
Worker Agents
Specialized agents for Claims, Knowledge, and Escalation tasks
"""

from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
import httpx
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from api.logger import logger


class BaseWorkerAgent:
    """Base class for worker agents"""
    
    def __init__(self, moss_client):
        self.moss_client = moss_client
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.3,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
    
    async def _query_moss_knowledge(self, query: str, category: Optional[str] = None) -> str:
        """Query Moss knowledge base"""
        results = await self.moss_client.query_knowledge_base(
            query=query,
            category=category,
            top_k=3
        )
        
        if results:
            knowledge_text = "\n".join([r.text for r in results])
            return f"Relevant knowledge: {knowledge_text}"
        return ""
    
    async def _call_api(self, endpoint: str, method: str = "GET", data: Optional[dict] = None):
        """Call the backend API"""
        async with httpx.AsyncClient() as client:
            url = f"{self.api_base_url}{endpoint}"
            if method == "GET":
                response = await client.get(url)
            elif method == "POST":
                response = await client.post(url, json=data)
            elif method == "PUT":
                response = await client.put(url, json=data)
            
            return response.json()


class ClaimsAgent(BaseWorkerAgent):
    """Agent for handling claims and payment-related queries"""
    
    def process(self, user_message: str, session_id: str) -> str:
        """Process claims-related requests"""
        logger.info(f"ClaimsAgent processing: {user_message[:100]}...")
        # Simple pattern matching for demo
        user_message_lower = user_message.lower()
        
        if "claim" in user_message_lower and "status" in user_message_lower:
            # Extract claim ID (simplified)
            claim_id = self._extract_claim_id(user_message)
            if claim_id:
                logger.info(f"Retrieving claim status for {claim_id}")
                return self._get_claim_status(claim_id)
            else:
                return "I can help you check claim status. Please provide the claim ID (e.g., CLM001)."
        
        elif "check" in user_message_lower and "status" in user_message_lower:
            check_id = self._extract_check_id(user_message)
            if check_id:
                logger.info(f"Retrieving check status for {check_id}")
                return self._get_check_status(check_id)
            else:
                return "I can help you check payment status. Please provide the check ID (e.g., CHK001)."
        
        else:
            # Use LLM with knowledge base
            knowledge = self._query_moss_knowledge_sync(user_message, "claims")
            prompt = f"""
            User is asking about claims or payments: {user_message}
            {knowledge}
            
            Provide a helpful response about claims and payment processes.
            """
            response = self.llm.invoke(prompt)
            return response.content
    
    def _extract_claim_id(self, text: str) -> Optional[str]:
        """Extract claim ID from text"""
        import re
        match = re.search(r'CLM\d+', text.upper())
        return match.group(0) if match else None
    
    def _extract_check_id(self, text: str) -> Optional[str]:
        """Extract check ID from text"""
        import re
        match = re.search(r'CHK\d+', text.upper())
        return match.group(0) if match else None
    
    def _get_claim_status(self, claim_id: str) -> str:
        """Get claim status from API (simplified)"""
        # In real implementation, this would call the API
        mock_claims = {
            "CLM001": "Claim CLM001 for John Doe is APPROVED. Amount: $150.00. Processed on Jan 20, 2024.",
            "CLM002": "Claim CLM002 for Jane Smith is PENDING. Amount: $75.00. Submitted on Jan 18, 2024.",
            "CLM003": "Claim CLM003 for John Doe is UNDER REVIEW. Amount: $250.00. Requires additional documentation."
        }
        return mock_claims.get(claim_id, f"Claim {claim_id} not found. Please verify the claim ID.")
    
    def _get_check_status(self, check_id: str) -> str:
        """Get check status from API (simplified)"""
        mock_checks = {
            "CHK001": "Check CHK001 for John Doe is CLEARED. Amount: $150.00. Cleared on Jan 25, 2024.",
            "CHK002": "Check CHK002 for Robert Johnson is ISSUED. Amount: $500.00. Issued on Jan 25, 2024.",
            "CHK003": "Check CHK003 for Jane Smith is PENDING. Amount: $75.00. Awaiting claim approval."
        }
        return mock_checks.get(check_id, f"Check {check_id} not found. Please verify the check ID.")
    
    def _query_moss_knowledge_sync(self, query: str, category: Optional[str] = None) -> str:
        """Synchronous wrapper for Moss query"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self._query_moss_knowledge(query, category))
        except:
            return ""


class KnowledgeAgent(BaseWorkerAgent):
    """Agent for handling policy and procedural queries"""
    
    def process(self, user_message: str, session_id: str) -> str:
        """Process knowledge-related requests"""
        logger.info(f"KnowledgeAgent processing: {user_message[:100]}...")
        # Query Moss knowledge base
        knowledge = self._query_moss_knowledge_sync(user_message)
        
        if knowledge:
            prompt = f"""
            User is asking: {user_message}
            
            Relevant knowledge from our database:
            {knowledge}
            
            Provide a clear, helpful response based on this knowledge. If the knowledge doesn't fully answer the question, acknowledge this and suggest contacting support.
            """
            response = self.llm.invoke(prompt)
            return response.content
        else:
            return "I don't have specific information about that in our knowledge base. Would you like me to escalate this to our support team?"
    
    def _query_moss_knowledge_sync(self, query: str, category: Optional[str] = None) -> str:
        """Synchronous wrapper for Moss query"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self._query_moss_knowledge(query, category))
        except:
            return ""


class EscalationAgent(BaseWorkerAgent):
    """Agent for handling escalation and ticket creation"""
    
    def process(self, user_message: str, session_id: str) -> str:
        """Process escalation requests"""
        logger.info(f"EscalationAgent processing: {user_message[:100]}...")
        # Extract ticket information
        patient_id = self._extract_patient_id(user_message)
        subject = self._extract_subject(user_message)
        priority = self._determine_priority(user_message)
        
        # Create ticket (simplified)
        ticket_id = f"TKT{datetime.now().strftime('%Y%m%d%H%M%S')}"
        logger.info(f"Created ticket {ticket_id} with priority {priority}")
        
        response = f"""
        I've created an escalation ticket for you:
        
        Ticket ID: {ticket_id}
        Subject: {subject or 'General inquiry'}
        Priority: {priority}
        Patient ID: {patient_id or 'Not specified'}
        
        Our support team will review this ticket. For {priority} priority issues, you can expect a response within {'2 hours' if priority == 'critical' else '24 hours'}.
        
        Is there anything else I can help you with?
        """
        
        return response
    
    def _extract_patient_id(self, text: str) -> Optional[str]:
        """Extract patient ID from text"""
        import re
        match = re.search(r'PAT\d+', text.upper())
        return match.group(0) if match else None
    
    def _extract_subject(self, text: str) -> str:
        """Extract subject from user message"""
        # Simplified - in real implementation, use LLM to extract
        return text[:100] if len(text) > 100 else text
    
    def _determine_priority(self, text: str) -> str:
        """Determine priority based on keywords"""
        text_lower = text.lower()
        if any(keyword in text_lower for keyword in ['urgent', 'emergency', 'critical', 'immediate']):
            return "critical"
        elif any(keyword in text_lower for keyword in ['important', 'asap', 'soon']):
            return "high"
        else:
            return "medium"
