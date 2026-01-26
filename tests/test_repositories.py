"""Tests for repository classes (PairRepository and MarketRepository)."""

import pytest
from unittest.mock import Mock

from sandwich.repositories.pair_repository import PairRepository
from sandwich.repositories.market_repository import MarketRepository
from sandwich.domain.models import TradingPair, MarketType, ExchangeId, MarketData
from sandwich.domain.exceptions import FileOperationError


class TestPairRepository:
    """Tests for PairRepository class."""

    @pytest.fixture
    def mock_settings(self):
        """Create a mock Settings object."""
        settings = Mock()
        settings.get_pairs_filename = Mock(return_value="test_pairs.txt")
        return settings

    @pytest.fixture
    def mock_filesystem(self):
        """Create a mock FilesystemOperations object."""
        filesystem = Mock()
        filesystem.load_pairs = Mock(return_value=[])
        filesystem.save_pairs_for_tradingview = Mock()
        filesystem.save_sorted_pairs = Mock()
        return filesystem

    @pytest.fixture
    def pair_repository(self, mock_settings, mock_filesystem):
        """Create a PairRepository instance with mocked dependencies."""
        return PairRepository(mock_settings, mock_filesystem)

    def test_initialization(self, pair_repository, mock_settings, mock_filesystem):
        """Test that PairRepository initializes with correct dependencies."""
        assert pair_repository.settings == mock_settings
        assert pair_repository.filesystem == mock_filesystem

    def test_load_tradingview_pairs(self, pair_repository, mock_filesystem):
        """Test loading TradingView format pairs from file."""
        # Arrange
        expected_pairs = ["BINANCE:BTCUSDT.P", "BINANCE:ETHUSDT.P"]
        mock_filesystem.load_pairs.return_value = expected_pairs

        # Act
        pairs = pair_repository.load_tradingview_pairs(
            base_currency="usdtperp",
            market_type=MarketType.SWAP,
            is_hyperliquid=False
        )

        # Assert
        assert pairs == expected_pairs
        mock_filesystem.load_pairs.assert_called_once()

    def test_load_tradingview_pairs_hyperliquid(self, pair_repository, mock_settings, mock_filesystem):
        """Test loading Hyperliquid TradingView format pairs from file."""
        # Arrange
        expected_pairs = ["BINANCE:BTCUSDC.P", "BINANCE:ETHUSDC.P"]
        mock_filesystem.load_pairs.return_value = expected_pairs
        expected_filename = "hyperliquid_pairs.txt"
        mock_settings.get_pairs_filename.return_value = expected_filename

        # Act
        pairs = pair_repository.load_tradingview_pairs(
            base_currency="usdcperp",
            market_type=MarketType.SWAP,
            is_hyperliquid=True
        )

        # Assert
        assert pairs == expected_pairs
        mock_settings.get_pairs_filename.assert_called_once_with(
            "usdcperp", MarketType.SWAP.value, True
        )
        mock_filesystem.load_pairs.assert_called_once_with(expected_filename)

    def test_load_pair_lines(self, pair_repository, mock_filesystem):
        """Test loading raw pair lines from file."""
        # Arrange
        expected_lines = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
        mock_filesystem.load_pairs.return_value = expected_lines

        # Act
        lines = pair_repository.load_pair_lines("test_file.txt")

        # Assert
        assert lines == expected_lines
        mock_filesystem.load_pairs.assert_called_once_with("test_file.txt")

    def test_load_ccxt_pairs_tradingview_format(self, pair_repository, mock_filesystem):
        """Test loading and parsing TradingView format pairs to CCXT format."""
        # Arrange
        mock_filesystem.load_pairs.return_value = [
            "BINANCE:BTCUSDT.P",
            "BINANCE:ETHUSDT.P",
            "BINANCE:SOLUSDT.P"
        ]

        # Act
        pairs = pair_repository.load_ccxt_pairs("test_file.txt")

        # Assert
        assert len(pairs) == 3
        assert all(isinstance(p, TradingPair) for p in pairs)
        assert pairs[0].symbol == "BTC/USDT"
        assert pairs[0].base == "BTC"
        assert pairs[0].quote == "USDT"
        assert pairs[0].exchange == ExchangeId.BINANCE
        assert pairs[0].market_type == MarketType.SWAP
        assert pairs[0].is_active is True
        mock_filesystem.load_pairs.assert_called_once_with("test_file.txt")

    def test_load_ccxt_pairs_ccxt_format(self, pair_repository, mock_filesystem):
        """Test loading and parsing CCXT format pairs."""
        # Arrange
        mock_filesystem.load_pairs.return_value = [
            "BTC/USDT",
            "ETH/USDC",
            "SOL/FDUSD"
        ]

        # Act
        pairs = pair_repository.load_ccxt_pairs("test_file.txt")

        # Assert
        assert len(pairs) == 3
        assert all(isinstance(p, TradingPair) for p in pairs)
        assert pairs[0].symbol == "BTC/USDT"
        assert pairs[0].quote == "USDT"
        assert pairs[1].quote == "USDC"
        assert pairs[2].quote == "FDUSD"
        assert all(p.market_type == MarketType.SPOT for p in pairs)

    def test_load_ccxt_pairs_invalid_lines(self, pair_repository, mock_filesystem, caplog):
        """Test handling invalid lines when loading CCXT pairs."""
        # Arrange
        mock_filesystem.load_pairs.return_value = [
            "InvalidPairFormat",
            "",
            "   ",
            "BTC"
        ]

        # Act
        pairs = pair_repository.load_ccxt_pairs("test_file.txt")

        # Assert
        assert len(pairs) == 0
        assert any("Failed to parse" in record.message for record in caplog.records)

    def test_save_tradingview_pairs(self, pair_repository, mock_filesystem):
        """Test saving pairs in TradingView format."""
        # Arrange
        pairs = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

        # Act
        pair_repository.save_tradingview_pairs(
            pairs,
            exchange_id="binance",
            base_currency="usdtperp",
            market_type=MarketType.SWAP
        )

        # Assert
        mock_filesystem.save_pairs_for_tradingview.assert_called_once_with(
            pairs, "binance", "usdtperp", MarketType.SWAP, None
        )

    def test_save_tradingview_pairs_with_filename(self, pair_repository, mock_filesystem):
        """Test saving pairs in TradingView format with custom filename."""
        # Arrange
        pairs = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        custom_filename = "custom_pairs.txt"

        # Act
        pair_repository.save_tradingview_pairs(
            pairs,
            exchange_id="binance",
            base_currency="usdtperp",
            market_type=MarketType.SWAP,
            filename=custom_filename
        )

        # Assert
        mock_filesystem.save_pairs_for_tradingview.assert_called_once_with(
            pairs, "binance", "usdtperp", MarketType.SWAP, custom_filename
        )

    def test_save_sorted_pairs(self, pair_repository, mock_filesystem):
        """Test saving sorted pairs to file."""
        # Arrange
        sorted_data = "BINANCE:BTCUSDT.P\nBINANCE:ETHUSDT.P\nBINANCE:SOLUSDT.P"

        # Act
        pair_repository.save_sorted_pairs(
            sorted_data,
            base_currency="usdtperp",
            market_type="swap",
            is_hyperliquid=False
        )

        # Assert
        mock_filesystem.save_sorted_pairs.assert_called_once_with(
            sorted_data, "usdtperp", "swap", False
        )


