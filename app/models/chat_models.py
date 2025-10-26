from pydantic import BaseModel, field_validator
from datetime import datetime, timezone
from typing import List, Optional, Dict, Union

class Message(BaseModel):
    """Represents a single message in a conversation."""
    username: str
    content: str
    timestamp: Optional[Union[datetime, str]] = None  # Allow missing or string

    @field_validator('timestamp', mode='before')
    @classmethod
    def parse_timestamp(cls, v):
        """Normalize timestamp: accept ISO string, datetime, or None."""
        if v is None:
            # Default to now in UTC if missing
            return datetime.now(timezone.utc)
        if isinstance(v, str):
            try:
                # Support trailing Z
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                return datetime.now(timezone.utc)
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
