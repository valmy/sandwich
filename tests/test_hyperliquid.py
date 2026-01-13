import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from tests.fixtures.hyperliquid_fixtures import (
    get_hyperliquid_markets,
    get_hyperliquid_special_prefix_pairs,
    get_binance_file_content,
    get_binance_file_content_spot,
)


@pytest.mark.unit
class TestGetPairsHyperliquid:
    def test_usdc_swap_pairs(self):
        from sandwich.hyperliquid.pairs import get_pairs

        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = get_hyperliquid_markets()

        with patch(
            "sandwich.hyperliquid.pairs.ccxt.hyperliquid", return_value=mock_exchange
        ):
            pairs = get_pairs("USDC", "swap")

            assert len(pairs) == 9
            assert "BTC/USDC:USDC" in pairs
            assert "ETH/USDC:USDC" in pairs
            assert "KPEPE/USDC:USDC" in pairs

    def test_usdc_spot_pairs(self):
        from sandwich.hyperliquid.pairs import get_pairs

        markets = {
            "BTC/USDC": {"active": True, "quote": "USDC", "swap": False, "spot": True},
            "ETH/USDC": {"active": True, "quote": "USDC", "swap": False, "spot": True},
        }

        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = markets

        with patch(
            "sandwich.hyperliquid.pairs.ccxt.hyperliquid", return_value=mock_exchange
        ):
            pairs = get_pairs("USDC", "spot")

            assert len(pairs) == 2
            assert "BTC/USDC" in pairs

    def test_api_error_handling(self, capsys):
        from sandwich.hyperliquid.pairs import get_pairs

        mock_exchange = Mock()
        mock_exchange.load_markets.side_effect = Exception("API Error")

        with patch(
            "sandwich.hyperliquid.pairs.ccxt.hyperliquid", return_value=mock_exchange
        ):
            pairs = get_pairs("USDC", "swap")

            captured = capsys.readouterr()
            assert "Error fetching Hyperliquid data via ccxt" in captured.out
            assert pairs == []

    def test_empty_result_handling(self):
        from sandwich.hyperliquid.pairs import get_pairs

        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = {}

        with patch(
            "sandwich.hyperliquid.pairs.ccxt.hyperliquid", return_value=mock_exchange
        ):
            pairs = get_pairs("USDC", "swap")
            assert len(pairs) == 0


@pytest.mark.unit
class TestNormalizeCoinName:
    def test_k_prefix_removal(self):
        from sandwich.hyperliquid.pairs import normalize_coin_name

        result = normalize_coin_name("kPEPE")
        assert result == "PEPE"

    def test_1000_prefix_removal(self):
        from sandwich.hyperliquid.pairs import normalize_coin_name

        result = normalize_coin_name("1000PEPE")
        assert result == "PEPE"

    def test_mixed_case_handling(self):
        from sandwich.hyperliquid.pairs import normalize_coin_name

        result = normalize_coin_name("Kpepe")
        assert result == "Kpepe"

    def test_no_prefix_coin(self):
        from sandwich.hyperliquid.pairs import normalize_coin_name

        result = normalize_coin_name("BTC")
        assert result == "BTC"

    def test_single_character_with_k_prefix(self):
        from sandwich.hyperliquid.pairs import normalize_coin_name

        result = normalize_coin_name("kB")
        assert result == "B"

    def test_k_not_followed_by_uppercase(self):
        from sandwich.hyperliquid.pairs import normalize_coin_name

        result = normalize_coin_name("kpepe")
        assert result == "kpepe"


