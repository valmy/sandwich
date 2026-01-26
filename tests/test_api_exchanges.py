import pytest
from unittest.mock import Mock, patch
from sandwich.infrastructure.api.exchanges import ExchangeClient
from sandwich.infrastructure.config import Settings
from sandwich.domain.models import ExchangeId, MarketType, TradingPair
from sandwich.domain.exceptions import ExchangeError


@pytest.fixture
def settings():
    return Settings()


@pytest.mark.unit
class TestExchangeClient:
    def test_initialization_success(self, settings):
        """Test successful initialization of ExchangeClient"""
        client = ExchangeClient(settings, ExchangeId.BINANCE)
        assert client is not None
        assert client.exchange_id == ExchangeId.BINANCE

    @patch("sandwich.infrastructure.api.exchanges.getattr")
    def test_initialization_unknown_exchange(self, mock_getattr, settings):
        """Test initialization with unknown exchange raises ExchangeError"""
        # Make getattr raise AttributeError when accessing exchange
        mock_getattr.side_effect = AttributeError("Unknown exchange")
        
        # Create a dummy exchange id
        class DummyExchangeId:
            @property
            def value(self):
                return "unknown_exchange"
        
        with pytest.raises(ExchangeError):
            ExchangeClient(settings, DummyExchangeId())

    @patch("sandwich.infrastructure.api.exchanges.ccxt")
    def test_fetch_pairs_success(self, mock_ccxt, settings):
        """Test successful fetching of trading pairs"""
        # Mock exchange
        mock_exchange_instance = Mock()
        mock_exchange_instance.load_markets.return_value = {
            "BTC/USDT": {
                "base": "BTC",
                "quote": "USDT",
                "active": True,
                "swap": True,
                "spot": False,
            },
            "ETH/USDT": {
                "base": "ETH",
                "quote": "USDT",
                "active": True,
                "swap": True,
                "spot": False,
            },
            "BTC/USDC": {
                "base": "BTC",
                "quote": "USDC",
                "active": False,
                "swap": True,
                "spot": False,
            },
        }
        mock_ccxt.binance.return_value = mock_exchange_instance

        client = ExchangeClient(settings, ExchangeId.BINANCE)
        pairs = client.fetch_pairs("USDT", MarketType.SWAP)

        assert len(pairs) == 2
        assert all(isinstance(pair, TradingPair) for pair in pairs)
        assert all(pair.quote == "USDT" for pair in pairs)
        assert all(pair.market_type == MarketType.SWAP for pair in pairs)
        assert all(pair.is_active for pair in pairs)

    @patch("sandwich.infrastructure.api.exchanges.ccxt")
    def test_fetch_pairs_no_active_pairs(self, mock_ccxt, settings):
        """Test fetching pairs when there are no active pairs"""
        mock_exchange_instance = Mock()
        mock_exchange_instance.load_markets.return_value = {
            "BTC/USDT": {
                "base": "BTC",
                "quote": "USDT",
                "active": False,
                "swap": True,
                "spot": False,
            },
        }
        mock_ccxt.binance.return_value = mock_exchange_instance

        client = ExchangeClient(settings, ExchangeId.BINANCE)
        pairs = client.fetch_pairs("USDT", MarketType.SWAP)

        assert len(pairs) == 0

    @patch("sandwich.infrastructure.api.exchanges.ccxt")
    def test_fetch_pairs_exchange_error(self, mock_ccxt, settings):
        """Test exchange error when fetching pairs raises ExchangeError"""
        mock_exchange_instance = Mock()
        mock_exchange_instance.load_markets.side_effect = Exception("API Connection Error")
        mock_ccxt.binance.return_value = mock_exchange_instance

        client = ExchangeClient(settings, ExchangeId.BINANCE)
        with pytest.raises(ExchangeError):
            client.fetch_pairs("USDT", MarketType.SWAP)

    @patch("sandwich.infrastructure.api.exchanges.ccxt")
    def test_fetch_pairs_invalid_market_type(self, mock_ccxt, settings):
        """Test fetching pairs with invalid market type returns empty list"""
        mock_exchange_instance = Mock()
        mock_exchange_instance.load_markets.return_value = {
            "BTC/USDT": {
                "base": "BTC",
                "quote": "USDT",
                "active": True,
                "swap": False,
                "spot": False,
            },
        }
        mock_ccxt.binance.return_value = mock_exchange_instance

        client = ExchangeClient(settings, ExchangeId.BINANCE)
        pairs = client.fetch_pairs("USDT", MarketType.SWAP)

        assert len(pairs) == 0

    @patch("sandwich.infrastructure.api.exchanges.ccxt")
    def test_fetch_spot_pairs(self, mock_ccxt, settings):
        """Test fetching spot pairs correctly"""
        mock_exchange_instance = Mock()
        mock_exchange_instance.load_markets.return_value = {
            "BTC/USDT": {
                "base": "BTC",
                "quote": "USDT",
                "active": True,
                "swap": False,
                "spot": True,
            },
            "ETH/USDT": {
                "base": "ETH",
                "quote": "USDT",
                "active": True,
                "swap": False,
                "spot": True,
            },
        }
        mock_ccxt.binance.return_value = mock_exchange_instance

        client = ExchangeClient(settings, ExchangeId.BINANCE)
        pairs = client.fetch_pairs("USDT", MarketType.SPOT)

        assert len(pairs) == 2
        assert all(pair.market_type == MarketType.SPOT for pair in pairs)
