"""Performance tests for the Sandwich application"""

import time
import pytest
from unittest.mock import MagicMock
from sandwich.domain.services import MarketDataSorter, PairMatcher
from sandwich.domain.models import TradingPair, ExchangeId, MarketType
from sandwich.infrastructure.config import Settings
from pathlib import Path


@pytest.fixture
def mock_settings():
    """Create a mock settings object"""
    settings = MagicMock(spec=Settings)
    settings.data_dir = Path("/tmp")
    settings.get_stablecoins_filename.return_value = "stablecoins.txt"
    settings.get_pairs_filename.return_value = "pairs.txt"
    settings.get_sorted_filename.return_value = "sorted_pairs.txt"
    settings.EXCLUDED_CURRENCIES = ["USDT", "USDC"]
    settings.QUOTE_CURRENCIES = ["USDT", "USDC", "FDUSD"]
    settings.marketcap_file = "marketcap.json"
    return settings


@pytest.fixture
def mock_coingecko_client():
    """Create a mock CoinGecko client"""
    client = MagicMock()
    client.fetch_stablecoins.return_value = {"USDT", "USDC", "FDUSD"}
    return client


@pytest.fixture
def mock_market_repository():
    """Create a mock market repository"""
    repo = MagicMock()
    repo.load_market_data.return_value = [
        MagicMock(
            model_dump=MagicMock(return_value={
                "symbol": f"BTC{i}",
                "total_volume": i * 1000
            })
        ) for i in range(1000)
    ]
    return repo


@pytest.fixture
def mock_pair_repository():
    """Create a mock pair repository"""
    repo = MagicMock()
    pairs = [f"BINANCE:BTC{i}USDT.P" for i in range(1000)]
    repo.load_pair_lines.return_value = pairs
    return repo


def test_market_data_sorter_performance(
    mock_settings, mock_coingecko_client, mock_market_repository, mock_pair_repository
):
    """Test performance of MarketDataSorter.sort_pairs_by_volume"""
    sorter = MarketDataSorter(
        mock_settings,
        mock_coingecko_client,
        mock_market_repository,
        mock_pair_repository
    )
    
    # Measure execution time
    start_time = time.time()
    sorted_data, sorted_count, unsorted_count = sorter.sort_pairs_by_volume(
        "USDT", "swap"
    )
    end_time = time.time()
    
    # Verify results
    assert sorted_count > 0
    assert sorted_count + unsorted_count == 1000
    
    # Performance requirement: should handle 1000 pairs in under 0.5 seconds
    execution_time = end_time - start_time
    assert execution_time < 0.5, f"Execution time ({execution_time:.2f}s) exceeds 0.5 seconds"
    
    print(f"\nMarketDataSorter performance test passed in {execution_time:.2f} seconds")
    print(f"Sorted pairs: {sorted_count}, Unsorted pairs: {unsorted_count}")


def test_pair_matcher_performance(mock_settings):
    """Test performance of PairMatcher.match_pairs"""
    matcher = PairMatcher(mock_settings)
    
    # Create large datasets
    source_pairs = [
        TradingPair(
            symbol=f"BTC{i}/USDT",
            base=f"BTC{i}",
            quote="USDT",
            exchange=ExchangeId.BINANCE,
            market_type=MarketType.SWAP,
            is_active=True
        ) for i in range(2000)
    ]
    
    target_pairs = [
        TradingPair(
            symbol=f"BTC{i}/USDC",
            base=f"BTC{i}",
            quote="USDC",
            exchange=ExchangeId.HYPERLIQUID,
            market_type=MarketType.SWAP,
            is_active=True
        ) for i in range(1500)
    ]
    
    # Measure execution time
    start_time = time.time()
    result = matcher.match_pairs(source_pairs, target_pairs)
    end_time = time.time()
    
    # Verify results
    assert len(result.matched_pairs) == 1500
    assert len(result.missing_pairs) == 500
    
    # Performance requirement: should handle 2000 pairs in under 0.1 seconds
    execution_time = end_time - start_time
    assert execution_time < 0.1, f"Execution time ({execution_time:.2f}s) exceeds 0.1 seconds"
    
    print(f"\nPairMatcher performance test passed in {execution_time:.2f} seconds")
    print(f"Matched pairs: {len(result.matched_pairs)}, Missing pairs: {len(result.missing_pairs)}")


def test_performance_regression(mock_settings, mock_coingecko_client, 
                               mock_market_repository, mock_pair_repository):
    """Test that performance improvements don't regress over time"""
    sorter = MarketDataSorter(
        mock_settings,
        mock_coingecko_client,
        mock_market_repository,
        mock_pair_repository
    )
    
    # Run the sort multiple times to ensure consistency
    execution_times = []
    for _ in range(3):
        start_time = time.time()
        sorter.sort_pairs_by_volume("USDT", "swap")
        end_time = time.time()
        execution_times.append(end_time - start_time)
    
    # Verify all executions are under the time limit
    for i, time_taken in enumerate(execution_times):
        assert time_taken < 0.5, f"Execution {i+1} took {time_taken:.2f}s, which exceeds 0.5s"
    
    print(f"\nPerformance regression test passed. Times: {[f'{t:.2f}s' for t in execution_times]}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])