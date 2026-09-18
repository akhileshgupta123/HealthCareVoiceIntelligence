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
from urllib.parse import urlparse

# Load .env from backend directory
env_path = Path(__file__).parent.parent.parent / '.env'
# The Uvicorn reload parent can retain values loaded from a previous .env.
# For this local configuration file, prefer the current on-disk values.
load_dotenv(env_path, override=True)

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

    if api_key.startswith("your_") or api_secret.startswith("your_"):
        raise HTTPException(
            status_code=500,
            detail="LiveKit credentials are still using the placeholder values in backend/.env"
        )

    # A JWT is an access token, not an API secret. API secrets are used only
    # on the backend to sign the short-lived participant token returned here.
    if api_secret.count(".") == 2 and api_secret.startswith("eyJ"):
        raise HTTPException(
            status_code=500,
            detail="LIVEKIT_API_SECRET must be the Secret from LiveKit Cloud API Keys, not a JWT access token"
        )

    parsed_url = urlparse(livekit_url)
    if parsed_url.scheme not in {"ws", "wss"} or not parsed_url.netloc:
        raise HTTPException(
            status_code=500,
            detail="LIVEKIT_URL must be a valid ws:// or wss:// URL"
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
