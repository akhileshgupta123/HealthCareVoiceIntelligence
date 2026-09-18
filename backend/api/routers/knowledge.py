"""
Knowledge Router
Query Moss-backed knowledge base for protocols and policies
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from api.moss_client import MossClient

router = APIRouter()


class KnowledgeQuery(BaseModel):
    query: str
    category: Optional[str] = None
    top_k: int = 5


class KnowledgeResponse(BaseModel):
    query: str
    results: List[dict]
    count: int


@router.post("/knowledge/search")
async def search_knowledge(
    request: KnowledgeQuery,
    moss_client: MossClient = Depends(lambda: None)  # Will be injected properly
):
    """Query the Moss-backed knowledge base for protocols and policies"""
    try:
        # Get moss client from app state (simplified for now)
        from api.main import moss_client
        if not moss_client:
            raise HTTPException(status_code=503, detail="Moss client not available")
        
        results = await moss_client.query_knowledge_base(
            query=request.query,
            category=request.category,
            top_k=request.top_k
        )
        
        # Convert results to dict format
        formatted_results = []
        for result in results:
            if isinstance(result, dict):
                formatted_results.append({
                    "id": result.get("id"),
                    "text": result.get("text", ""),
                    "score": result.get("score", 0),
                    "metadata": result.get("metadata", {}),
                })
            else:
                formatted_results.append({
                    "id": result.id,
                    "text": result.text,
                    "score": result.score,
                    "metadata": result.metadata,
                })
        
        return KnowledgeResponse(
            query=request.query,
            results=formatted_results,
            count=len(formatted_results)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying knowledge base: {str(e)}")
