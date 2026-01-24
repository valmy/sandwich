import pytest
from unittest.mock import Mock, patch, mock_open
from sandwich.infrastructure.api.coingecko import CoinGeckoClient
from sandwich.infrastructure.config import Settings
from sandwich.domain.models import MarketData
from sandwich.domain.exceptions import APIRequestError


@pytest.fixture
def settings():
    return Settings()


@pytest.mark.unit
class TestCoinGeckoClient:
    def test_initialization(self, settings):
        """Test successful initialization of CoinGeckoClient"""
        client = CoinGeckoClient(settings)
        assert client is not None
        assert client.api_url == settings.coingecko_api_url

    @patch("sandwich.infrastructure.api.coingecko.CoinGeckoClient.make_request")
    def test_fetch_market_data_success(self, mock_make_request, settings, sample_market_data):
        """Test successful fetching of market data from CoinGecko API"""
        # Set to 1 page to avoid duplicate data
        settings.pages_to_fetch = 1
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_market_data
        mock_make_request.return_value = mock_response

        client = CoinGeckoClient(settings)
        market_data = client.fetch_market_data()

        assert len(market_data) == 3
        assert all(isinstance(item, MarketData) for item in market_data)
        assert market_data[0].id == "bitcoin"
        assert market_data[0].symbol == "BTC"
        assert market_data[0].current_price == 50000.0
        assert market_data[0].market_cap == 1000000000000

    @patch("sandwich.infrastructure.api.coingecko.CoinGeckoClient.make_request")
    def test_fetch_market_data_api_error(self, mock_make_request, settings):
        """Test API error when fetching market data raises APIRequestError"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_make_request.return_value = mock_response

        client = CoinGeckoClient(settings)
        with pytest.raises(APIRequestError):
            client.fetch_market_data()

    @patch("sandwich.infrastructure.api.coingecko.CoinGeckoClient.make_request")
    def test_fetch_market_data_invalid_json(self, mock_make_request, settings):
        """Test invalid JSON response raises APIRequestError"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_make_request.return_value = mock_response

        client = CoinGeckoClient(settings)
        with pytest.raises(APIRequestError):
            client.fetch_market_data()

    @patch("sandwich.infrastructure.api.coingecko.CoinGeckoClient.make_request")
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_fetch_market_data_save_to_file(
        self, mock_json_dump, mock_file_open, mock_make_request, settings, sample_market_data
    ):
        """Test market data is saved to file when file path is provided"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_market_data
        mock_make_request.return_value = mock_response

        file_path = "test_market_data.json"
        client = CoinGeckoClient(settings)
        client.fetch_market_data(file_path)

        mock_file_open.assert_called_once_with(file_path, "w")
        mock_json_dump.assert_called_once()

    def test_fetch_stablecoins_returns_hardcoded_list(self, settings):
        """Test fetch_stablecoins returns hardcoded list of stablecoins"""
        client = CoinGeckoClient(settings)
        stablecoins = client.fetch_stablecoins()

        assert len(stablecoins) > 0
        assert "USDT" in stablecoins
        assert "USDC" in stablecoins
        assert "DAI" in stablecoins

    @patch("sandwich.infrastructure.api.coingecko.time.time", return_value=0)
    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.stat")
    @patch("builtins.open", new_callable=mock_open, read_data='["usdt", "usdc", "dai"]')
    def test_fetch_stablecoins_from_cache(
        self, mock_file_open, mock_stat, mock_exists, mock_time, settings
    ):
        """Test fetch_stablecoins loads from cache when cache file exists and is fresh"""
        # Mock file modification time (fresh cache)
        mock_stat_result = Mock()
        mock_stat_result.st_mtime = 0  # Very old timestamp to ensure cache is fresh
        mock_stat.return_value = mock_stat_result

        client = CoinGeckoClient(settings)
        stablecoins = client.fetch_stablecoins("stablecoins.json")

        assert len(stablecoins) == 3
        assert "USDT" in stablecoins
        assert "USDC" in stablecoins
        assert "DAI" in stablecoins

    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.stat")
    @patch("builtins.open", new_callable=mock_open, read_data='["usdt", "usdc", "dai"]')
    def test_fetch_stablecoins_cache_expired(
        self, mock_file_open, mock_stat, mock_exists, settings
    ):
        """Test fetch_stablecoins uses hardcoded list when cache is expired"""
        import time
        from sandwich.infrastructure.api.coingecko import CACHE_EXPIRY_HOURS

        # Mock file modification time (expired cache)
        mock_stat_result = Mock()
        mock_stat_result.st_mtime = time.time() - (CACHE_EXPIRY_HOURS * 3600 + 3600)
        mock_stat.return_value = mock_stat_result

        client = CoinGeckoClient(settings)
        stablecoins = client.fetch_stablecoins("stablecoins.json")

        # Should return hardcoded list, not cached list (which has 3 items)
        assert len(stablecoins) > 3
        assert "USDT" in stablecoins
        assert "USDC" in stablecoins
        assert "DAI" in stablecoins

    @patch("sandwich.infrastructure.api.coingecko.CoinGeckoClient._save_stablecoins_to_file")
    @patch("pathlib.Path.exists", return_value=True)
    @patch("builtins.open", side_effect=Exception("Failed to read file"))
    def test_fetch_stablecoins_cache_read_error(self, mock_file_open, mock_exists, mock_save, settings):
        """Test fetch_stablecoins uses hardcoded list when cache file is unreadable"""
        client = CoinGeckoClient(settings)
        stablecoins = client.fetch_stablecoins("stablecoins.json")

        assert len(stablecoins) > 0
        assert "USDT" in stablecoins

    @patch("pathlib.Path.exists", return_value=False)
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_fetch_stablecoins_save_cache(
        self, mock_json_dump, mock_file_open, mock_exists, settings
    ):
        """Test fetch_stablecoins saves cache file when it doesn't exist"""
        client = CoinGeckoClient(settings)
        client.fetch_stablecoins("stablecoins.json")

        mock_file_open.assert_called_once_with("stablecoins.json", "w")
        mock_json_dump.assert_called_once()
