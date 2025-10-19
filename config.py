"""
Configuration management for FastAPI Video Chat Application
"""
import os
from typing import Set
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with validation and type safety"""
    
    # Application
    app_name: str = "FastAPI Video Chat"
    app_version: str = "2.0.0"
    environment: str = "development"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Bunny.net Stream Configuration
    bunny_api_key: str = ""
    bunny_library_id: str = ""
    bunny_pull_zone: str = ""
    bunny_collection_id: str = ""
    
    # CORS Configuration
    allowed_origins: list[str] = [
        "http://localhost:3000",
        "https://localhost:3000",
        "https://next-js-14-front-end-for-chat-plast.vercel.app",
        "https://video-chat-frontend-ruby.vercel.app",
    ]
    
    # WebSocket
    websocket_ping_interval: int = 20
    websocket_ping_timeout: int = 10
    
    # Message limits
    max_message_length: int = 5000
    max_username_length: int = 50
    max_room_name_length: int = 100
    message_history_limit: int = 100
    
    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # seconds
    
    # File upload
    max_upload_size_mb: int = 500
    allowed_video_extensions: Set[str] = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def bunny_enabled(self) -> bool:
        """Check if Bunny.net Stream is properly configured"""
        return bool(
            self.bunny_api_key and 
            self.bunny_library_id and 
            self.bunny_pull_zone
        )
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() == "production"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
