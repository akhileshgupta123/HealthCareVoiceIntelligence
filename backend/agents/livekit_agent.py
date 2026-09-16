"""
LiveKit Agent Integration
Connects the agent layer with LiveKit for real-time voice processing
"""

from livekit import rtc
from livekit.agents import Agent, AgentSession
from typing import Optional
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from agents.supervisor import SupervisorAgent
from api.moss_client import MossClient
from api.logger import logger


class HealthcareVoiceAgent(Agent):
    """Healthcare Operations Assistant - LiveKit Voice Agent"""
    
    def __init__(self):
        super().__init__()
        self.moss_client: Optional[MossClient] = None
        self.supervisor_agent: Optional[SupervisorAgent] = None
        self.session_id: Optional[str] = None
    
    async def on_start(self, session: AgentSession):
        """Initialize agent when session starts"""
        self.session_id = session.room.name or f"session_{session.sid}"
        
        # Initialize Moss client
        self.moss_client = MossClient(
            project_id=os.getenv("MOSS_PROJECT_ID"),
            project_key=os.getenv("MOSS_PROJECT_KEY")
        )
        await self.moss_client.initialize()
        
        # Initialize supervisor agent
        self.supervisor_agent = SupervisorAgent(self.moss_client)
        
        logger.info(f"Healthcare Voice Agent started for session: {self.session_id}")
    
    async def on_stop(self):
        """Cleanup when session ends"""
        if self.moss_client:
            await self.moss_client.close()
        logger.info("Healthcare Voice Agent stopped")
    
    async def on_transcript(self, transcript: rtc.TranscriptionEvent):
        """Handle incoming speech transcription"""
        user_text = transcript.text
        logger.info(f"User said: {user_text}")
        
        # Process through supervisor agent
        try:
            response = await self.supervisor_agent.process(user_text, self.session_id)
            logger.info(f"Agent response: {response}")
            
            # Convert response to speech
            await self.session.say(response)
            
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            await self.session.say("I apologize, but I encountered an error. Please try again.")
    
    async def on_message(self, message: rtc.DataMessage):
        """Handle incoming data messages"""
        # Can be used for non-voice interactions
        pass


async def create_agent() -> HealthcareVoiceAgent:
    """Factory function to create the healthcare voice agent"""
    return HealthcareVoiceAgent()


# Entry point for LiveKit
if __name__ == "__main__":
    import asyncio
    from livekit import api
    
    async def main():
        # This would be used with LiveKit's agent framework
        # For now, it's a placeholder for the actual deployment
        logger.info("Healthcare Voice Agent - LiveKit Integration")
        logger.info("To deploy, use the LiveKit Agent CLI or integrate with your LiveKit server")
    
    asyncio.run(main())
