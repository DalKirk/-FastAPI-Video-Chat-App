from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import List, Optional, Dict, Union

class Message(BaseModel):
    """Represents a single message in a conversation."""
    username: str
    content: str
    timestamp: Union[datetime, str]  # Accept both datetime and ISO string
    
    @field_validator('timestamp', mode='before')
    @classmethod
    def parse_timestamp(cls, v):
        """Convert ISO string to datetime if needed."""
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                # Fallback: use current time if parsing fails
                return datetime.now()
        return v


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