@pytest.mark.unit
class TestLoadPairsFromFile:
    def test_file_exists_and_loads_correctly(self, tmp_path):
        from sandwich.hyperliquid.pairs import load_pairs_from_file

        pairs_file = tmp_path / "usdt_swap_pairs.txt"
        with open(pairs_file, "w") as f:
            f.write(get_binance_file_content())

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            pairs = load_pairs_from_file("USDT", "swap")

            assert len(pairs) == 8
            assert "BTC/USDT" in pairs
            assert "ETH/USDT" in pairs
        finally:
            os.chdir(original_cwd)

    def test_file_doesnt_exist_warning(self, tmp_path, capsys):
        from sandwich.hyperliquid.pairs import load_pairs_from_file

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            pairs = load_pairs_from_file("USDT", "swap")

            captured = capsys.readouterr()
            assert "Warning: usdt_swap_pairs.txt not found" in captured.out
            assert pairs == []
        finally:
            os.chdir(original_cwd)

    def test_perp_suffix_removal_for_swap(self, tmp_path):
        from sandwich.hyperliquid.pairs import load_pairs_from_file

        pairs_file = tmp_path / "usdt_swap_pairs.txt"
        with open(pairs_file, "w") as f:
            f.write("BINANCE:BTCUSDTPERP\nBINANCE:ETHUSDTPERP\n")

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            pairs = load_pairs_from_file("USDT", "swap")

            assert "BTC/USDT" in pairs
            assert "ETH/USDT" in pairs
        finally:
            os.chdir(original_cwd)

    def test_no_suffix_for_spot(self, tmp_path):
        from sandwich.hyperliquid.pairs import load_pairs_from_file

        pairs_file = tmp_path / "usdt_spot_pairs.txt"
        with open(pairs_file, "w") as f:
            f.write("BINANCE:BTCUSDT\nBINANCE:ETHUSDT\n")

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            pairs = load_pairs_from_file("USDT", "spot")

            assert "BTC/USDT" in pairs
            assert "ETH/USDT" in pairs
        finally:
            os.chdir(original_cwd)

    def test_binance_prefix_removal(self, tmp_path):
        from sandwich.hyperliquid.pairs import load_pairs_from_file

        pairs_file = tmp_path / "usdt_swap_pairs.txt"
        with open(pairs_file, "w") as f:
            f.write("BINANCE:BTCUSDTPERP\n")

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            pairs = load_pairs_from_file("USDT", "swap")

            assert "BTC/USDT" in pairs
        finally:
            os.chdir(original_cwd)

    def test_ccxt_format_conversion(self, tmp_path):
        from sandwich.hyperliquid.pairs import load_pairs_from_file

        pairs_file = tmp_path / "usdt_swap_pairs.txt"
        with open(pairs_file, "w") as f:
            f.write("BINANCE:BTCUSDTPERP\nBINANCE:ETHUSDTPERP\n")

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            pairs = load_pairs_from_file("USDT", "swap")

            assert "BTC/USDT" in pairs
            assert "ETH/USDT" in pairs
        finally:
            os.chdir(original_cwd)

    def test_base_currency_location_detection(self, tmp_path):
        from sandwich.hyperliquid.pairs import load_pairs_from_file

        pairs_file = tmp_path / "usdc_swap_pairs.txt"
        with open(pairs_file, "w") as f:
            f.write("BINANCE:BTCUSDCPERP\nBINANCE:ETHUSDCPERP\n")

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            pairs = load_pairs_from_file("USDC", "swap")

            assert "BTC/USDC" in pairs
            assert "ETH/USDC" in pairs
        finally:
            os.chdir(original_cwd)


