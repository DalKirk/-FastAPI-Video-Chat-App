"""
Custom exception classes for better error handling
"""
from fastapi import HTTPException, status


class VideoStreamException(HTTPException):
    """Base exception for video streaming errors"""
    def __init__(self, detail: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        super().__init__(status_code=status_code, detail=detail)


class BunnyAPIException(VideoStreamException):
    """Exception for Bunny.net API errors"""
    def __init__(self, detail: str, status_code: int = None):
        super().__init__(
            detail=f"Bunny.net API error: {detail}",
            status_code=status_code or status.HTTP_503_SERVICE_UNAVAILABLE
        )


class RoomNotFoundException(HTTPException):
    """Exception when room is not found"""
    def __init__(self, room_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room not found: {room_id}"
        )


class UserNotFoundException(HTTPException):
    """Exception when user is not found"""
    def __init__(self, user_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found: {user_id}"
        )


class InvalidMessageException(HTTPException):
    """Exception for invalid message content"""
    def __init__(self, detail: str = "Invalid message format"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


class UploadException(HTTPException):
    """Exception for file upload errors"""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Upload error: {detail}"
        )


class RateLimitException(HTTPException):
    """Exception when rate limit is exceeded"""
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail
        )
