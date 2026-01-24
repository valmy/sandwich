import pytest
from sandwich.domain.services import PairMatcher, MarketDataSorter
from sandwich.domain.models import TradingPair, ExchangeId, MarketType
from sandwich.infrastructure.config import Settings


@pytest.fixture
def settings():
    return Settings()


@pytest.fixture
def pair_matcher(settings):
    return PairMatcher(settings)


@pytest.fixture
def market_sorter(settings):
    return MarketDataSorter(settings)


@pytest.mark.unit
class TestPairMatcher:
    def test_normalize_coin_name_k_prefix(self, pair_matcher):
        assert pair_matcher.normalize_coin_name("kPEPE") == "PEPE"
        assert pair_matcher.normalize_coin_name("kB") == "B"

    def test_normalize_coin_name_1000_prefix(self, pair_matcher):
        assert pair_matcher.normalize_coin_name("1000PEPE") == "PEPE"

    def test_normalize_coin_name_no_prefix(self, pair_matcher):
        assert pair_matcher.normalize_coin_name("BTC") == "BTC"
        assert (
            pair_matcher.normalize_coin_name("kpepe") == "kpepe"
        )  # Lowercase k doesn't match if not followed by uppercase

    def test_match_pairs_with_normalization(self, pair_matcher):
        source_pairs = [
            TradingPair(
                symbol="kPEPE/USDC",
                base="kPEPE",
                quote="USDC",
                exchange=ExchangeId.HYPERLIQUID,
                market_type=MarketType.SWAP,
                is_active=True,
            )
        ]
        target_pairs = [
            TradingPair(
                symbol="PEPE/USDT",
                base="PEPE",
                quote="USDT",
                exchange=ExchangeId.BINANCE,
                market_type=MarketType.SWAP,
                is_active=True,
            )
        ]

        result = pair_matcher.match_pairs(source_pairs, target_pairs)
        assert len(result.matched_pairs) == 1
        assert result.special_matches == 1

    def test_match_pairs_currency_equivalence(self, pair_matcher):
        source_pairs = [
            TradingPair(
                symbol="BTC/USDT",
                base="BTC",
                quote="USDT",
                exchange=ExchangeId.BINANCE,
                market_type=MarketType.SWAP,
                is_active=True,
            )
        ]
        target_pairs = [
            TradingPair(
                symbol="BTC/USDC",
                base="BTC",
                quote="USDC",
                exchange=ExchangeId.HYPERLIQUID,
                market_type=MarketType.SWAP,
                is_active=True,
            )
        ]

        result = pair_matcher.match_pairs(source_pairs, target_pairs)
        assert len(result.matched_pairs) == 1
        # BTC is normal match. But quote is different.
        # Actually PairMatcher matches by BASE.
        assert result.normal_matches == 1


@pytest.mark.unit
class TestMarketDataSorter:
    def test_remove_prefix_suffix(self, market_sorter):
        assert market_sorter.remove_prefix_suffix("BINANCE:BTCUSDT.P") == "BTCUSDT"
        assert market_sorter.remove_prefix_suffix("BTCUSDT") == "BTCUSDT"

    def test_find_symbol_in_lines(self, market_sorter):
        lines = ["BINANCE:BTCUSDT.P", "BINANCE:ETHUSDT.P"]
        item = {"symbol": "BTC"}

        line = market_sorter.find_symbol_in_lines(item, lines, "USDT", set())
        assert line == "BINANCE:BTCUSDT.P"

    def test_sort_pairs_by_volume(self, market_sorter):
        market_data = [
            {"symbol": "ETH", "total_volume": 1000},
            {"symbol": "BTC", "total_volume": 2000},
        ]
        lines = ["BINANCE:BTCUSDT.P", "BINANCE:ETHUSDT.P"]

        sorted_data, sorted_count, unsorted_count = market_sorter.sort_pairs_by_volume(
            market_data, lines, "USDT", "swap"
        )

        assert sorted_count == 2
        assert unsorted_count == 0
        assert sorted_data.startswith("BINANCE:BTCUSDT.P")  # BTC has higher volume

    def test_sort_pairs_by_volume_filters_stablecoins(self, market_sorter):
        market_data = [
            {"symbol": "ETH", "total_volume": 1000},
            {"symbol": "BTC", "total_volume": 2000},
            {"symbol": "USDC", "total_volume": 5000},
            {"symbol": "DAI", "total_volume": 3000},
        ]
        lines = [
            "BINANCE:BTCUSDT.P",
            "BINANCE:ETHUSDT.P",
            "BINANCE:USDCUSDT.P",
            "BINANCE:DAIUSDT.P",
        ]

        stablecoins = {"USDC", "DAI", "USDT"}
        sorted_data, sorted_count, unsorted_count = market_sorter.sort_pairs_by_volume(
            market_data, lines, "USDT", "swap", False, stablecoins
        )

        # USDC and DAI should be filtered out
        assert sorted_count == 2
        assert "BINANCE:USDCUSDT.P" not in sorted_data
        assert "BINANCE:DAIUSDT.P" not in sorted_data
        assert "BINANCE:BTCUSDT.P" in sorted_data
        assert "BINANCE:ETHUSDT.P" in sorted_data
