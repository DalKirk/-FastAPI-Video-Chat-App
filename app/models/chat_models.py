from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict

class Message(BaseModel):
    """Represents a single message in a conversation."""
    username: str
    content: str
    timestamp: datetime


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    conversation_history: List[Message] = []
    user_id: Optional[str] = None
    room_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    content: str
    format_type: str
    metadata: Dict
    success: bool = True
