from pydantic import BaseModel
from datetime import datetime

class Message(BaseModel):
    """Represents a single message in a conversation."""
    username: str
    content: str
    timestamp: datetime
