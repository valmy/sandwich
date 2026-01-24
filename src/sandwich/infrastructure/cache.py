import json
import time
import hashlib
from typing import Any, Optional, TypeVar, Callable
from pathlib import Path

from sandwich.infrastructure.config import Settings
from sandwich.infrastructure.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class CacheManager:
    """Generic cache manager for API responses supporting both memory and file-based caching"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._memory_cache: dict[str, dict] = {}
        self._cache_dir = settings.cache_dir
        self._cache_dir.mkdir(exist_ok=True)

    def _get_cache_key(self, func: Callable, *args: Any, **kwargs: Any) -> str:
        """Generate unique cache key from function name and arguments"""
        key_parts = [func.__name__]
        for arg in args:
            key_parts.append(str(arg))
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")
        key_str = ":".join(key_parts)
        return hashlib.md5(key_str.encode("utf-8")).hexdigest()

    def _get_file_path(self, cache_key: str) -> Path:
        """Get file path for cache entry"""
        return self._cache_dir / f"{cache_key}.json"

    def get(self, func: Callable, *args: Any, **kwargs: Any) -> Optional[T]:
        """
        Get cached value for function call

        Args:
            func: Function to cache
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Cached value or None if cache miss or expired
        """
        if not self.settings.cache_enabled:
            logger.debug("Cache disabled, skipping get")
            return None

        cache_key = self._get_cache_key(func, *args, **kwargs)
        logger.debug(f"Cache key for {func.__name__}: {cache_key}")

        # Try memory cache first
        if cache_key in self._memory_cache:
            entry = self._memory_cache[cache_key]
            if time.time() - entry["timestamp"] < self.settings.cache_duration:
                logger.debug(f"Cache hit (memory) for {func.__name__}")
                return entry["value"]
            else:
                logger.debug(f"Memory cache expired for {func.__name__}")
                del self._memory_cache[cache_key]

        # Try file cache
        cache_file = self._get_file_path(cache_key)
        if cache_file.exists():
            try:
                with open(cache_file, "r") as f:
                    entry = json.load(f)
                if time.time() - entry["timestamp"] < self.settings.cache_duration:
                    logger.debug(f"Cache hit (file) for {func.__name__}")
                    # Update memory cache
                    self._memory_cache[cache_key] = entry
                    return entry["value"]
                else:
                    logger.debug(f"File cache expired for {func.__name__}")
                    cache_file.unlink(missing_ok=True)
            except (IOError, OSError, json.JSONDecodeError) as e:
                logger.warning(f"Failed to read cache file {cache_file}: {e}")
                cache_file.unlink(missing_ok=True)

        logger.debug(f"Cache miss for {func.__name__}")
        return None

    def set(self, func: Callable, value: T, *args: Any, **kwargs: Any) -> None:
        """
        Set cached value for function call

        Args:
            func: Function to cache
            value: Value to cache
            *args: Function arguments
            **kwargs: Function keyword arguments
        """
        if not self.settings.cache_enabled:
            logger.debug("Cache disabled, skipping set")
            return

        cache_key = self._get_cache_key(func, *args, **kwargs)
        logger.debug(f"Setting cache for {func.__name__}: {cache_key}")

        # Create cache entry
        entry = {
            "timestamp": time.time(),
            "value": value,
            "function": func.__name__,
        }

        # Update memory cache
        self._memory_cache[cache_key] = entry

        # Save to file cache
        cache_file = self._get_file_path(cache_key)
        try:
            with open(cache_file, "w") as f:
                json.dump(entry, f)
            logger.debug(f"Cache saved to file: {cache_file}")
        except (IOError, OSError) as e:
            logger.warning(f"Failed to write cache file {cache_file}: {e}")

    def invalidate(self, func: Callable, *args: Any, **kwargs: Any) -> None:
        """
        Invalidate cache entry for function call

        Args:
            func: Function to invalidate
            *args: Function arguments
            **kwargs: Function keyword arguments
        """
        cache_key = self._get_cache_key(func, *args, **kwargs)
        logger.debug(f"Invalidating cache for {func.__name__}: {cache_key}")

        # Remove from memory cache
        if cache_key in self._memory_cache:
            del self._memory_cache[cache_key]

        # Remove from file cache
        cache_file = self._get_file_path(cache_key)
        if cache_file.exists():
            try:
                cache_file.unlink()
                logger.debug(f"Cache file removed: {cache_file}")
            except (IOError, OSError) as e:
                logger.warning(f"Failed to remove cache file {cache_file}: {e}")

    def clear(self) -> None:
        """Clear all cache entries"""
        logger.info("Clearing all cache entries")
        self._memory_cache.clear()

        # Remove all cache files
        if self._cache_dir.exists():
            for cache_file in self._cache_dir.glob("*.json"):
                try:
                    cache_file.unlink()
                except (IOError, OSError) as e:
                    logger.warning(f"Failed to remove cache file {cache_file}: {e}")

    def is_cached(self, func: Callable, *args: Any, **kwargs: Any) -> bool:
        """
        Check if function call is cached and not expired

        Args:
            func: Function to check
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            True if cached and not expired, False otherwise
        """
        return self.get(func, *args, **kwargs) is not None


class cached:
    """Decorator for caching function results using CacheManager"""

    def __init__(self, cache_manager: Optional[CacheManager] = None):
        self.cache_manager = cache_manager

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Try to find cache_manager in args or kwargs
            if self.cache_manager is None:
                from sandwich.application.container import Container

                container = Container()
                self.cache_manager = container.cache_manager()

            # Try to get cached value
            cached_value = self.cache_manager.get(func, *args, **kwargs)
            if cached_value is not None:
                return cached_value

            # Call function and cache result
            result = func(*args, **kwargs)
            self.cache_manager.set(func, result, *args, **kwargs)
            return result

        return wrapper
