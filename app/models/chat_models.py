from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from typing import List, Optional, Dict, Any

class Message(BaseModel):
    """Represents a single message in a conversation."""
    username: str
    content: str
    # Accept strings or omit entirely
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: Optional[str] = None
    conversation_history: List[Message] = Field(default_factory=list)
    user_id: Optional[str] = None
    room_id: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def coerce_payload(cls, values: Any) -> Any:
        """
        Allow legacy and alternate shapes:
        - {"prompt": "..."} or {"input"|"query"|"text": "...}
        - history entries with {"role": "user"|"assistant", "content": "...}
        """
        if values is None:
            return values
        if isinstance(values, str):
            return {"message": values}
        if isinstance(values, dict):
            # Map alternate message keys
            if not values.get("message"):
                for k in ("prompt", "input", "query", "text"):
                    if isinstance(values.get(k), str):
                        values["message"] = values[k]
                        break
            # Normalize conversation_history if provided with role/content
            hist = values.get("conversation_history")
            if isinstance(hist, list):
                normalized: List[Dict[str, Any]] = []
                for item in hist:
                    if isinstance(item, dict):
                        username = item.get("username")
                        if not username and "role" in item:
                            role = str(item.get("role") or "").lower()
                            username = "User" if role == "user" else "Assistant"
                        normalized.append({
                            "username": username or "User",
                            "content": item.get("content", ""),
                            "timestamp": item.get("timestamp")
                        })
                    else:
                        continue
                values["conversation_history"] = normalized
        return values

    @model_validator(mode="after")
    def ensure_message(self) -> "ChatRequest":
        if not self.message or not isinstance(self.message, str) or not self.message.strip():
            raise ValueError("'message' is required (or provide 'prompt'/'input'/'query'/'text')")
        self.message = self.message.strip()
        return self


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    content: str
    format_type: str
    metadata: Dict
    success: bool = True
