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
        - {"prompt": "..."} or {"input"|"query"|"text": "..."}
        - OpenAI-style {"messages": [{"role":"user|assistant|system", "content":"..."}]}
        - history entries with {"role": "user"|"assistant", "content": "..."}
        """
        if values is None:
            return values
        if isinstance(values, str):
            return {"message": values}
        if isinstance(values, dict):
            # Map alternate message keys first
            if not values.get("message"):
                for k in ("prompt", "input", "query", "text"):
                    if isinstance(values.get(k), str) and values.get(k).strip():
                        values["message"] = values[k]
                        break

            # Handle OpenAI-style messages array
            msgs = values.get("messages")
            if isinstance(msgs, list):
                normalized_hist: List[Dict[str, Any]] = []
                last_user_content: Optional[str] = None
                for item in msgs:
                    if not isinstance(item, dict):
                        continue
                    role = str(item.get("role") or "").lower()
                    content = item.get("content")
                    if content is None:
                        continue
                    username = "User" if role == "user" else ("Assistant" if role == "assistant" else "System")
                    normalized_hist.append({
                        "username": username,
                        "content": content,
                        "timestamp": item.get("timestamp")
                    })
                    if role == "user":
                        last_user_content = content
                # Prefer explicit message; otherwise, use last user message, else last message
                if not values.get("message"):
                    if last_user_content:
                        values["message"] = last_user_content
                    elif normalized_hist:
                        values["message"] = normalized_hist[-1]["content"]
                # Merge/overwrite conversation_history with normalized from messages
                values["conversation_history"] = normalized_hist

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
                values["conversation_history"] = normalized
        return values

    @model_validator(mode="after")
    def ensure_message(self) -> "ChatRequest":
        if not self.message or not isinstance(self.message, str) or not self.message.strip():
            raise ValueError("'message' is required (or provide 'prompt'/'input'/'query'/'text' or OpenAI-style 'messages')")
        self.message = self.message.strip()
        return self


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    content: str
    format_type: str
    metadata: Dict
    success: bool = True