@pytest.mark.unit
class TestGetCcxtPairs:
    def test_binance_pairs_retrieval(self):
        from sandwich.hyperliquid.pairs import get_ccxt_pairs

        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = {
            "BTC/USDT:USDT": {"active": True, "quote": "USDT", "swap": True},
        }

        with patch(
            "sandwich.hyperliquid.pairs.ccxt.binance", return_value=mock_exchange
        ):
            pairs = get_ccxt_pairs("binance", "USDT", "swap")

            assert len(pairs) == 1
            assert "BTC/USDT:USDT" in pairs

    def test_bybit_pairs_retrieval(self):
        from sandwich.hyperliquid.pairs import get_ccxt_pairs

        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = {
            "BTC/USDT:USDT": {"active": True, "quote": "USDT", "swap": True},
        }

        with patch("sandwich.hyperliquid.pairs.ccxt.bybit", return_value=mock_exchange):
            pairs = get_ccxt_pairs("bybit", "USDT", "swap")

            assert len(pairs) == 1

    def test_invalid_exchange_id(self):
        from sandwich.hyperliquid.pairs import get_ccxt_pairs

        with patch(
            "sandwich.hyperliquid.pairs.ccxt",
            side_effect=AttributeError("Invalid exchange"),
        ):
            pairs = get_ccxt_pairs("invalid", "USDT", "swap")

            assert pairs == []

    def test_api_error_handling(self, capsys):
        from sandwich.hyperliquid.pairs import get_ccxt_pairs

        mock_exchange = Mock()
        mock_exchange.load_markets.side_effect = Exception("API Error")

        with patch(
            "sandwich.hyperliquid.pairs.ccxt.binance", return_value=mock_exchange
        ):
            pairs = get_ccxt_pairs("binance", "USDT", "swap")

            captured = capsys.readouterr()
            assert "Error fetching pairs from binance" in captured.out
            assert pairs == []


@pytest.mark.unit
class TestMatchWithBinancePairs:
    def test_exact_matches_found(self, tmp_path, capsys):
        from sandwich.hyperliquid.pairs import match_with_binance_pairs

        hyperliquid_pairs = ["BTC/USDC:USDC", "ETH/USDC:USDC"]

        pairs_file = tmp_path / "usdt_swap_pairs.txt"
        with open(pairs_file, "w") as f:
            f.write("BINANCE:BTCUSDTPERP\nBINANCE:ETHUSDTPERP\n")

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            matched = match_with_binance_pairs(hyperliquid_pairs, "USDT", "swap")

            captured = capsys.readouterr()
            assert len(matched) == 2
            assert "Found 2 matching pairs" in captured.out
        finally:
            os.chdir(original_cwd)

    def test_special_prefix_matches(self, tmp_path, capsys):
        from sandwich.hyperliquid.pairs import match_with_binance_pairs

        hyperliquid_pairs = ["KPEPE/USDC:USDC", "KSHIB/USDC:USDC"]

        pairs_file = tmp_path / "usdt_swap_pairs.txt"
        with open(pairs_file, "w") as f:
            f.write("BINANCE:1000PEPEUSDTPERP\nBINANCE:1000SHIBUSDTPERP\n")

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            matched = match_with_binance_pairs(hyperliquid_pairs, "USDT", "swap")

            captured = capsys.readouterr()
            assert len(matched) == 0
        finally:
            os.chdir(original_cwd)

    def test_no_matches_all_missing(self, tmp_path, capsys):
        from sandwich.hyperliquid.pairs import match_with_binance_pairs

        hyperliquid_pairs = ["DOGE/USDC:USDC", "XRP/USDC:USDC"]

        pairs_file = tmp_path / "usdt_swap_pairs.txt"
        with open(pairs_file, "w") as f:
            f.write("BINANCE:BTCUSDTPERP\nBINANCE:ETHUSDTPERP\n")

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            matched = match_with_binance_pairs(hyperliquid_pairs, "USDT", "swap")

            captured = capsys.readouterr()
            assert len(matched) == 0
            assert "Found 0 matching pairs" in captured.out
            assert "Pairs not found in Binance" in captured.out
        finally:
            os.chdir(original_cwd)

    def test_partial_matches(self, tmp_path, capsys):
        from sandwich.hyperliquid.pairs import match_with_binance_pairs

        hyperliquid_pairs = ["BTC/USDC:USDC", "DOGE/USDC:USDC", "ETH/USDC:USDC"]

        pairs_file = tmp_path / "usdt_swap_pairs.txt"
        with open(pairs_file, "w") as f:
            f.write("BINANCE:BTCUSDTPERP\nBINANCE:ETHUSDTPERP\n")

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            matched = match_with_binance_pairs(hyperliquid_pairs, "USDT", "swap")

            assert len(matched) == 2
        finally:
            os.chdir(original_cwd)

    def test_api_fallback_when_file_doesnt_exist(self, tmp_path, capsys):
        from sandwich.hyperliquid.pairs import match_with_binance_pairs

        hyperliquid_pairs = ["BTC/USDC:USDC"]

        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = {
            "BTC/USDT:USDT": {"active": True, "quote": "USDT", "swap": True},
        }

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            with patch(
                "sandwich.hyperliquid.pairs.ccxt.binance", return_value=mock_exchange
            ):
                matched = match_with_binance_pairs(hyperliquid_pairs, "USDT", "swap")

                captured = capsys.readouterr()
                assert (
                    "No pairs found in file, fetching from Binance API" in captured.out
                )
                assert len(matched) == 1
        finally:
            os.chdir(original_cwd)


