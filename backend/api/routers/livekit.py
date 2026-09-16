"""
LiveKit Token Generation Router
Provides secure access tokens for LiveKit room connections
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import os
from livekit import api
from dotenv import load_dotenv
from pathlib import Path

# Load .env from backend directory
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

router = APIRouter()


class TokenRequest(BaseModel):
    room_name: str
    participant_name: Optional[str] = "user"


class TokenResponse(BaseModel):
    token: str
    url: str


@router.post("/token", response_model=TokenResponse)
async def create_livekit_token(request: TokenRequest):
    """
    Generate a LiveKit access token for room connection
    
    This endpoint creates a secure token that allows the frontend to connect
    to a LiveKit room. The token is generated using the server's API key and secret.
    """
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")
    livekit_url = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
    
    if not api_key or not api_secret:
        raise HTTPException(
            status_code=500,
            detail="LiveKit credentials not configured on server"
        )
    
    try:
        # Create token with room join permissions
        token = api.AccessToken(api_key, api_secret) \
            .with_identity(request.participant_name) \
            .with_name(request.participant_name) \
            .with_grants(api.VideoGrants(
                room_join=True,
                room=request.room_name,
                can_publish=True,
                can_subscribe=True
            ))
        
        jwt_token = token.to_jwt()
        
        return TokenResponse(
            token=jwt_token,
            url=livekit_url
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate LiveKit token: {str(e)}"
        )
