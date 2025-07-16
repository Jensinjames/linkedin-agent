"""Performance optimization utilities."""

import asyncio
from typing import Any, Optional, Callable, Hashable
from functools import wraps
import hashlib
import json
import time
from collections import OrderedDict


class TTLCache:
    """Thread-safe TTL (Time To Live) cache implementation."""
    
    def __init__(self, max_size: int = 128, ttl_seconds: int = 300):
        """
        Initialize TTL cache.
        
        Args:
            max_size: Maximum number of items to cache
            ttl_seconds: Time to live for cached items
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: OrderedDict = OrderedDict()
        self._lock = asyncio.Lock()
    
    async def get(self, key: Hashable) -> Optional[Any]:
        """Get item from cache if not expired."""
        async with self._lock:
            if key in self.cache:
                item, timestamp = self.cache[key]
                if time.time() - timestamp < self.ttl_seconds:
                    # Move to end (most recently used)
                    self.cache.move_to_end(key)
                    return item
                else:
                    # Expired, remove it
                    del self.cache[key]
            return None
    
    async def set(self, key: Hashable, value: Any) -> None:
        """Set item in cache."""
        async with self._lock:
            # Remove oldest items if cache is full
            while len(self.cache) >= self.max_size:
                self.cache.popitem(last=False)
            
            self.cache[key] = (value, time.time())
    
    async def clear(self) -> None:
        """Clear all cached items."""
        async with self._lock:
            self.cache.clear()


class ConnectionPool:
    """Simple connection pool for HTTP clients."""
    
    def __init__(self, max_connections: int = 10):
        """
        Initialize connection pool.
        
        Args:
            max_connections: Maximum number of concurrent connections
        """
        self.max_connections = max_connections
        self.semaphore = asyncio.Semaphore(max_connections)
        self.active_connections = 0
    
    async def acquire(self):
        """Acquire a connection from the pool."""
        await self.semaphore.acquire()
        self.active_connections += 1
    
    def release(self):
        """Release a connection back to the pool."""
        if self.active_connections > 0:
            self.active_connections -= 1
            self.semaphore.release()
    
    async def __aenter__(self):
        await self.acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.release()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


def cache_async_result(ttl_seconds: int = 300, max_size: int = 128):
    """
    Decorator to cache async function results with TTL.
    
    Args:
        ttl_seconds: Time to live for cached results
        max_size: Maximum number of cached results
    """
    cache = TTLCache(max_size=max_size, ttl_seconds=ttl_seconds)
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key_data = {
                'func': func.__name__,
                'args': args,
                'kwargs': kwargs
            }
            
            # Handle non-serializable arguments by converting to string
            try:
                key_str = json.dumps(key_data, sort_keys=True, default=str)
            except (TypeError, ValueError):
                # Fallback to string representation
                key_str = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Use hash of the key string for cache key
            cache_key = hashlib.md5(key_str.encode()).hexdigest()
            
            # Try to get from cache
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result)
            return result
        
        # Add cache management methods
        wrapper.cache_clear = cache.clear
        wrapper.cache = cache
        return wrapper
    
    return decorator


def batch_process(batch_size: int = 10, delay_seconds: float = 0.1):
    """
    Decorator to batch process multiple calls to a function.
    
    Args:
        batch_size: Number of items to process in each batch
        delay_seconds: Delay between batches to avoid rate limiting
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(items: list, *args, **kwargs):
            results = []
            
            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]
                batch_results = await func(batch, *args, **kwargs)
                results.extend(batch_results)
                
                # Add delay between batches if not the last batch
                if i + batch_size < len(items):
                    await asyncio.sleep(delay_seconds)
            
            return results
        
        return wrapper
    
    return decorator


# Global instances
default_cache = TTLCache(max_size=256, ttl_seconds=600)
connection_pool = ConnectionPool(max_connections=10)
