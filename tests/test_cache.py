import tempfile
import time
from pathlib import Path
import pytest
from unittest.mock import Mock

from sandwich.infrastructure.cache import CacheManager
from sandwich.infrastructure.config import Settings


class TestCacheManager:
    """Tests for CacheManager functionality"""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def settings(self, temp_dir):
        """Create settings with temporary cache directory"""
        return Settings(
            cache_enabled=True,
            cache_duration=60,
            cache_dir=temp_dir / ".cache"
        )

    @pytest.fixture
    def cache_manager(self, settings):
        """Create a CacheManager instance"""
        return CacheManager(settings)

    def test_cache_initialization(self, cache_manager, settings):
        """Test that cache manager initializes correctly"""
        assert isinstance(cache_manager, CacheManager)
        assert cache_manager._cache_dir == settings.cache_dir
        assert cache_manager._cache_dir.exists()

    def test_cache_set_and_get(self, cache_manager):
        """Test setting and getting a cache value"""
        # Define a simple test function
        def test_func(x, y):
            return x + y

        # Set cache
        cache_manager.set(test_func, 5, 2, 3)

        # Get cache
        result = cache_manager.get(test_func, 2, 3)
        assert result == 5

    def test_cache_miss(self, cache_manager):
        """Test that cache miss returns None"""
        def test_func(x, y):
            return x + y

        result = cache_manager.get(test_func, 2, 3)
        assert result is None

    def test_cache_with_different_args(self, cache_manager):
        """Test that different arguments produce different cache keys"""
        def test_func(x, y):
            return x + y

        cache_manager.set(test_func, 5, 2, 3)
        cache_manager.set(test_func, 10, 4, 6)

        assert cache_manager.get(test_func, 2, 3) == 5
        assert cache_manager.get(test_func, 4, 6) == 10

    def test_cache_expiration(self, settings, temp_dir):
        """Test that cache entries expire after configured duration"""
        # Create a cache manager with very short duration
        settings.cache_duration = 1
        cache_manager = CacheManager(settings)

        def test_func(x, y):
            return x + y

        cache_manager.set(test_func, 5, 2, 3)
        assert cache_manager.get(test_func, 2, 3) == 5

        # Wait for cache to expire
        time.sleep(1.1)
        assert cache_manager.get(test_func, 2, 3) is None

    def test_cache_disabled(self, settings, temp_dir):
        """Test that cache operations are skipped when disabled"""
        settings.cache_enabled = False
        cache_manager = CacheManager(settings)

        def test_func(x, y):
            return x + y

        cache_manager.set(test_func, 5, 2, 3)
        assert cache_manager.get(test_func, 2, 3) is None

    def test_cache_clear(self, cache_manager):
        """Test clearing all cache entries"""
        def test_func(x, y):
            return x + y

        cache_manager.set(test_func, 5, 2, 3)
        assert cache_manager.get(test_func, 2, 3) == 5

        cache_manager.clear()
        assert cache_manager.get(test_func, 2, 3) is None

    def test_cache_invalidation(self, cache_manager):
        """Test invalidating a specific cache entry"""
        def test_func(x, y):
            return x + y

        cache_manager.set(test_func, 5, 2, 3)
        assert cache_manager.get(test_func, 2, 3) == 5

        cache_manager.invalidate(test_func, 2, 3)
        assert cache_manager.get(test_func, 2, 3) is None

    def test_is_cached(self, cache_manager):
        """Test checking if an entry is cached"""
        def test_func(x, y):
            return x + y

        assert not cache_manager.is_cached(test_func, 2, 3)
        cache_manager.set(test_func, 5, 2, 3)
        assert cache_manager.is_cached(test_func, 2, 3)

    def test_file_based_cache(self, cache_manager):
        """Test that cache is properly persisted to file"""
        def test_func(x, y):
            return x + y

        cache_manager.set(test_func, 5, 2, 3)

        # Create a new cache manager instance to verify file-based cache
        new_cache_manager = CacheManager(cache_manager.settings)
        result = new_cache_manager.get(test_func, 2, 3)
        assert result == 5
