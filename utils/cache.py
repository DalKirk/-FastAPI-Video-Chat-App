"""
Caching utilities for improved performance
"""
import time
from typing import Any, Optional, Callable
from functools import wraps
from collections import OrderedDict


class LRUCache:
    """
    Simple LRU (Least Recently Used) cache implementation.
    For production, use Redis or similar external cache.
    """
    
    def __init__(self, max_size: int = 1000, ttl: int = 300):
        """
        Args:
            max_size: Maximum number of items to store
            ttl: Time to live in seconds
        """
        self.cache: OrderedDict = OrderedDict()
        self.max_size = max_size
        self.ttl = ttl
        self.timestamps: dict = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self.cache:
            return None
        
        # Check if expired
        if time.time() - self.timestamps.get(key, 0) > self.ttl:
            self.delete(key)
            return None
        
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache"""
        if key in self.cache:
            # Update existing
            self.cache.move_to_end(key)
        else:
            # Add new
            if len(self.cache) >= self.max_size:
                # Remove least recently used
                oldest_key = next(iter(self.cache))
                self.delete(oldest_key)
        
        self.cache[key] = value
        self.timestamps[key] = time.time()
    
    def delete(self, key: str) -> None:
        """Delete value from cache"""
        if key in self.cache:
            del self.cache[key]
        if key in self.timestamps:
            del self.timestamps[key]
    
    def clear(self) -> None:
        """Clear all cache"""
        self.cache.clear()
        self.timestamps.clear()
    
    def size(self) -> int:
        """Get current cache size"""
        return len(self.cache)


def cached(ttl: int = 300):
    """
    Decorator for caching function results.
    
    Usage:
        @cached(ttl=60)
        def expensive_function(arg1, arg2):
            # ... expensive computation
            return result
    """
    cache = LRUCache(max_size=1000, ttl=ttl)
    
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Compute result
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result)
            
            return result
        
        # Add cache management methods
        wrapper.cache = cache
        wrapper.clear_cache = cache.clear
        
        return wrapper
    
    return decorator


# Global cache instances for common use cases
room_cache = LRUCache(max_size=500, ttl=300)
user_cache = LRUCache(max_size=1000, ttl=600)
message_cache = LRUCache(max_size=2000, ttl=180)
