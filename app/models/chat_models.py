from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict

class Message(BaseModel):
    """Represents a single message in a conversation."""
    username: str
    content: str
    # Relax timestamp to accept strings from frontend and make it optional
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    # Use default_factory to avoid mutable default issues
    conversation_history: List[Message] = Field(default_factory=list)
    user_id: Optional[str] = None
    room_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    content: str
    format_type: str
    metadata: Dict
    success: bool = True