@pytest.mark.unit
class TestMatchPairsBetweenExchanges:
    def test_source_hyperliquid_target_binance(self, tmp_path):
        from sandwich.hyperliquid.pairs import match_pairs_between_exchanges

        source_pairs = ["BTC/USDC:USDC", "ETH/USDC:USDC"]

        pairs_file = tmp_path / "usdt_swap_pairs.txt"
        with open(pairs_file, "w") as f:
            f.write("BINANCE:BTCUSDTPERP\nBINANCE:ETHUSDTPERP\n")

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            matched = match_pairs_between_exchanges(
                source_pairs, "binance", "USDT", "swap"
            )

            assert len(matched) == 2
        finally:
            os.chdir(original_cwd)

    def test_different_base_currencies(self, tmp_path):
        from sandwich.hyperliquid.pairs import match_pairs_between_exchanges

        source_pairs = ["BTC/USDC:USDC"]

        pairs_file = tmp_path / "usdc_swap_pairs.txt"
        with open(pairs_file, "w") as f:
            f.write("BINANCE:BTCUSDCPERP\n")

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            matched = match_pairs_between_exchanges(
                source_pairs, "binance", "USDC", "swap"
            )

            assert len(matched) == 1
        finally:
            os.chdir(original_cwd)


@pytest.mark.unit
class TestSaveHyperliquidPairsForTradingview:
    def test_correct_filename_generation(self, tmp_path, capsys):
        from sandwich.hyperliquid.pairs import save_hyperliquid_pairs_for_tradingview

        matched_pairs = ["BTC/USDT:USDT", "ETH/USDT:USDT"]

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            save_hyperliquid_pairs_for_tradingview(matched_pairs, "USDT", "swap")

            captured = capsys.readouterr()
            assert "usdt_swap_hype_pairs.txt" in captured.out
            assert (tmp_path / "usdt_swap_hype_pairs.txt").exists()
        finally:
            os.chdir(original_cwd)

    def test_perp_suffix_for_swap(self, tmp_path):
        from sandwich.hyperliquid.pairs import save_hyperliquid_pairs_for_tradingview

        matched_pairs = ["BTC/USDT:USDT", "ETH/USDT:USDT"]

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            save_hyperliquid_pairs_for_tradingview(matched_pairs, "USDT", "swap")

            with open("usdt_swap_hype_pairs.txt", "r") as f:
                lines = f.read().strip().split("\n")
                assert lines[0] == "BINANCE:BTCUSDTPERP"
                assert lines[1] == "BINANCE:ETHUSDTPERP"
        finally:
            os.chdir(original_cwd)

    def test_no_suffix_for_spot(self, tmp_path):
        from sandwich.hyperliquid.pairs import save_hyperliquid_pairs_for_tradingview

        matched_pairs = ["BTC/USDT", "ETH/USDT"]

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            save_hyperliquid_pairs_for_tradingview(matched_pairs, "USDT", "spot")

            with open("usdt_spot_hype_pairs.txt", "r") as f:
                lines = f.read().strip().split("\n")
                assert lines[0] == "BINANCE:BTCUSDT"
                assert lines[1] == "BINANCE:ETHUSDT"
        finally:
            os.chdir(original_cwd)

    def test_binance_prefix(self, tmp_path):
        from sandwich.hyperliquid.pairs import save_hyperliquid_pairs_for_tradingview

        matched_pairs = ["BTC/USDT:USDT"]

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            save_hyperliquid_pairs_for_tradingview(matched_pairs, "USDT", "swap")

            with open("usdt_swap_hype_pairs.txt", "r") as f:
                content = f.read()
                assert content.startswith("BINANCE:")
        finally:
            os.chdir(original_cwd)


