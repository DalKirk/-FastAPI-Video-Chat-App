"""
Database abstraction layer - ready for migration from in-memory to persistent storage
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime


class DatabaseInterface(ABC):
    """Abstract interface for database operations"""
    
    @abstractmethod
    async def create_user(self, user_id: str, username: str, joined_at: datetime) -> dict:
        """Create a new user"""
        pass
    
    @abstractmethod
    async def get_user(self, user_id: str) -> Optional[dict]:
        """Get user by ID"""
        pass
    
    @abstractmethod
    async def get_all_users(self) -> List[dict]:
        """Get all users"""
        pass
    
    @abstractmethod
    async def create_room(self, room_id: str, name: str, created_at: datetime) -> dict:
        """Create a new room"""
        pass
    
    @abstractmethod
    async def get_room(self, room_id: str) -> Optional[dict]:
        """Get room by ID"""
        pass
    
    @abstractmethod
    async def get_all_rooms(self) -> List[dict]:
        """Get all rooms"""
        pass
    
    @abstractmethod
    async def add_message(self, room_id: str, message: dict) -> None:
        """Add message to room"""
        pass
    
    @abstractmethod
    async def get_messages(self, room_id: str, limit: int = 50) -> List[dict]:
        """Get messages from room"""
        pass


class InMemoryDatabase(DatabaseInterface):
    """In-memory database implementation (current)"""
    
    def __init__(self):
        self.users: Dict[str, dict] = {}
        self.rooms: Dict[str, dict] = {}
        self.messages: Dict[str, List[dict]] = {}
    
    async def create_user(self, user_id: str, username: str, joined_at: datetime) -> dict:
        user = {
            "id": user_id,
            "username": username,
            "joined_at": joined_at.isoformat()
        }
        self.users[user_id] = user
        return user
    
    async def get_user(self, user_id: str) -> Optional[dict]:
        return self.users.get(user_id)
    
    async def get_all_users(self) -> List[dict]:
        return list(self.users.values())
    
    async def create_room(self, room_id: str, name: str, created_at: datetime) -> dict:
        room = {
            "id": room_id,
            "name": name,
            "created_at": created_at.isoformat(),
            "users": []
        }
        self.rooms[room_id] = room
        self.messages[room_id] = []
        return room
    
    async def get_room(self, room_id: str) -> Optional[dict]:
        return self.rooms.get(room_id)
    
    async def get_all_rooms(self) -> List[dict]:
        return list(self.rooms.values())
    
    async def add_message(self, room_id: str, message: dict) -> None:
        if room_id not in self.messages:
            self.messages[room_id] = []
        self.messages[room_id].append(message)
    
    async def get_messages(self, room_id: str, limit: int = 50) -> List[dict]:
        messages = self.messages.get(room_id, [])
        return messages[-limit:]


# Future implementations can be added here:
# class PostgreSQLDatabase(DatabaseInterface): ...
# class MongoDBDatabase(DatabaseInterface): ...
# class RedisDatabase(DatabaseInterface): ...


# Factory function for easy database switching
def get_database(db_type: str = "memory") -> DatabaseInterface:
    """
    Get database instance based on type.
    
    Args:
        db_type: Type of database ("memory", "postgres", "mongodb", "redis")
    
    Returns:
        Database instance
    """
    if db_type == "memory":
        return InMemoryDatabase()
    # Add more database types as needed
    # elif db_type == "postgres":
    #     return PostgreSQLDatabase()
    else:
        raise ValueError(f"Unsupported database type: {db_type}")
