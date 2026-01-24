import pytest
from unittest.mock import Mock, patch
from sandwich.application.commands import (
    FetchMarketDataCommand,
    FetchPairsCommand,
    MatchPairsCommand,
    SortPairsCommand,
)
from sandwich.domain.models import ExchangeId, MarketType
from sandwich.domain.exceptions import SandwichError
from sandwich.infrastructure.config import Settings


@pytest.fixture
def mock_coin_gecko_client():
    client = Mock()
    client.fetch_market_data = Mock(return_value=[])
    client.fetch_stablecoins = Mock(return_value=[])
    return client


@pytest.fixture
def mock_exchange_client():
    client = Mock()
    client.exchange_id = ExchangeId.BINANCE
    client.fetch_pairs = Mock(return_value=[])
    return client


@pytest.fixture
def mock_pair_repository():
    repo = Mock()
    repo.save_tradingview_pairs = Mock()
    repo.load_ccxt_pairs = Mock(return_value=[])
    repo.load_pair_lines = Mock(return_value=[])
    repo.save_sorted_pairs = Mock()
    return repo


@pytest.fixture
def mock_market_repository():
    repo = Mock()
    repo.save_market_data = Mock()
    repo.load_market_data = Mock(return_value=[])
    return repo


@pytest.fixture
def mock_pair_matcher():
    matcher = Mock()
    matcher.match_pairs = Mock(return_value=Mock(matched_pairs=[]))
    return matcher


@pytest.fixture
def mock_market_sorter():
    sorter = Mock()
    sorter.sort_pairs_by_volume = Mock(return_value=([], 0, 0))
    return sorter


@pytest.fixture
def settings():
    return Settings()


@pytest.mark.unit
class TestFetchMarketDataCommand:
    def test_initialization(self, mock_coin_gecko_client, mock_market_repository, settings):
        command = FetchMarketDataCommand(
            mock_coin_gecko_client,
            mock_market_repository,
            settings,
        )
        assert command.api_client == mock_coin_gecko_client
        assert command.market_repository == mock_market_repository
        assert command.settings == settings

    def test_execute_success(self, mock_coin_gecko_client, mock_market_repository, settings):
        # Arrange
        mock_data = [{"id": "bitcoin", "symbol": "btc", "market_cap": 1000000000000}]
        mock_coin_gecko_client.fetch_market_data.return_value = mock_data

        command = FetchMarketDataCommand(
            mock_coin_gecko_client,
            mock_market_repository,
            settings,
        )

        # Act
        command.execute()

        # Assert
        mock_coin_gecko_client.fetch_market_data.assert_called_once()
        mock_market_repository.save_market_data.assert_called_once_with(mock_data)

    def test_execute_failure(self, mock_coin_gecko_client, mock_market_repository, settings):
        # Arrange
        mock_coin_gecko_client.fetch_market_data.side_effect = Exception("API error")

        command = FetchMarketDataCommand(
            mock_coin_gecko_client,
            mock_market_repository,
            settings,
        )

        # Act & Assert
        with pytest.raises(SandwichError):
            command.execute()

        mock_coin_gecko_client.fetch_market_data.assert_called_once()
        mock_market_repository.save_market_data.assert_not_called()


@pytest.mark.unit
class TestFetchPairsCommand:
    def test_initialization(self, mock_exchange_client, mock_pair_repository, settings):
        command = FetchPairsCommand(
            mock_exchange_client,
            mock_pair_repository,
            settings,
        )
        assert command.exchange_client == mock_exchange_client
        assert command.pair_repository == mock_pair_repository
        assert command.settings == settings

    def test_execute_success(self, mock_exchange_client, mock_pair_repository, settings):
        # Arrange
        mock_pairs = [
            Mock(symbol="BTC/USDT"),
            Mock(symbol="ETH/USDT"),
        ]
        mock_exchange_client.fetch_pairs.return_value = mock_pairs

        command = FetchPairsCommand(
            mock_exchange_client,
            mock_pair_repository,
            settings,
        )

        # Act
        command.execute("USDT", MarketType.SWAP)

        # Assert
        mock_exchange_client.fetch_pairs.assert_called_once_with("USDT", MarketType.SWAP)
        mock_pair_repository.save_tradingview_pairs.assert_called_once()

    def test_execute_failure(self, mock_exchange_client, mock_pair_repository, settings):
        # Arrange
        mock_exchange_client.fetch_pairs.side_effect = Exception("Exchange error")

        command = FetchPairsCommand(
            mock_exchange_client,
            mock_pair_repository,
            settings,
        )

        # Act & Assert
        with pytest.raises(SandwichError):
            command.execute("USDT", MarketType.SWAP)

        mock_exchange_client.fetch_pairs.assert_called_once_with("USDT", MarketType.SWAP)
        mock_pair_repository.save_tradingview_pairs.assert_not_called()