@pytest.mark.unit
class TestGetAndSaveHyperliquidPairs:
    def test_complete_flow(self, tmp_path, capsys):
        from sandwich.hyperliquid.pairs import get_and_save_hyperliquid_pairs

        mock_hl_exchange = Mock()
        mock_hl_exchange.load_markets.return_value = {
            "BTC/USDC:USDC": {"active": True, "quote": "USDC", "swap": True}
        }

        pairs_file = tmp_path / "usdt_swap_pairs.txt"
        with open(pairs_file, "w") as f:
            f.write("BINANCE:BTCUSDTPERP\n")

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            with patch(
                "sandwich.hyperliquid.pairs.ccxt.hyperliquid",
                return_value=mock_hl_exchange,
            ):
                get_and_save_hyperliquid_pairs("USDC", "USDT", "swap")

                captured = capsys.readouterr()
                assert "Getting Hyperliquid pairs" in captured.out
                assert "Hyperliquid pairs: 1 found" in captured.out
                assert "Matched pairs: 1 found" in captured.out
                assert (tmp_path / "usdt_swap_hype_pairs.txt").exists()
        finally:
            os.chdir(original_cwd)


@pytest.mark.unit
class TestGetAndSaveCcxtPairs:
    def test_no_binance_filter(self, tmp_path, capsys):
        from sandwich.hyperliquid.pairs import get_and_save_ccxt_pairs

        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = {
            "BTC/USDT:USDT": {"active": True, "quote": "USDT", "swap": True},
        }

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            with patch(
                "sandwich.hyperliquid.pairs.ccxt.binance", return_value=mock_exchange
            ):
                get_and_save_ccxt_pairs(
                    "binance", "USDT", "swap", use_existing_binance=False
                )

                captured = capsys.readouterr()
                assert "binance USDT swap pairs: 1 found" in captured.out
        finally:
            os.chdir(original_cwd)

    def test_with_binance_filter(self, tmp_path, capsys):
        from sandwich.hyperliquid.pairs import get_and_save_ccxt_pairs

        mock_bybit_exchange = Mock()
        mock_bybit_exchange.load_markets.return_value = {
            "BTC/USDT:USDT": {"active": True, "quote": "USDT", "swap": True},
            "ETH/USDT:USDT": {"active": True, "quote": "USDT", "swap": True},
        }

        pairs_file = tmp_path / "usdt_swap_pairs.txt"
        with open(pairs_file, "w") as f:
            f.write("BINANCE:BTCUSDTPERP\n")

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            with patch(
                "sandwich.hyperliquid.pairs.ccxt.bybit",
                return_value=mock_bybit_exchange,
            ):
                get_and_save_ccxt_pairs(
                    "bybit", "USDT", "swap", use_existing_binance=True
                )

                captured = capsys.readouterr()
                assert (
                    "Found 1 pairs that exist in both bybit and Binance" in captured.out
                )
        finally:
            os.chdir(original_cwd)
