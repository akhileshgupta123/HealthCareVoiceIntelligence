"""
Moss Client Integration
Handles sub-10ms semantic search for context and knowledge retrieval
"""

import os
from typing import List, Dict, Any, Optional
import moss
from moss import MossClient, SessionIndex, SearchResult


class MossClientWrapper:
    """Moss client wrapper for sub-10ms semantic search"""
    
    def __init__(self, project_id: str, project_key: str):
        self.project_id = project_id
        self.project_key = project_key
        self.client: Optional[MossClient] = None
        self.session_index: Optional[SessionIndex] = None
        self.knowledge_index_name = "knowledge_base"
        
    async def initialize(self):
        """Initialize Moss client and load indexes"""
        try:
            # Initialize Moss SDK client
            self.client = MossClient(
                project_id=self.project_id,
                api_key=self.project_key
            )
            
            # Initialize session index
            self.session_index = SessionIndex(
                client=self.client,
                index_name="session_context"
            )
            
            # For knowledge base, we'll use the client's search functionality
            # In a real implementation, you would create a persistent index
            await self._index_sample_knowledge()
                
            print("Moss client initialized successfully")
            
        except Exception as e:
            print(f"Error initializing Moss client: {e}")
            # Don't raise - allow the app to run without Moss for POC
            self.client = None
    
    async def _index_sample_knowledge(self):
        """Index sample healthcare knowledge base"""
        # For POC, we'll store knowledge in memory
        # In production, this would use Moss's persistent indexing
        self._knowledge_store = [
            {
                "id": "kb_001",
                "text": "Claim submission requires patient ID, procedure code, and date of service. Claims are typically processed within 5-10 business days.",
                "metadata": {"category": "claims", "priority": "high"}
            },
            {
                "id": "kb_002", 
                "text": "Insurance eligibility can be checked using patient ID and insurance provider. Real-time verification is available for most major insurers.",
                "metadata": {"category": "eligibility", "priority": "high"}
            },
            {
                "id": "kb_003",
                "text": "Escalation tickets should include patient ID, issue description, urgency level, and relevant claim or check numbers. Critical issues are responded to within 2 hours.",
                "metadata": {"category": "escalation", "priority": "high"}
            },
            {
                "id": "kb_004",
                "text": "Check status can be verified using check number or patient ID. Payments are typically issued within 14 days of claim approval.",
                "metadata": {"category": "payments", "priority": "medium"}
            },
            {
                "id": "kb_005",
                "text": "HIPAA compliance requires all patient data to be encrypted in transit and at rest. Access is logged and audited regularly.",
                "metadata": {"category": "compliance", "priority": "high"}
            }
        ]
    
    async def query_session_context(
        self, 
        query: str, 
        session_id: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Query session context for relevant information"""
        if not self.client or not self.session_index:
            return []
        
        try:
            results = self.session_index.search(
                query=query,
                top_k=top_k
            )
            return [{"text": r.text, "score": r.score, "metadata": r.metadata} for r in results]
        except Exception as e:
            print(f"Error querying session context: {e}")
            return []
    
    async def query_knowledge_base(
        self, 
        query: str, 
        category: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Query knowledge base for relevant policies and procedures"""
        # For POC, do simple keyword matching
        # In production, this would use Moss's semantic search
        if not hasattr(self, '_knowledge_store'):
            return []
        
        query_lower = query.lower()
        results = []
        
        for doc in self._knowledge_store:
            if category and doc["metadata"].get("category") != category:
                continue
            
            # Simple keyword matching for POC
            if any(word in doc["text"].lower() for word in query_lower.split()):
                results.append({
                    "text": doc["text"],
                    "score": 0.8,  # Mock score
                    "metadata": doc["metadata"]
                })
        
        return results[:top_k]
    
    async def add_session_context(
        self,
        session_id: str,
        text: str,
        metadata: Dict[str, Any]
    ):
        """Add context to current session"""
        if not self.client or not self.session_index:
            return
        
        try:
            metadata["session_id"] = session_id
            self.session_index.add(
                text=text,
                metadata=metadata
            )
        except Exception as e:
            print(f"Error adding session context: {e}")
    
    async def clear_session(self, session_id: str):
        """Clear session context"""
        if not self.client or not self.session_index:
            return
        
        try:
            self.session_index.clear()
        except Exception as e:
            print(f"Error clearing session: {e}")
    
    async def close(self):
        """Close Moss client"""
        if self.client:
            try:
                self.client.close()
            except:
                pass