@pytest.mark.unit
class TestMatchPairsCommand:
    def test_initialization(self, mock_pair_matcher, mock_pair_repository, settings):
        command = MatchPairsCommand(
            mock_pair_matcher,
            mock_pair_repository,
            settings,
        )
        assert command.pair_matcher == mock_pair_matcher
        assert command.pair_repository == mock_pair_repository
        assert command.settings == settings

    def test_execute_with_match_with_config(self, mock_pair_matcher, mock_pair_repository, settings):
        # Arrange
        mock_matched_pairs = [
            Mock(base="BTC", quote="USDT", market_type=MarketType.SWAP),
            Mock(base="ETH", quote="USDT", market_type=MarketType.SWAP),
        ]
        mock_pair_matcher.match_pairs.return_value = Mock(matched_pairs=mock_matched_pairs)

        command = MatchPairsCommand(
            mock_pair_matcher,
            mock_pair_repository,
            settings,
        )

        # Act
        result = command.execute(ExchangeId.HYPERLIQUID, "USDC", MarketType.SWAP)

        # Assert
        assert len(result) == 2
        assert "BINANCE:BTCUSDT.P" in result
        assert "BINANCE:ETHUSDT.P" in result

    def test_execute_target_pairs_not_found(self, mock_pair_matcher, mock_pair_repository, settings):
        # Arrange
        mock_pair_repository.load_ccxt_pairs.return_value = []
        mock_matched_pairs = [Mock(base="BTC", quote="USDT", market_type=MarketType.SWAP)]
        mock_pair_matcher.match_pairs.return_value = Mock(matched_pairs=mock_matched_pairs)

        command = MatchPairsCommand(
            mock_pair_matcher,
            mock_pair_repository,
            settings,
        )

        # Act
        with patch('sandwich.application.commands.FetchPairsCommand') as mock_fetch_cmd:
            mock_fetch_instance = Mock()
            mock_fetch_cmd.return_value = mock_fetch_instance
            mock_pair_repository.load_ccxt_pairs.return_value = [
                Mock(base="BTC", quote="USDT", market_type=MarketType.SWAP)
            ]

            result = command.execute(ExchangeId.HYPERLIQUID, "USDC", MarketType.SWAP)

        # Assert
        assert len(result) == 1
        assert "BINANCE:BTCUSDT.P" in result

    def test_execute_failure(self, mock_pair_matcher, mock_pair_repository, settings):
        # Arrange
        mock_pair_repository.load_ccxt_pairs.side_effect = Exception("Load error")

        command = MatchPairsCommand(
            mock_pair_matcher,
            mock_pair_repository,
            settings,
        )

        # Act & Assert
        with pytest.raises(SandwichError):
            command.execute(ExchangeId.HYPERLIQUID, "USDC", MarketType.SWAP)


@pytest.mark.unit
class TestSortPairsCommand:
    def test_initialization(
        self,
        mock_market_sorter,
        mock_pair_repository,
    ):
        command = SortPairsCommand(
            mock_market_sorter,
            mock_pair_repository,
        )
        assert command.market_sorter == mock_market_sorter
        assert command.pair_repository == mock_pair_repository

    def test_execute_success(
        self,
        mock_market_sorter,
        mock_pair_repository,
    ):
        # Arrange
        mock_market_sorter.sort_pairs_by_volume.return_value = (
            ["BINANCE:BTCUSDT.P", "BINANCE:ETHUSDT.P"],
            2,
            0,
        )

        command = SortPairsCommand(
            mock_market_sorter,
            mock_pair_repository,
        )

        # Act
        command.execute("USDT", "swap", False)

        # Assert
        mock_market_sorter.sort_pairs_by_volume.assert_called_once_with(
            "USDT", "swap", False
        )
        mock_pair_repository.save_sorted_pairs.assert_called_once()

    def test_execute_failure(
        self,
        mock_market_sorter,
        mock_pair_repository,
    ):
        # Arrange
        mock_market_sorter.sort_pairs_by_volume.side_effect = Exception("Sorting error")

        command = SortPairsCommand(
            mock_market_sorter,
            mock_pair_repository,
        )

        # Act & Assert
        with pytest.raises(SandwichError):
            command.execute("USDT", "swap", False)

    def test_execute_with_hyperliquid_pairs(
        self,
        mock_market_sorter,
        mock_pair_repository,
    ):
        # Arrange
        command = SortPairsCommand(
            mock_market_sorter,
            mock_pair_repository,
        )

        # Act
        command.execute("USDC", "swap", True)

        # Assert
        mock_market_sorter.sort_pairs_by_volume.assert_called_once_with(
            "USDC", "swap", True
        )