class TestMarketRepository:
    """Tests for MarketRepository class."""

    @pytest.fixture
    def mock_settings(self):
        """Create a mock Settings object."""
        from pathlib import Path
        settings = Mock()
        settings.data_dir = Path(".")
        settings.marketcap_file = "market_data.json"
        return settings

    @pytest.fixture
    def mock_filesystem(self):
        """Create a mock FilesystemOperations object."""
        filesystem = Mock()
        filesystem.load_market_data = Mock(return_value=[])
        return filesystem

    @pytest.fixture
    def market_repository(self, mock_settings, mock_filesystem):
        """Create a MarketRepository instance with mocked dependencies."""
        return MarketRepository(mock_settings, mock_filesystem)

    def test_initialization(self, market_repository, mock_settings, mock_filesystem):
        """Test that MarketRepository initializes with correct dependencies."""
        assert market_repository.settings == mock_settings
        assert market_repository.filesystem == mock_filesystem

    def test_load_market_data(self, market_repository, mock_filesystem):
        """Test loading market data from file."""
        # Arrange
        sample_data = [
            {
                "id": "bitcoin",
                "symbol": "btc",
                "name": "Bitcoin",
                "current_price": 50000.0,
                "market_cap": 1000000000000,
                "market_cap_rank": 1,
                "total_volume": 30000000000,
                "price_change_24h": 2.5,
                "high_24h": 51000.0,
                "low_24h": 49000.0,
            },
            {
                "id": "ethereum",
                "symbol": "eth",
                "name": "Ethereum",
                "current_price": 3000.0,
                "market_cap": 360000000000,
                "market_cap_rank": 2,
                "total_volume": 15000000000,
                "price_change_24h": -1.2,
                "high_24h": 3100.0,
                "low_24h": 2950.0,
            },
        ]
        mock_filesystem.load_market_data.return_value = sample_data

        # Act
        market_data = market_repository.load_market_data()

        # Assert
        assert len(market_data) == 2
        assert all(isinstance(m, MarketData) for m in market_data)
        assert market_data[0].id == "bitcoin"
        assert market_data[0].symbol == "BTC"  # Symbol is uppercase due to validator
        assert market_data[0].current_price == 50000.0
        assert market_data[1].id == "ethereum"
        assert market_data[1].current_price == 3000.0
        mock_filesystem.load_market_data.assert_called_once()

    def test_save_market_data(self, market_repository, mock_settings):
        """Test saving market data to file."""
        # Arrange
        market_data = [
            MarketData(
                id="bitcoin",
                symbol="btc",
                name="Bitcoin",
                current_price=50000.0,
                market_cap=1000000000000,
                market_cap_rank=1,
                total_volume=30000000000,
                price_change_24h=2.5,
                high_24h=51000.0,
                low_24h=49000.0,
            ),
            MarketData(
                id="ethereum",
                symbol="eth",
                name="Ethereum",
                current_price=3000.0,
                market_cap=360000000000,
                market_cap_rank=2,
                total_volume=15000000000,
                price_change_24h=-1.2,
                high_24h=3100.0,
                low_24h=2950.0,
            ),
        ]

        # Act
        market_repository.save_market_data(market_data)

        # Assert
        # Verify the file was created and contains the correct data
        import json
        with open(mock_settings.data_dir / mock_settings.marketcap_file, "r") as f:
            saved_data = json.load(f)

        assert len(saved_data) == 2
        assert saved_data[0]["id"] == "bitcoin"
        assert saved_data[0]["current_price"] == 50000.0
        assert saved_data[1]["id"] == "ethereum"
        assert saved_data[1]["current_price"] == 3000.0

        # Clean up
        import os
        os.remove(mock_settings.data_dir / mock_settings.marketcap_file)

    def test_save_market_data_error(self, market_repository):
        """Test that saving market data raises FileOperationError on failure."""
        # Arrange
        from pathlib import Path
        market_data = [
            MarketData(
                id="bitcoin",
                symbol="btc",
                name="Bitcoin",
                current_price=50000.0,
                market_cap=1000000000000,
                market_cap_rank=1,
                total_volume=30000000000,
                price_change_24h=2.5,
                high_24h=51000.0,
                low_24h=49000.0,
            ),
        ]

        # Make the repository use a read-only directory to cause failure
        market_repository.settings.data_dir = Path("/nonexistent/directory/that/should/not/exist")

        # Act & Assert
        with pytest.raises(FileOperationError):
            market_repository.save_market_data(market_data)
